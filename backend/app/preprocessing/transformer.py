"""Build the retrieval representation (``search_text``) for each incident.

``search_text`` is a single field that concatenates the incident description,
root cause, and resolution into one labeled block. It is what gets embedded in
the RAG stage; the original columns are left untouched.

Layout (exact):

    Incident:
    <description>

    Root Cause:
    <root_cause>

    Resolution:
    <resolution>
"""

from __future__ import annotations

import pandas as pd

from app.preprocessing.validator import REQUIRED_COLUMNS

SEARCH_TEXT_COLUMN = "search_text"

SEARCH_TEXT_TEMPLATE = (
    "Incident:\n{description}\n\n"
    "Root Cause:\n{root_cause}\n\n"
    "Resolution:\n{resolution}"
)


def _as_text(value: object) -> str:
    """Render a cell for inclusion in ``search_text``.

    Missing values map to an empty string so we never emit the literal
    ``"nan"`` and never invent content — the corresponding line is simply left
    blank.
    """
    if pd.isna(value):
        return ""
    return str(value)


def build_search_text(
    description: object, root_cause: object, resolution: object
) -> str:
    """Assemble the ``search_text`` block for a single incident."""
    return SEARCH_TEXT_TEMPLATE.format(
        description=_as_text(description),
        root_cause=_as_text(root_cause),
        resolution=_as_text(resolution),
    )


def add_search_text(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of ``df`` with a ``search_text`` column appended.

    Original columns are not modified. The returned frame's columns are ordered
    ``ticket_id, description, root_cause, resolution, search_text`` (any
    unexpected extra columns are preserved after these).
    """
    result = df.copy()
    result[SEARCH_TEXT_COLUMN] = [
        build_search_text(description, root_cause, resolution)
        for description, root_cause, resolution in zip(
            result["description"],
            result["root_cause"],
            result["resolution"],
        )
    ]

    ordered = [*REQUIRED_COLUMNS, SEARCH_TEXT_COLUMN]
    extras = [col for col in result.columns if col not in ordered]
    return result[ordered + extras]
