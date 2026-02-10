"""
Document Generator Page

Generates structured legal documents (notes, memos, briefs)
from researched arguments and citations.
"""

from __future__ import annotations

from typing import Dict, List

import streamlit as st

from src.ui.components.citation_viewer import render_citation_viewer
from src.ui.components.download_buttons import render_download_buttons


# ---------------------------------------------------------------------
# Page Config
# ---------------------------------------------------------------------

st.set_page_config(
    page_title="Document Generator",
    page_icon="🧾",
    layout="wide",
)


# ---------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------

st.title("🧾 Document Generator")

st.markdown(
    """
    Use this page to **generate structured legal documents**
    such as internal notes, research memos, or draft briefs.

    All generated content is **review-first** and fully editable.
    """
)


# ---------------------------------------------------------------------
# Case Selection (Placeholder)
# ---------------------------------------------------------------------

st.markdown("## 📁 Select Case")

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

case_id = selected_case.split("·")[0].strip()


# ---------------------------------------------------------------------
# Document Type
# ---------------------------------------------------------------------

st.markdown("## 📄 Document Type")

doc_type = st.selectbox(
    "Select document type",
    options=[
        "Research Note",
        "Legal Memorandum",
        "Draft Argument",
        "Case Summary",
    ],
)


# ---------------------------------------------------------------------
# Document Inputs
# ---------------------------------------------------------------------

st.markdown("## ✍️ Document Content")

title = st.text_input(
    "Document Title",
    placeholder="Example: Note on Applicability of Section 14 – Limitation Act",
)

introduction = st.text_area(
    "Introduction / Background",
    height=120,
    placeholder=(
        "Brief background of the case and the purpose of this document."
    ),
)

body = st.text_area(
    "Main Content",
    height=260,
    placeholder=(
        "Present the legal analysis, arguments, and reasoning here. "
        "Refer to citations where relevant."
    ),
)

conclusion = st.text_area(
    "Conclusion / Next Steps",
    height=120,
    placeholder=(
        "Summarize findings and suggest next steps or implications."
    ),
)


# ---------------------------------------------------------------------
# Supporting Citations (Placeholder)
# ---------------------------------------------------------------------

st.markdown("## 📚 Supporting Citations")

# NOTE: Replace with citations selected from research / argument builder
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
    }
]

render_citation_viewer(
    citations=citations,
    expanded=False,
)


# ---------------------------------------------------------------------
# Generated Document Preview
# ---------------------------------------------------------------------

st.markdown("## 🧾 Document Preview")

document_text = f"""
{title}

{doc_type.upper()}
Case: {selected_case}

INTRODUCTION
{introduction.strip()}

MAIN CONTENT
{body.strip()}

CONCLUSION
{conclusion.strip()}
""".strip()

if document_text.replace("\n", "").strip():
    st.code(document_text, language="text")
else:
    st.info("Fill in the sections above to preview the document.")


# ---------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------

st.markdown("## ⬇️ Export Document")

render_download_buttons(
    answer_text=document_text,
    citations=citations,
    filename_prefix=f"{case_id}_{doc_type.lower().replace(' ', '_')}",
)


# ---------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------

st.divider()
st.caption(
    "Generated documents are drafts intended for review and refinement. "
    "Always validate reasoning and citations before external use."
)
