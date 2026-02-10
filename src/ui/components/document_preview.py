"""
Document Preview Component

Renders a preview of source documents (PDF / text).
Designed for legal review and citation verification.
"""

from __future__ import annotations

import os
from typing import Optional

import streamlit as st


# ---------------------------------------------------------------------
# Document Preview
# ---------------------------------------------------------------------

def render_document_preview(
    *,
    title: str = "📄 Document Preview",
    file_path: Optional[str] = None,
    text_content: Optional[str] = None,
    height: int = 600,
) -> None:
    """
    Render a document preview.

    Args:
        title: Section title
        file_path: Local or S3-style path to the document
        text_content: Parsed text (used when file preview isn't available)
        height: Preview height in pixels
    """

    st.subheader(title)

    if not file_path and not text_content:
        st.info("No document available for preview.")
        return

    if file_path:
        _render_file_preview(file_path, height)

    elif text_content:
        _render_text_preview(text_content, height)


# ---------------------------------------------------------------------
# Internal Helpers
# ---------------------------------------------------------------------

def _render_file_preview(file_path: str, height: int) -> None:
    """
    Render preview for a file path.
    """

    # ---- PDF Preview (Local) ----
    if file_path.lower().endswith(".pdf") and _is_local_file(file_path):
        try:
            with open(file_path, "rb") as f:
                st.pdf(f, height=height)
            return
        except Exception:
            st.warning("Unable to preview PDF file.")

    # ---- Text File Preview (Local) ----
    if _is_local_file(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            _render_text_preview(content, height)
            return
        except Exception:
            st.warning("Unable to preview local file.")

    # ---- Remote / Unsupported ----
    st.info("Preview not available for this document.")
    st.code(file_path, language="text")


def _render_text_preview(text: str, height: int) -> None:
    """
    Render parsed text preview.
    """
    st.markdown("**Extracted Text**")
    st.text_area(
        label="",
        value=text.strip(),
        height=height,
        disabled=True,
    )


def _is_local_file(path: str) -> bool:
    """
    Check if path is a local filesystem path.
    """
    return not path.startswith("s3://") and os.path.exists(path)
