# AI-Powered Incident Root Cause Analysis & Resolution Assistant

A support-engineering tool that retrieves similar historical incidents and
generates an **evidence-grounded** root cause analysis — and never fabricates a
root cause. If the retrieved evidence doesn't document one, it returns exactly
`Not explicitly documented.`

- **Evidence-only:** every conclusion cites real historical ticket IDs.
- **No semantic leakage:** only the problem statement (project + summary +
  description) is embedded; root causes and resolutions are returned as
  retrieved evidence, never mixed into the search text.
- **Workflow status ≠ resolution:** Jira status (`Fixed`/`Resolved`/`Closed`) is
  never treated as a technical fix — only the documented `resolution_notes` are.

## Architecture

```
CSV → validate → clean → search_text (project+summary+description)
    → embeddings (MiniLM, 384-d) → FAISS (cosine) + metadata
                                                    │
new incident → analyze → retrieve (Top-10) → rerank (Top-5) → evidence check
        ┬─ sufficient   → Groq LLM → validate (citation + mechanism) → RCA
        └─ insufficient → "Not explicitly documented."
```

- **Backend** ([`backend/`](backend/)) — Python, FastAPI, `uv`. RAG with Sentence
  Transformers + FAISS + LangChain, orchestrated by a LangGraph workflow, with
  the LLM served by Groq. The deterministic steps (retrieval, reranking, the
  evidence gate, and post-generation validation) live outside the LLM.
- **Frontend** ([`frontend/`](frontend/)) — React + Vite + Tailwind CSS. A
  dashboard with an **Analyze** tab (upload dataset · ask query · RCA response ·
  retrieved evidence) and an **Evaluation** tab (benchmark metrics), clearly
  separating AI-generated conclusions from the dataset facts they derive from.

## Quick start

**Backend** (from `backend/`):

```bash
uv sync
cp .env.example .env          # then set GROQ_API_KEY (required for RCA)
uv run python -m scripts.validate_dataset   # sanity-check data/raw/incidents.csv
uv run python -m scripts.preprocess         # -> data/processed/incidents_clean.csv
uv run python -m scripts.build_index        # -> data/vectorstore/ (FAISS + metadata)
uv run uvicorn app.main:app --reload        # http://127.0.0.1:8000  (docs at /docs)
```

**Frontend** (from `frontend/`):

```bash
npm install
npm run dev                   # http://localhost:5173  (proxies /api to the backend)
```

## API

- `GET  /api/health` — liveness
- `POST /api/auth/signup` · `POST /api/auth/login` — return a JWT bearer token
- `GET  /api/auth/me` — current user (requires token)
- `POST /api/incidents/analyze` — `{ "description": "..." }` → RCA + similar incidents *(auth)*
- `POST /api/dataset/upload` — multipart CSV → re-validate, clean, embed, re-index *(auth)*
- `GET  /api/evaluation` — latest offline benchmark metrics (from `evaluation/results.json`)

Auth uses JWT bearer tokens; passwords are hashed with PBKDF2 (stdlib) in a small
SQLite store. The public API exposes the technical resolution under the field
name `resolution` (mapped internally from `resolution_notes`) for a stable
contract.

## Configuration

Backend settings (Pydantic) via `backend/.env` — see `backend/.env.example`:

- `GROQ_API_KEY` (required for RCA) — **never committed**
- `GROQ_MODEL` (default `openai/gpt-oss-120b`)
- `GROQ_MAX_RETRIES` (default `6`) — rides out free-tier 429 rate limits
- `EMBEDDING_MODEL` (default `sentence-transformers/all-MiniLM-L6-v2`)
- `JWT_SECRET` (**override in production**) — signs auth tokens

Frontend backend URL via `frontend/.env` → `VITE_API_BASE_URL` (empty uses the
Vite dev proxy).

## Dataset

3,000 historical incidents across **8 Apache projects** (Cassandra, Flink,
Hadoop, HBase, Kafka, Solr, Spark, ZooKeeper), derived from public Apache Jira
data. The raw source is kept untouched at `backend/data/raw/incidents.csv`.

Canonical schema (14 columns):

```
ticket_id, project, summary, description, components, labels, comments,
root_cause, resolution_status, resolution_notes, root_cause_source,
resolution_source, evidence_quality, search_text
```

**Key distinction:** `resolution_status` is Jira workflow state (never used as
evidence); `resolution_notes` is the actual technical fix. Only project, summary,
and description are embedded into `search_text` — root cause and resolution are
retrieved as metadata after a match, avoiding answer leakage.

## Evaluation

Run `cd backend && uv run python -m scripts.evaluate`; results are written to
`backend/evaluation/results.json` and surfaced in the frontend's **Evaluation**
tab. Latest run:

| Metric | Result |
|---|---|
| Recall@5 / MRR | 0.875 / 0.875 |
| Root-cause correctness | 0.78 |
| Evidence-support rate | 1.0 |
| Hallucination rate | 0.0 |
| Abstention-correct (out-of-domain) | 1.0 |

See [`backend/docs/evaluation.md`](backend/docs/evaluation.md) for metric
definitions.

## Docs

- [`PRESENTATION.md`](PRESENTATION.md) — problem, approach, architecture, and
  the evaluator Q&A.
- [`TEST_CASES.md`](TEST_CASES.md) — verified demo/test queries across all 8
  projects, plus abstention cases.
