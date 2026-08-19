"""retrieve node: FAISS Top-``fetch_k`` (stage 1 of two-stage retrieval).

Reuses the existing retriever; no business logic is duplicated here.
"""

from __future__ import annotations

from app.agent.state import RCAState
from app.core.logger import get_logger
from app.rag.retriever import retrieve_similar_incidents

logger = get_logger(__name__)


def retrieve_node(state: RCAState) -> dict:
    incident = state["normalized_incident"]
    fetch_k = state.get("fetch_k", 10)
    candidates = retrieve_similar_incidents(incident, top_k=fetch_k)
    logger.info("retrieve: %d FAISS candidate(s)", len(candidates))
    return {"candidates": candidates}
