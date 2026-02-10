"""
Case Research Page

Allows users to ask legal questions against ingested case data,
review retrieved answers, inspect citations, and preview source documents.
"""

from __future__ import annotations

from typing import Dict, List

import streamlit as st

from src.ui.components.citation_viewer import render_citation_viewer
from src.ui.components.document_preview import render_document_preview
from src.ui.components.download_buttons import render_download_buttons


# ---------------------------------------------------------------------
# Page Config
# ---------------------------------------------------------------------

st.set_page_config(
    page_title="Case Research",
    page_icon="🔍",
    layout="wide",
)


# ---------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------

st.title("🔍 Case Research")

st.markdown(
    """
    Use this page to **research a case by asking focused legal questions**.
    Answers are generated strictly from ingested documents and are
    always accompanied by citations for verification.
    """
)


# ---------------------------------------------------------------------
# Case Selection (Placeholder)
# ---------------------------------------------------------------------

st.markdown("## 📁 Select Case")

# NOTE: Replace this with real case registry later
available_cases = [
    "SC-2024-1234 · ABC Ltd vs Union of India",
    "HC-2023-998 · XYZ vs State of Maharashtra",
]

selected_case = st.selectbox(
    "Choose a registered case",
    options=available_cases,
)

if not selected_case:
    st.info("Please select a case to continue.")
    st.stop()


# ---------------------------------------------------------------------
# Question Input
# ---------------------------------------------------------------------

st.markdown("## ❓ Ask a Legal Question")

query = st.text_area(
    "Enter your question",
    placeholder=(
        "Example: What did the court hold regarding limitation "
        "under Section 14 of the Limitation Act?"
    ),
    height=100,
)

ask_button = st.button("🔍 Run Research")

if not ask_button:
    st.stop()

if not query.strip():
    st.warning("Please enter a question before proceeding.")
    st.stop()


# ---------------------------------------------------------------------
# Research Execution (Placeholder)
# ---------------------------------------------------------------------

with st.spinner("Retrieving relevant documents and generating answer…"):
    # -------------------------------------------------------------
    # PLACEHOLDER: Backend retrieval & answer generation
    # -------------------------------------------------------------
    # result = research_service.answer(
    #     case_id=selected_case,
    #     query=query,
    # )
    # -------------------------------------------------------------

    # Mocked response (for UI completeness)
    answer_text = (
        "The court held that Section 14 of the Limitation Act applies "
        "when the prior proceeding was prosecuted with due diligence "
        "and in good faith before a forum lacking jurisdiction."
    )

    citations: List[Dict[str, str]] = [
        {
            "case_id": "SC-2024-1234",
            "case_title": "ABC Ltd vs Union of India",
            "court": "Supreme Court",
            "year": "2024",
            "bench": "Justice A.B. Sharma",
            "document_type": "Judgment",
            "source": "Supreme Court Website",
            "excerpt": (
                "Section 14 shall apply where the prior proceeding "
                "was prosecuted with due diligence and in good faith…"
            ),
            "storage_path": "data/raw/SC-2024-1234/judgment.pdf",
        }
    ]

    retrieved_text = citations[0]["excerpt"]


# ---------------------------------------------------------------------
# Answer Section
# ---------------------------------------------------------------------

st.markdown("## 📝 Answer")

st.success("Answer generated from available case documents.")
st.markdown(answer_text)


# ---------------------------------------------------------------------
# Citations
# ---------------------------------------------------------------------

st.markdown("## 📚 Citations")

render_citation_viewer(
    citations=citations,
    expanded=False,
)


# ---------------------------------------------------------------------
# Document Preview
# ---------------------------------------------------------------------

st.markdown("## 📄 Source Preview")

render_document_preview(
    file_path=citations[0].get("storage_path"),
    text_content=citations[0].get("excerpt"),
)


# ---------------------------------------------------------------------
# Downloads
# ---------------------------------------------------------------------

render_download_buttons(
    answer_text=answer_text,
    citations=citations,
    raw_content=retrieved_text,
    filename_prefix=selected_case.split("·")[0].strip(),
)


# ---------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------

st.divider()
st.caption(
    "Always verify cited passages in the original document "
    "before relying on an answer."
)
