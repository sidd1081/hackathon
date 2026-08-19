# AI-Powered Incident Root Cause Analysis & Resolution Assistant

A support-engineering tool that retrieves similar historical incidents and
generates an **evidence-grounded** root cause analysis — and never fabricates a
root cause. If the evidence doesn't document one, it returns exactly
`Not explicitly documented.`

## Architecture

```
CSV → validate → clean → search_text → embeddings (MiniLM) → FAISS
                                                                │
new incident → retrieval → rerank → evidence check ┬─ sufficient → Groq LLM → validate → RCA
                                                    └─ insufficient → "Not explicitly documented."
```

- **Backend** ([`backend/`](backend/)) — Python, FastAPI, `uv`. RAG with Sentence
  Transformers + FAISS + LangChain, orchestrated by a LangGraph workflow, with
  the LLM served by Groq. Deterministic steps (retrieval, reranking, evidence
  gate, validation) live outside the LLM.
- **Frontend** ([`frontend/`](frontend/)) — React + Vite + Tailwind CSS. An
  enterprise dashboard that clearly separates AI-generated conclusions from the
  historical dataset facts they're derived from.

## Quick start

**Backend** (from `backend/`):

```bash
uv sync
cp .env.example .env          # then set GROQ_API_KEY
uv run python -m scripts.preprocess     # build data/processed/incidents_clean.csv
uv run python -m scripts.build_index    # build the FAISS index
uv run uvicorn app.main:app --reload    # http://127.0.0.1:8000  (docs at /docs)
```

**Frontend** (from `frontend/`):

```bash
npm install
npm run dev                   # http://localhost:5173  (proxies /api to the backend)
```

## API

- `GET  /api/health` — liveness
- `POST /api/incidents/analyze` — `{ "description": "..." }` → RCA + similar incidents
- `POST /api/dataset/upload` — multipart CSV → re-validate, clean, embed, re-index

## Configuration

Backend settings (Pydantic) via `backend/.env` — see `backend/.env.example`:

- `GROQ_API_KEY` (required for RCA) — **never committed**
- `GROQ_MODEL` (default `openai/gpt-oss-120b`)
- `EMBEDDING_MODEL` (default `sentence-transformers/all-MiniLM-L6-v2`)

Frontend backend URL via `frontend/.env` → `VITE_API_BASE_URL` (empty uses the
Vite dev proxy).

## Dataset

A 300-record curated subset of the Apache Jira (Kafka) issue dataset
(columns: `ticket_id, description, root_cause, resolution`), derived from the
public [Zenodo dataset](https://zenodo.org/records/7740379). The raw source is
kept untouched at `backend/data/raw/incidents.csv`.

## Evaluation

See [`backend/docs/evaluation.md`](backend/docs/evaluation.md); machine-readable
results in `backend/evaluation/results.json`. Metrics cover retrieval
(Recall@5 / Precision@5 / MRR), RCA quality (correctness, evidence support,
hallucination rate), and latency.
