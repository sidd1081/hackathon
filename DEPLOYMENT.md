# Deployment

Two supported ways to deploy:

- **A. Docker Compose** on a single host (EC2/Lightsail/local) — one command, same-origin.
- **B. Hugging Face Spaces (backend) + Vercel (frontend)** — free hosting, split
  origins (see the CORS step). Jump to
  [that section](#b-hugging-face-spaces-backend--vercel-frontend).

---

## A. Docker Compose (single host)

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

---

## B. Hugging Face Spaces (backend) + Vercel (frontend)

Free hosting. The backend runs as a Docker Space (HF free CPU: 2 vCPU / 16 GB,
enough for PyTorch); the frontend is a static Vercel deploy that calls the Space.
Because they're on different origins, the backend must allow the Vercel domain
via `CORS_ORIGINS`.

```
Vercel (frontend) ──HTTPS──▶ https://<user>-<space>.hf.space/api/*  (HF Space)
                                       └─ CORS_ORIGINS = your Vercel URL
```

### B1. Backend → Hugging Face Space

The **root `Dockerfile`** is backend-only and serves the API on port **7860**
(HF's default), with the MiniLM model and FAISS index baked in for instant boot.

1. Create a Space: <https://huggingface.co/new-space> → **SDK: Docker** → blank
   template → hardware **CPU basic (free)**.
2. Push this project to the Space's git repo (HF builds from the root
   `Dockerfile`). The Space's `README.md` must start with this metadata header —
   prepend it if pushing this repo's README:

   ```yaml
   ---
   title: AI Incident RCA Assistant API
   emoji: 🛠️
   colorFrom: indigo
   colorTo: blue
   sdk: docker
   app_port: 7860
   pinned: false
   ---
   ```

   The 35 MB dataset must be tracked with **Git LFS** on the Space (HF requires
   LFS for files > 10 MB):

   ```bash
   git clone https://huggingface.co/spaces/<user>/<space> && cd <space>
   #   copy the project files in (or add the Space as a remote of this repo)
   git lfs install
   git lfs track "*.csv"
   git add .gitattributes .
   git commit -m "Deploy backend" && git push
   ```

3. In the Space → **Settings → Variables and secrets**, add:
   - `GROQ_API_KEY` — your Groq key *(secret)*
   - `JWT_SECRET` — a long random string *(secret)*
   - `CORS_ORIGINS` — your Vercel URL (set after B2; start with `*` if unsure)
4. The Space builds (~10 min: Torch + model + index) then serves at
   `https://<user>-<space>.hf.space`. Verify `…/api/health` and `…/docs`.

> Free Spaces have **ephemeral storage**: the index is baked into the image (always
> present), but the SQLite **auth DB resets** on restart/rebuild — registered users
> are lost. Fine for a demo; use a managed DB for anything durable.

### B2. Frontend → Vercel

1. Vercel → **Add New → Project** → import the GitHub repo.
2. **Root Directory:** `frontend` (the included `frontend/vercel.json` sets the
   Vite build + SPA rewrites).
3. **Environment variable:** `VITE_API_BASE_URL = https://<user>-<space>.hf.space`
   (your Space URL, **no trailing slash**).
4. Deploy → you get `https://<app>.vercel.app`.

### B3. Wire them together (order matters)

1. Deploy the **backend Space** first → note its URL.
2. Deploy **Vercel** with `VITE_API_BASE_URL` = the Space URL.
3. Back in the Space, set `CORS_ORIGINS` = your Vercel URL → **Restart** the Space.
4. Open the Vercel URL, sign up, and analyze an incident.

If API calls fail with a CORS error in the browser console, `CORS_ORIGINS` on the
Space doesn't match the Vercel origin exactly (scheme + host, no trailing slash).
