"""Application configuration via Pydantic Settings.

Settings are loaded from environment variables and an optional `.env` file.
Every field has a default so the app can start without any configuration.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed application settings.

    Values resolve in this order: environment variable -> `.env` file -> default.
    Field names are case-insensitive (e.g. `APP_NAME` maps to `app_name`).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---- Application ----
    app_name: str = "AI-Powered Incident RCA Assistant"
    api_prefix: str = "/api"
    debug: bool = False
    log_level: str = "INFO"

    # Browser origins allowed to call the API directly (when not using the
    # frontend dev proxy). Defaults to the Vite dev/preview ports.
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ]

    # ---- LLM: Groq ----
    groq_api_key: str | None = None
    # Override via GROQ_MODEL. Must be a chat model your key can access
    # (e.g. openai/gpt-oss-120b, openai/gpt-oss-20b, qwen/qwen3.6-27b).
    groq_model: str = "openai/gpt-oss-120b"
    llm_temperature: float = 0.0
    # How many times to retry a Groq call on transient failures (notably HTTP
    # 429 rate limits on the free tier). The client backs off per the server's
    # Retry-After, so a burst of requests rides out the per-minute window
    # instead of hard-failing.
    groq_max_retries: int = 6

    # ---- Embeddings (reserved for a later RAG stage; not used yet) ----
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # ---- Auth (JWT) ----
    # Secret used to sign JWTs. MUST be overridden in production via JWT_SECRET.
    # (>=32 bytes to satisfy HS256 key-length guidance even in dev.)
    jwt_secret: str = "dev-insecure-change-me-set-JWT_SECRET-in-prod"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 720  # 12 hours


@lru_cache
def get_settings() -> Settings:
    """Return a cached, singleton `Settings` instance."""
    return Settings()


# Convenience singleton for direct imports: `from app.core.config import settings`.
settings: Settings = get_settings()
