"""Build the FAISS index from the processed incidents CSV.

Workflow:
    load processed CSV -> read search_text -> generate embeddings ->
    build FAISS -> store metadata -> save index + metadata to disk.

Usage (from the backend/ directory):

    uv run python -m scripts.build_index
    uv run python -m scripts.build_index path/to/incidents_clean.csv

Requires the processed CSV (run `uv run python -m scripts.preprocess` first).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from app.preprocessing.transformer import SEARCH_TEXT_COLUMN
from app.rag.embeddings import embed_texts
from app.rag.vector_store import (
    DEFAULT_INDEX_PATH,
    DEFAULT_METADATA_PATH,
    METADATA_FIELDS,
    VectorStore,
)

# backend/scripts/build_index.py -> parents[1] == backend/
_BACKEND_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROCESSED_PATH: Path = (
    _BACKEND_ROOT / "data" / "processed" / "incidents_clean.csv"
)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    processed_path = Path(args[0]) if args else DEFAULT_PROCESSED_PATH

    # 1. Load the processed CSV.
    if not processed_path.is_file():
        print(f"Processed CSV not found: {processed_path}")
        print("Run `uv run python -m scripts.preprocess` first.")
        return 1
    df = pd.read_csv(processed_path, dtype=str, keep_default_na=True)

    missing = [c for c in (*METADATA_FIELDS, SEARCH_TEXT_COLUMN) if c not in df.columns]
    if missing:
        print(f"Processed CSV is missing column(s): {', '.join(missing)}")
        return 1
    if df.empty:
        print("Processed CSV has 0 rows; nothing to index.")
        return 1

    # 2. Read search_text (the text that gets embedded).
    texts = df[SEARCH_TEXT_COLUMN].fillna("").astype(str).tolist()

    # 3. Build the metadata records (one per vector, aligned by row order).
    metadata = (
        df[list(METADATA_FIELDS)].fillna("").astype(str).to_dict(orient="records")
    )

    # 4. Generate embeddings (single batched call).
    print(f"Embedding {len(texts)} incidents from {processed_path} ...")
    embeddings = embed_texts(texts)

    # 5. Build FAISS + attach metadata, then 6. save.
    store = VectorStore.build(embeddings, metadata)
    store.save(DEFAULT_INDEX_PATH, DEFAULT_METADATA_PATH)

    # Verification output.
    print("\nFAISS index built and saved.")
    print(f"  number of vectors:   {store.size}")
    print(f"  embedding dimension: {store.dimension}")
    print(
        f"  index file:          {DEFAULT_INDEX_PATH} "
        f"({'exists' if DEFAULT_INDEX_PATH.is_file() else 'MISSING'}, "
        f"{DEFAULT_INDEX_PATH.stat().st_size} bytes)"
    )
    print(
        f"  metadata file:       {DEFAULT_METADATA_PATH} "
        f"({'exists' if DEFAULT_METADATA_PATH.is_file() else 'MISSING'}, "
        f"{DEFAULT_METADATA_PATH.stat().st_size} bytes)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
