"""Manual test for the historical incident retrieval layer.

Usage (from the backend/ directory):

    uv run python -m scripts.test_retrieval

Runs several realistic incident queries through
``retrieve_similar_incidents`` and prints the Top 5 results for each so their
relevance can be reviewed. Requires the FAISS index (run
`uv run python -m scripts.build_index` first).
"""

from __future__ import annotations

import sys
import textwrap

from app.rag.retriever import retrieve_similar_incidents

# Historical incident text can contain non-cp1252 characters (e.g. CJK
# punctuation). Force UTF-8 output so printing never crashes on Windows.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):  # pragma: no cover - non-reconfigurable stream
    pass

# At least five realistic software incidents (first is the given example).
QUERIES: list[str] = [
    "Kafka consumers stopped processing messages after a broker restart.",
    "Producer requests fail with TimeoutException when sending records to the broker.",
    "Consumer group keeps rebalancing repeatedly and never makes progress.",
    "SSL/TLS handshake fails between the broker and client with certificate errors.",
    "Kafka Streams application throws a NullPointerException while restoring its state store.",
    "Offsets are not committed correctly, causing messages to be reprocessed after a restart.",
]

_WRAP = 100


def _short(text: str, width: int = _WRAP) -> str:
    """Collapse and shorten a field for one-line-ish display."""
    collapsed = " ".join(str(text).split())
    return textwrap.shorten(collapsed, width=width, placeholder=" ...")


def main() -> int:
    for q_index, query in enumerate(QUERIES, start=1):
        print("=" * 100)
        print(f"QUERY {q_index}: {query}")
        print("=" * 100)

        results = retrieve_similar_incidents(query, top_k=5)
        if not results:
            print("  (no results)")
            continue

        for inc in results:
            print(f"\n  #{inc.rank}  {inc.ticket_id}   similarity={inc.similarity:.4f}")
            print(f"      description: {_short(inc.description)}")
            print(f"      root_cause:  {_short(inc.root_cause)}")
            print(f"      resolution:  {_short(inc.resolution)}")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
