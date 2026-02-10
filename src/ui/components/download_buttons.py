"""
Download Buttons Component

Reusable UI component for downloading answers, citations,
and source documents in multiple formats.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

import streamlit as st


# ---------------------------------------------------------------------
# Download Buttons
# ---------------------------------------------------------------------

def render_download_buttons(
    *,
    answer_text: Optional[str] = None,
    citations: Optional[list[Dict[str, Any]]] = None,
    raw_content: Optional[str] = None,
    filename_prefix: str = "case_output",
) -> None:
    """
    Render download buttons for available artifacts.

    Args:
        answer_text: Generated answer text
        citations: Citation metadata
        raw_content: Raw extracted or retrieved text
        filename_prefix: Prefix for downloaded filenames
    """

    if not any([answer_text, citations, raw_content]):
        st.info("No downloadable content available.")
        return

    st.markdown("### ⬇️ Downloads")

    cols = st.columns(3)
    col_idx = 0

    if answer_text:
        with cols[col_idx]:
            st.download_button(
                label="📝 Answer (TXT)",
                data=answer_text,
                file_name=f"{filename_prefix}_answer.txt",
                mime="text/plain",
            )
        col_idx += 1

    if citations:
        with cols[col_idx]:
            st.download_button(
                label="📚 Citations (JSON)",
                data=_to_pretty_json(citations),
                file_name=f"{filename_prefix}_citations.json",
                mime="application/json",
            )
        col_idx += 1

    if raw_content:
        with cols[col_idx]:
            st.download_button(
                label="📄 Source Text (TXT)",
                data=raw_content,
                file_name=f"{filename_prefix}_source.txt",
                mime="text/plain",
            )


# ---------------------------------------------------------------------
# Internal Helpers
# ---------------------------------------------------------------------

def _to_pretty_json(data: Any) -> str:
    """
    Convert data to formatted JSON string.
    """
    return json.dumps(
        data,
        indent=2,
        ensure_ascii=False,
        default=str,
    )
