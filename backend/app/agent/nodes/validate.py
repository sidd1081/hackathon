"""validate node: deterministic post-checks on the LLM output.

No LLM. Enforces grounding by dropping any cited ticket ID that is not in the
retrieved evidence (an anti-hallucination guardrail), and records validation
findings on the state.
"""

from __future__ import annotations

from app.agent.state import RCAState
from app.core.logger import get_logger
from app.models.schemas import NOT_DOCUMENTED

logger = get_logger(__name__)


def validate_node(state: RCAState) -> dict:
    rca = state["rca"]
    evidence = state.get("evidence", [])
    valid_ids = {item.ticket_id for item in evidence}

    cited = list(rca.supporting_ticket_ids)
    removed = [ticket for ticket in cited if ticket not in valid_ids]
    issues: list[str] = []

    root_documented = bool(rca.root_cause.strip()) and rca.root_cause != NOT_DOCUMENTED

    if not root_documented:
        # No established root cause => nothing genuinely supports one.
        if cited:
            issues.append(
                "Cleared supporting citations because the root cause is not "
                "documented."
            )
        kept: list[str] = []
    else:
        # Keep only citations that actually appear in the retrieved evidence.
        kept = [ticket for ticket in cited if ticket in valid_ids]
        if removed:
            issues.append(
                f"Dropped {len(removed)} cited ticket ID(s) not present in the "
                f"evidence: {removed}"
            )
        if not kept:
            issues.append(
                "A concrete root cause was asserted without citing any evidence."
            )

    rca.supporting_ticket_ids = kept

    validation = {
        "citations_checked": True,
        "removed_citations": removed,
        "root_cause_documented": root_documented,
        "issues": issues,
    }
    logger.info("validate: %d issue(s), citations kept=%d", len(issues), len(kept))
    return {"rca": rca, "validation": validation, "status": "generated"}
