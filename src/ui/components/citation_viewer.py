"""
Citation Viewer Component

Displays document citations used to generate an answer.
Designed for legal / compliance review workflows.
"""

from __future__ import annotations

from typing import Dict, List, Optional

import streamlit as st


# ---------------------------------------------------------------------
# Citation Viewer
# ---------------------------------------------------------------------

def render_citation_viewer(
    citations: List[Dict[str, str]],
    *,
    title: str = "📚 Citations",
    expanded: bool = False,
) -> None:
    """
    Render a list of citations.

    Args:
        citations: List of citation dictionaries
        title: Section title
        expanded: Whether citation panels are expanded by default
    """

    if not citations:
        st.info("No citations available.")
        return

    st.subheader(title)

    for idx, citation in enumerate(citations, start=1):
        _render_single_citation(
            citation=citation,
            index=idx,
            expanded=expanded,
        )


# ---------------------------------------------------------------------
# Internal Helpers
# ---------------------------------------------------------------------

def _render_single_citation(
    *,
    citation: Dict[str, str],
    index: int,
    expanded: bool,
) -> None:
    """
    Render a single citation entry.
    """

    case_title = citation.get("case_title", "Unknown Case")
    court = citation.get("court", "Unknown Court")
    year = citation.get("year", "")
    document_type = citation.get("document_type", "Document")
    source = citation.get("source", "Unknown Source")

    label_parts = [f"[{index}] {case_title}", court]
    if year:
        label_parts.append(year)

    label = " · ".join(label_parts)

    with st.expander(label, expanded=expanded):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Case Details**")
            _kv("Case Title", case_title)
            _kv("Court", court)
            _kv("Year", year or "—")
            _kv("Document Type", document_type)

        with col2:
            st.markdown("**Source Information**")
            _kv("Source", source)
            _kv("Case ID", citation.get("case_id", "—"))
            _kv("Bench / Judge", citation.get("bench", "—"))

        excerpt = citation.get("excerpt")
        if excerpt:
            st.markdown("**Relevant Excerpt**")
            st.code(excerpt.strip(), language="text")

        storage_path = citation.get("storage_path")
        if storage_path:
            st.markdown("**Document Location**")
            st.code(storage_path, language="text")


def _kv(label: str, value: Optional[str]) -> None:
    """
    Render a key-value line safely.
    """
    st.markdown(f"**{label}:** {value if value else '—'}")
