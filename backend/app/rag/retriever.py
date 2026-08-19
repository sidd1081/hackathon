"""Historical incident retrieval layer.

Given a newly reported incident (free text), embed it and search the FAISS
vector store for the most similar historical incidents:

    new incident -> embedding -> FAISS search -> Top K

Similarity is the cosine score returned by FAISS (embeddings are normalized, so
inner product == cosine). No LLM is involved in scoring, and the historical
``root_cause`` / ``resolution`` values are returned verbatim — never modified,
never regenerated.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from threading import Lock

from app.core.logger import get_logger
from app.rag.embeddings import embed_text
from app.rag.vector_store import VectorStore

logger = get_logger(__name__)

_store: VectorStore | None = None
_store_lock = Lock()


class RetrievalError(RuntimeError):
    """Raised when retrieval cannot be performed (e.g. missing vector store)."""


@dataclass
class RetrievedIncident:
    """A historical incident returned by retrieval, with its similarity score."""

    rank: int
    ticket_id: str
    description: str
    root_cause: str
    resolution: str
    similarity: float

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def set_vector_store(store: VectorStore) -> None:
    """Replace the cached vector store (e.g. after rebuilding the index).

    Ensures subsequent retrievals use the freshly built index without a
    process restart.
    """
    global _store
    with _store_lock:
        _store = store


def get_vector_store() -> VectorStore:
    """Load the FAISS vector store once (thread-safe) and reuse it."""
    global _store
    if _store is None:
        with _store_lock:
            if _store is None:
                try:
                    _store = VectorStore.load()
                except FileNotFoundError as exc:
                    raise RetrievalError(
                        "Vector store not found. Build it first with "
                        "`uv run python -m scripts.build_index`."
                    ) from exc
    return _store


def retrieve_similar_incidents(
    query: str, top_k: int = 5
) -> list[RetrievedIncident]:
    """Return the ``top_k`` historical incidents most similar to ``query``.

    Args:
        query: The newly reported incident text.
        top_k: How many similar incidents to return (default 5).

    Returns:
        A list of :class:`RetrievedIncident`, ordered by descending similarity.

    Raises:
        TypeError: If ``query`` is not a string.
        ValueError: If ``query`` is empty or ``top_k`` is not positive.
        RetrievalError: If the vector store is unavailable.
    """
    if not isinstance(query, str):
        raise TypeError(f"query must be a str, got {type(query).__name__}")
    text = query.strip()
    if not text:
        raise ValueError("query must be a non-empty string.")
    if top_k <= 0:
        raise ValueError(f"top_k must be positive, got {top_k}")

    store = get_vector_store()
    query_embedding = embed_text(text)
    hits = store.search(query_embedding, top_k=top_k)

    incidents = [
        RetrievedIncident(
            rank=hit.rank,
            ticket_id=hit.ticket_id,
            description=hit.description,
            root_cause=hit.root_cause,
            resolution=hit.resolution,
            similarity=hit.score,
        )
        for hit in hits
    ]

    # FAISS already returns hits sorted by descending similarity; sort again
    # defensively so the ordering contract holds regardless of backend.
    incidents.sort(key=lambda inc: inc.similarity, reverse=True)
    for new_rank, inc in enumerate(incidents, start=1):
        inc.rank = new_rank

    logger.info("Retrieved %d incidents for query (top_k=%d)", len(incidents), top_k)
    return incidents
