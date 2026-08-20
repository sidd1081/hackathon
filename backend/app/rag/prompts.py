"""Prompt construction for the RCA LLM layer.

The system prompt encodes the hard rules (evidence-only, no hallucination,
similarity-is-not-proof, the exact 'Not explicitly documented.' fallback). The
user prompt packs the new incident together with the retrieved historical
incidents (similarity, root cause, technical resolution notes) as evidence.
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
    resolution_notes: str
    similarity: float


SYSTEM_PROMPT = f"""You are an Incident Root Cause Analysis assistant for support engineers.

You are given a NEW incident and a set of RETRIEVED historical incidents that
serve as your ONLY evidence. Each piece of evidence includes a similarity score,
a historical root cause, and historical technical resolution notes.

Follow these rules strictly:
1. Do not invent root causes, resolutions, mechanisms, error names, settings,
   versions, or other technical details.
2. Do not infer causality solely from similarity or shared keywords; similarity
   is only a retrieval hint, not proof of a shared mechanism.
3. Do not turn an observed symptom into a root cause.
4. Do not combine unrelated historical mechanisms to manufacture a cause or a
   resolution. Each claim must be supported by a ticket with the same failure
   mechanism.
5. Use historical technical resolution notes only when they support the same
   documented mechanism as the proposed root cause.
6. Never treat Jira workflow status such as "Fixed", "Resolved", "Closed",
   "Done", or "Merged" as technical resolution evidence. Workflow status is
   intentionally not included in the evidence below.
7. If evidence is insufficient, conflicting, or does not document the same
   failure mechanism, set both root_cause and resolution to exactly:
   "{NOT_DOCUMENTED}". Set confidence to "low" and state the limitation.
8. Cite only supporting ticket IDs that you actually used. Keep the summary
   concise (2-4 sentences) and free of invented facts.

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
                    "Historical technical resolution notes: "
                    f"{inc.resolution_notes}",
                ]
            )

    parts.extend(
        [
            "",
            "## TASK",
            "Using ONLY the evidence above, produce the structured root-cause "
            "analysis. Do not infer causality from similarity alone. If the "
            "technical mechanism is not documented, both root_cause and "
            f'resolution must be exactly "{NOT_DOCUMENTED}".',
        ]
    )
    return "\n".join(parts)
