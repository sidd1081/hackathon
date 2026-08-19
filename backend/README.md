# Incident RCA Assistant — Backend

AI-Powered Incident Root Cause Analysis & Resolution Assistant.

Built incrementally. **Stage 1 (current): backend foundation only** — package
structure, configuration, logging, and a health endpoint. RAG, LangGraph,
LangChain, Groq, and the frontend are added in later stages.

## Requirements

- [uv](https://docs.astral.sh/uv/) (Python package/venv manager)
- Python 3.11 or 3.12 (pinned to 3.12; uv fetches it automatically)

## Setup & run

From the `backend/` directory:

```bash
# 1. Create the virtual environment and install dependencies
uv sync

# 2. Run the API (auto-reload for development)
uv run uvicorn app.main:app --reload --port 8000
```

The server listens on `http://127.0.0.1:8000`.

## Verify

```bash
curl http://127.0.0.1:8000/api/health
```

Expected response:

```json
{ "status": "ok" }
```

Interactive API docs: `http://127.0.0.1:8000/docs`

## Configuration

Settings are defined in `app/core/config.py` (Pydantic Settings) and can be
overridden via environment variables or a `.env` file. Copy the template:

```bash
cp .env.example .env    # Windows: Copy-Item .env.example .env
```

All settings have defaults, so a `.env` file is optional at this stage.

## Layout (Stage 1)

```
backend/
├── app/
│   ├── main.py            # FastAPI app factory + entrypoint
│   ├── api/routes/
│   │   └── health.py      # GET /api/health
│   └── core/
│       ├── config.py      # Pydantic Settings
│       └── logger.py      # Logging setup
├── data/                  # raw / processed / vectorstore (later stages)
├── tests/
├── pyproject.toml
├── requirements.txt
├── .env.example
└── .gitignore
```
