# Deployment

The app ships as two containers wired together by Docker Compose:

- **backend** — FastAPI + Sentence-Transformers (MiniLM, baked in) + FAISS + Groq
- **web** — nginx serving the built React frontend and proxying `/api` to the backend

Everything is **same-origin** (nginx proxies `/api`), so there's no CORS setup and
the frontend needs no backend URL.

```
Browser ─▶ web (nginx :8080) ─┬─ /            → static frontend
                              └─ /api/*        → backend :8000 ─▶ Groq API
                                                 ./backend/data (volume)
                                                   ├─ vectorstore/  (FAISS)
                                                   └─ auth.db        (users)
```

## Prerequisites

- Docker + Docker Compose (v2)
- A Groq API key

## Run it (local or any VM)

```bash
# 1. Configure the backend (Groq key; set a strong JWT_SECRET for anything public)
cd backend
cp .env.example .env         # then edit .env: GROQ_API_KEY=..., JWT_SECRET=...
cd ..

# 2. Build and start
docker compose up --build          # add -d to run detached

# 3. Open the app
#    http://localhost:8080
```

On **first start** the backend builds the FAISS index from `data/raw/incidents.csv`
into the mounted volume (one-time, ~1–2 min; no network needed — the model is
baked into the image). Later starts reuse the persisted index.

Useful commands:

```bash
docker compose logs -f backend     # watch backend logs (incl. index build)
docker compose down                # stop
docker compose up --build -d       # rebuild + restart detached
```

## Configuration

Backend env comes from `backend/.env` (loaded via compose `env_file`):

| Variable | Notes |
|---|---|
| `GROQ_API_KEY` | **required** for RCA |
| `JWT_SECRET` | **set a long random value in production** (`python -c "import secrets; print(secrets.token_urlsafe(48))"`) |
| `GROQ_MODEL` | default `openai/gpt-oss-120b` |
| `GROQ_MAX_RETRIES` | default `6` (rides out free-tier 429s) |

Persisted state lives in `./backend/data/` (bind-mounted): the FAISS index
(`vectorstore/`), the processed CSV, and the auth database (`auth.db`). Back this
directory up if you care about registered users.

## Deploying to AWS

This compose setup runs unchanged on a single VM:

1. **EC2 / Lightsail:** launch a `t3.medium` (2 vCPU / 4 GB — Torch needs ~2 GB),
   install Docker + Compose, clone the repo, create `backend/.env`, then
   `docker compose up --build -d`. Put it behind an ALB or Caddy/nginx for HTTPS,
   or open port 8080 via the security group for a quick demo.
2. **HTTPS:** terminate TLS at an ALB, or add a small Caddy/Traefik container in
   front of `web` for automatic Let's Encrypt certs.

> Note: the auth database is SQLite on a local volume — fine for a demo or a
> single instance. For multiple backend replicas or zero-downtime redeploys,
> move users to a managed database (e.g. RDS/Postgres); `auth_service.py` is the
> single seam to change.

## Image notes

- **Backend image** is large (~2–3 GB) because it bundles PyTorch + the MiniLM
  weights. That's expected for local, GPU-free embeddings.
- The embedding model is baked at build time, so containers start without any
  HuggingFace download.
- Secrets are **never** baked into images — they're injected at runtime via
  compose `env_file`.
