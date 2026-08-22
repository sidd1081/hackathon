# Deploying to Google Cloud Platform (GCP)

End-to-end guide to deploy this project on GCP:

- **Backend** → **Cloud Run** (containerized FastAPI + FAISS + Groq)
- **Frontend** → **Firebase Hosting** (GCP-native, free) *or* Vercel

The backend image already works on Cloud Run unchanged — the root
[`Dockerfile`](Dockerfile) listens on Cloud Run's injected `$PORT` and bakes in
the embedding model + FAISS index for fast startup.

```
Browser ─▶ Firebase Hosting / Vercel (static frontend)
                         └─ HTTPS ─▶ Cloud Run (backend API) ─▶ Groq API
                                       env: GROQ_API_KEY, JWT_SECRET, CORS_ORIGINS
```

---

## 0. Prerequisites

- A Google account and a **GCP project with billing enabled** (Cloud Run's free
  tier still requires a billing account — see [§2](#2-enable-billing)).
- **gcloud CLI** installed: <https://cloud.google.com/sdk/docs/install>
- (Optional, for the local build path) **Docker** installed.
- Your **Groq API key** (already in `backend/.env`).

Set these shell variables once (reuse them throughout — Git Bash shown):

```bash
export PROJECT_ID="your-project-id"          # see: gcloud projects list
export REGION="us-central1"
export SERVICE="incident-rca-api"
```

---

## 1. Log in and select the project

```bash
gcloud auth login
gcloud config set project "$PROJECT_ID"
gcloud config get-value project              # confirm
```

Find your project ID if unsure:

```bash
gcloud projects list
```

Use the value in the **PROJECT_ID** column (not the name or number).

---

## 2. Enable billing

Cloud Run requires a billing account attached (you won't be charged for a small
demo; new accounts get $300 credit / 90 days).

**Console (easiest):**
1. <https://console.cloud.google.com/billing>
2. Create a billing account (add a payment method) if you don't have one.
3. Link it: **Billing → My projects → your project → Change billing**.

**Check remaining credit:** Billing → **Credits** (the CLI cannot show a credit balance).

**CLI (if you already have a billing account):**
```bash
gcloud billing accounts list                 # copy the ACCOUNT_ID; OPEN must be True
gcloud billing projects link "$PROJECT_ID" --billing-account=XXXXXX-XXXXXX-XXXXXX
```

---

## 3. Enable the required APIs

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com

# Our image build (~10 min: PyTorch + index bake) exceeds Cloud Build's 600s default.
gcloud config set builds/timeout 1800
```

---

## 4. Deploy the backend to Cloud Run

Pick **Option A** (simplest) or **Option B** (build locally).

### Option A — Deploy from source (recommended)

Run from the **repo root** (`Dockerfile` at the root is used automatically):

```bash
gcloud run deploy "$SERVICE" \
  --source . \
  --region "$REGION" \
  --memory 4Gi \
  --cpu 2 \
  --timeout 300 \
  --allow-unauthenticated \
  --set-env-vars "GROQ_API_KEY=YOUR_GROQ_KEY,JWT_SECRET=YOUR_RANDOM_SECRET,CORS_ORIGINS=*"
```

- On first run it offers to create an Artifact Registry repo
  (`cloud-run-source-deploy`) → answer **yes**.
- `--memory 4Gi` is **required** (PyTorch OOMs at the 512 MB default).
- `CORS_ORIGINS=*` is fine to start; tighten it to your frontend URL later ([§7](#7-connect-frontend--backend-cors)).
- Generate a strong `JWT_SECRET`: `python -c "import secrets; print(secrets.token_urlsafe(48))"`

> **PowerShell users:** the `\` line-continuations are Bash-only. Run the whole
> command on one line, or use backticks `` ` `` instead of `\`.

### Option B — Build locally, push to Artifact Registry, then deploy

Requires Docker. Useful if Cloud Build is slow/limited.

```bash
# 1. Create a Docker repo (one-time)
gcloud artifacts repositories create rca \
  --repository-format=docker --location="$REGION"

# 2. Authenticate Docker to Artifact Registry
gcloud auth configure-docker "${REGION}-docker.pkg.dev"

# 3. Build and push (from repo root; uses the root Dockerfile)
export IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/rca/${SERVICE}:latest"
docker build -t "$IMAGE" -f Dockerfile .
docker push "$IMAGE"

# 4. Deploy the image
gcloud run deploy "$SERVICE" \
  --image "$IMAGE" \
  --region "$REGION" \
  --memory 4Gi --cpu 2 --timeout 300 \
  --allow-unauthenticated \
  --set-env-vars "GROQ_API_KEY=YOUR_GROQ_KEY,JWT_SECRET=YOUR_RANDOM_SECRET,CORS_ORIGINS=*"
```

### Helper script

The repo also includes [`deploy-cloudrun.sh`](deploy-cloudrun.sh) (Option A in one command):

```bash
GROQ_API_KEY=xxx JWT_SECRET=xxx CORS_ORIGINS='*' ./deploy-cloudrun.sh "$PROJECT_ID" "$REGION" "$SERVICE"
```

---

## 5. Secrets: env vars vs. Secret Manager

`--set-env-vars` (above) is fine for a demo. For production, keep secrets in
**Secret Manager**:

```bash
gcloud services enable secretmanager.googleapis.com

printf '%s' "YOUR_GROQ_KEY"      | gcloud secrets create groq-api-key --data-file=-
printf '%s' "YOUR_RANDOM_SECRET" | gcloud secrets create jwt-secret   --data-file=-

# Grant Cloud Run's runtime service account read access
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')
RUNTIME_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
for S in groq-api-key jwt-secret; do
  gcloud secrets add-iam-policy-binding "$S" \
    --member="serviceAccount:${RUNTIME_SA}" \
    --role="roles/secretmanager.secretAccessor"
done

# Deploy referencing the secrets (CORS still a plain env var)
gcloud run deploy "$SERVICE" \
  --source . --region "$REGION" --memory 4Gi --cpu 2 --allow-unauthenticated \
  --set-secrets "GROQ_API_KEY=groq-api-key:latest,JWT_SECRET=jwt-secret:latest" \
  --set-env-vars "CORS_ORIGINS=*"
```

---

## 6. Verify

```bash
# Get the service URL
export API_URL=$(gcloud run services describe "$SERVICE" --region "$REGION" --format 'value(status.url)')
echo "$API_URL"

# Health
curl "$API_URL/api/health"                    # -> {"status":"ok"}

# Auth + a real RCA
curl -s -X POST "$API_URL/api/auth/signup" -H "Content-Type: application/json" \
  -d '{"name":"Demo","email":"demo@example.com","password":"secret123"}'
```

Interactive docs: `$API_URL/docs`.

> First request after idle is slow (~30–60 s) — the ~9 GB image is pulled and the
> model loads. Subsequent requests are fast.

---

## 7. Connect frontend ↔ backend (CORS)

After the frontend is deployed you'll have its URL (e.g. a Firebase or Vercel
domain). Lock the backend CORS to it:

```bash
gcloud run services update "$SERVICE" --region "$REGION" \
  --update-env-vars "CORS_ORIGINS=https://your-frontend-domain"
```

(Comma-separate multiple origins. `*` allows any origin — fine here since auth is
via bearer token, not cookies.)

---

## 8. Deploy the frontend

### Option 1 — Firebase Hosting (GCP-native, free)

```bash
cd frontend
npm install

# Build with the API URL baked in (same $API_URL from §6)
VITE_API_BASE_URL="$API_URL" npm run build

npm install -g firebase-tools
firebase login
firebase init hosting
#   - Use an existing project -> pick $PROJECT_ID
#   - Public directory: dist
#   - Configure as a single-page app (rewrite all to /index.html): Yes
#   - Set up automatic builds with GitHub: No
firebase deploy
```

Firebase prints a `https://<project>.web.app` URL. Put that in the backend's
`CORS_ORIGINS` ([§7](#7-connect-frontend--backend-cors)).

### Option 2 — Vercel

1. Import the GitHub repo in Vercel → **Root Directory: `frontend`**
   (`frontend/vercel.json` handles the Vite build + SPA rewrites).
2. Env var **`VITE_API_BASE_URL`** = your Cloud Run `$API_URL` (no trailing slash).
3. Deploy → get `https://<app>.vercel.app`, then set it in backend `CORS_ORIGINS`.

---

## 9. Updating / redeploying

```bash
# New code -> rebuild & redeploy
gcloud run deploy "$SERVICE" --source . --region "$REGION"

# Change only an env var (no rebuild)
gcloud run services update "$SERVICE" --region "$REGION" \
  --update-env-vars "CORS_ORIGINS=https://your-frontend-domain"
```

---

## 10. Logs & debugging

```bash
# Recent logs
gcloud run services logs read "$SERVICE" --region "$REGION" --limit 100

# Live tail (needs the beta component)
gcloud beta run services logs tail "$SERVICE" --region "$REGION"

# Service details (URL, revision, resources)
gcloud run services describe "$SERVICE" --region "$REGION"
```

---

## 11. Cost & free tier

- Cloud Run **scales to zero** — you pay nothing while idle.
- Free tier per month: ~2M requests, 360k GB-seconds, 180k vCPU-seconds — a demo
  usually stays within it.
- **Cost risks:** setting `--min-instances 1` (keeps a warm instance = continuous
  billing) and Artifact Registry storage for the ~9 GB image (small).
- Cloud Build minutes: first build is long; you get 120 free build-minutes/day.

---

## 12. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `FAILED_PRECONDITION: Billing account ... is not open` | Billing not enabled — do [§2](#2-enable-billing). |
| Build fails with a timeout | `gcloud config set builds/timeout 1800` (step 3). |
| Container "failed to start / listen on PORT" | Don't hardcode a port — the root Dockerfile already uses `$PORT`. Don't pass `--port` unless it matches. |
| App crashes / restarts, `Memory limit exceeded` | Raise `--memory 4Gi` (PyTorch needs ~2 GB). |
| First request very slow, then fast | Cold start pulling the 9 GB image + loading the model. Use `--min-instances 1` for demos. |
| Browser `CORS` error | `CORS_ORIGINS` must match the frontend origin exactly (scheme + host, no trailing slash). Update via [§7](#7-connect-frontend--backend-cors). |
| Registered users disappeared | Cloud Run's filesystem is ephemeral; the SQLite auth DB resets on instance recycle. Use Cloud SQL for durable users. |

---

## 13. Teardown (avoid charges)

```bash
gcloud run services delete "$SERVICE" --region "$REGION"
gcloud artifacts repositories delete rca --location="$REGION"        # if you used Option B
# Firebase: delete the Hosting site in the Firebase console if desired
```

---

## Notes on this app

- The ~9 GB image and 4 GB RAM requirement are entirely **PyTorch** (used only
  transitively by `sentence-transformers` for the MiniLM embeddings). Swapping to
  an **ONNX** embedding runtime (`fastembed`/`onnxruntime`) would cut the image to
  ~1 GB and RAM to ~400 MB, making cold starts fast and unlocking smaller/free
  tiers. See the project README for the embedding layer (`app/rag/embeddings.py`).
- The FAISS index is baked into the image at build time, so the service starts
  without rebuilding it; only the auth DB is runtime state (and ephemeral).
