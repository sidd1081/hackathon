"""FastAPI application entrypoint.

Stage 1 (foundation): wires configuration, logging, and the health route only.
RAG / LangGraph / LangChain endpoints are added in later stages.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, dataset, evaluation, health, incidents
from app.core.config import settings
from app.core.logger import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)


def create_app() -> FastAPI:
    """Application factory: build and configure the FastAPI instance."""
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        debug=settings.debug,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, prefix=settings.api_prefix)
    app.include_router(auth.router, prefix=settings.api_prefix)
    app.include_router(incidents.router, prefix=settings.api_prefix)
    app.include_router(dataset.router, prefix=settings.api_prefix)
    app.include_router(evaluation.router, prefix=settings.api_prefix)

    logger.info("%s started (api_prefix=%s)", settings.app_name, settings.api_prefix)
    return app


app = create_app()
