"""Prompt construction for the RCA LLM layer.

The system prompt encodes the hard rules (evidence-only, no hallucination,
similarity-is-not-proof, the exact 'Not explicitly documented.' fallback). The
user prompt packs the new incident together with the retrieved historical
incidents (similarity, root cause, resolution) as evidence.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from app.models.schemas import NOT_DOCUMENTED


@runtime_checkable
class EvidenceIncident(Protocol):
    """Minimal shape of a retrieved incident used as evidence."""

    ticket_id: str
    description: str
    root_cause: str
    resolution: str
    similarity: float


SYSTEM_PROMPT = f"""You are an Incident Root Cause Analysis assistant for support engineers.

You are given a NEW incident and a set of RETRIEVED historical incidents that
serve as your ONLY evidence. Each piece of evidence includes a similarity score,
a historical root cause, and a historical resolution.

Follow these rules strictly:
1. Ground every statement ONLY in the provided evidence. NEVER invent, infer, or
   add technical details (error names, configs, versions, components) that are
   not present in the evidence.
2. Similarity is only a retrieval hint. It is NOT proof that two incidents share
   the same root cause. Judge on the actual technical content, not the score.
3. Identify the single most likely TECHNICAL root cause that the evidence
   supports.
4. If the evidence does not clearly establish a technical root cause, set
   root_cause to exactly: "{NOT_DOCUMENTED}" (verbatim, nothing added).
5. Recommend a resolution grounded in the historical resolutions. If none is
   supportable, set resolution to exactly: "{NOT_DOCUMENTED}".
6. In supporting_ticket_ids, list ONLY the ticket IDs you actually relied upon.
7. Set confidence to "low", "medium", or "high" based on how well the evidence
   supports your conclusion. Weak or conflicting evidence means "low".
8. Keep the summary concise (2-4 sentences) and free of invented facts.

Do not output anything beyond the requested structured fields."""


def build_user_prompt(
    new_incident: str, incidents: Sequence[EvidenceIncident]
) -> str:
    """Assemble the evidence-packed user prompt for the RCA request."""
    parts: list[str] = [
        "## NEW INCIDENT",
        new_incident.strip(),
        "",
        "## RETRIEVED HISTORICAL INCIDENTS (evidence)",
    ]

    if not incidents:
        parts.append("(no historical incidents were retrieved)")
    else:
        for i, inc in enumerate(incidents, start=1):
            parts.extend(
                [
                    "",
                    f"### Evidence {i} — Ticket {inc.ticket_id} "
                    f"(similarity {inc.similarity:.3f})",
                    f"Description: {inc.description}",
                    f"Historical root cause: {inc.root_cause}",
                    f"Historical resolution: {inc.resolution}",
                ]
            )

    parts.extend(
        [
            "",
            "## TASK",
            "Using ONLY the evidence above, produce the structured root-cause "
            "analysis. Remember: do not fabricate, and if the technical root "
            f'cause is not established, root_cause must be exactly "{NOT_DOCUMENTED}".',
        ]
    )
    return "\n".join(parts)
