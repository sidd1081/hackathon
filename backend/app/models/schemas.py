"""Pydantic schemas for the RCA assistant.

``RCAResponse`` is the structured output the Groq LLM must return. Field
descriptions double as instructions to the model when used with LangChain's
``with_structured_output``. The ``Analyze*`` models are the public HTTP
request/response contract for the FastAPI endpoint.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints

# The exact string that must be emitted when a technical root cause cannot be
# established from the evidence.
NOT_DOCUMENTED = "Not explicitly documented."

ConfidenceLevel = Literal["low", "medium", "high"]


class RCAResponse(BaseModel):
    """Structured root-cause-analysis result grounded in retrieved evidence."""

    root_cause: str = Field(
        description=(
            "The single most likely TECHNICAL root cause, supported ONLY by the "
            "provided evidence. If the evidence does not clearly establish a "
            "technical root cause, this MUST be exactly 'Not explicitly "
            "documented.' and nothing else."
        )
    )
    resolution: str = Field(
        description=(
            "A recommended resolution grounded in the historical resolutions in "
            "the evidence. If no resolution can be supported by the evidence, "
            "this MUST be exactly 'Not explicitly documented.'"
        )
    )
    summary: str = Field(
        description=(
            "A concise (2-4 sentence) root-cause-analysis summary written for a "
            "support engineer. Do not introduce facts absent from the evidence."
        )
    )
    supporting_ticket_ids: list[str] = Field(
        default_factory=list,
        description=(
            "Ticket IDs of the historical incidents actually relied upon to reach "
            "this conclusion. Empty list if none were sufficient."
        ),
    )
    confidence: ConfidenceLevel = Field(
        description=(
            "How well the evidence supports the conclusion: 'low', 'medium', or "
            "'high'. High similarity alone is NOT high confidence."
        )
    )


# --- HTTP API contract -------------------------------------------------------

# Confidence as presented in the API response (title-cased).
ApiConfidence = Literal["Low", "Medium", "High"]


class AnalyzeRequest(BaseModel):
    """Request body for POST /api/incidents/analyze."""

    description: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=10000)
    ] = Field(description="The newly reported incident, in free text.")


class SimilarIncident(BaseModel):
    """A historical incident surfaced during retrieval, with its similarity."""

    ticket_id: str
    similarity: float = Field(description="Cosine similarity from the vector search.")
    description: str
    root_cause: str
    resolution: str


class AnalyzeResponse(BaseModel):
    """Response body for POST /api/incidents/analyze."""

    summary: str
    root_cause: str
    resolution: str
    confidence: ApiConfidence
    similar_incidents: list[SimilarIncident] = Field(
        default_factory=list,
        description="All historical incidents retrieved as evidence (reranked Top-K).",
    )
    supporting_incidents: list[SimilarIncident] = Field(
        default_factory=list,
        description="The subset of similar incidents the RCA actually relied upon.",
    )


class DatasetUploadResponse(BaseModel):
    """Response body for POST /api/dataset/upload."""

    status: str = Field(description="Overall processing status, e.g. 'success'.")
    message: str
    records: int = Field(description="Number of incident records indexed.")
    duplicates_removed: int = Field(
        default=0, description="Rows dropped as duplicates during cleaning."
    )
    embedding_dimension: int = Field(description="Dimension of the stored vectors.")
    index_status: str = Field(description="State of the FAISS index, e.g. 'ready'.")
