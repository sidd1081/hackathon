"""evidence_check node: deterministic gate that decides the routing.

No LLM. Evidence is considered sufficient only when BOTH hold:
  * at least one reranked incident is similar enough (similarity >= threshold), and
  * at least one reranked incident has a documented (non-sentinel) root cause to
    ground an answer on.

Otherwise the workflow routes to the fallback and returns the sentinel — this
keeps a cheap, explainable guardrail out of the LLM and avoids a wasted call.
"""

from __future__ import annotations

from app.agent.state import RCAState
from app.core.logger import get_logger
from app.models.schemas import NOT_DOCUMENTED

logger = get_logger(__name__)

# Minimum cosine similarity for the best evidence to be considered relevant.
MIN_SIMILARITY = 0.35


def evidence_check_node(state: RCAState) -> dict:
    evidence = state.get("evidence", [])

    if not evidence:
        reason = "No historical incidents were retrieved."
        logger.info("evidence_check: insufficient (%s)", reason)
        return {"evidence_sufficient": False, "evidence_reason": reason}

    top_similarity = max(item.similarity for item in evidence)
    is_relevant = top_similarity >= MIN_SIMILARITY
    documented = [
        item
        for item in evidence
        if item.root_cause.strip() and item.root_cause.strip() != NOT_DOCUMENTED
    ]
    has_documented = len(documented) > 0
    sufficient = is_relevant and has_documented

    if sufficient:
        reason = (
            f"Top similarity {top_similarity:.3f} >= {MIN_SIMILARITY} and "
            f"{len(documented)} incident(s) have documented root causes."
        )
    elif not is_relevant:
        reason = (
            f"Top similarity {top_similarity:.3f} < {MIN_SIMILARITY}; no "
            "sufficiently similar historical incident."
        )
    else:
        reason = "No retrieved incident has a documented root cause to ground on."

    logger.info(
        "evidence_check: %s (%s)",
        "sufficient" if sufficient else "insufficient",
        reason,
    )
    return {"evidence_sufficient": sufficient, "evidence_reason": reason}
