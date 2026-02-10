"""
Compliance Check Page

Performs compliance and quality checks on generated answers,
arguments, or documents before external or formal use.
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
    page_title="Compliance Check",
    page_icon="✅",
    layout="wide",
)


# ---------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------

st.title("✅ Compliance Check")

st.markdown(
    """
    Use this page to **review generated content for compliance, quality,
    and citation integrity** before relying on it for internal or external use.

    This is a **review tool**, not an automatic approval system.
    """
)


# ---------------------------------------------------------------------
# Select Case & Content Type
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


st.markdown("## 📄 Select Content to Review")

content_type = st.radio(
    "What would you like to review?",
    options=[
        "Answer",
        "Argument Draft",
        "Generated Document",
    ],
    horizontal=True,
)


# ---------------------------------------------------------------------
# Content Under Review
# ---------------------------------------------------------------------

st.markdown("## 🧾 Content Under Review")

content_text = st.text_area(
    "Content",
    height=260,
    placeholder=(
        "Paste or load the content you want to review for compliance."
    ),
)

if not content_text.strip():
    st.info("Provide content to run compliance checks.")
    st.stop()


# ---------------------------------------------------------------------
# Supporting Citations (Placeholder)
# ---------------------------------------------------------------------

st.markdown("## 📚 Referenced Citations")

# NOTE: Replace with actual citations linked to the content
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
# Run Compliance Checks
# ---------------------------------------------------------------------

st.markdown("## 🔍 Compliance Review")

run_check = st.button("Run Compliance Check")

if not run_check:
    st.stop()


with st.spinner("Running compliance checks…"):
    # -------------------------------------------------------------
    # PLACEHOLDER: Backend compliance engine
    # -------------------------------------------------------------
    # result = compliance_engine.check(
    #     content=content_text,
    #     citations=citations,
    #     content_type=content_type,
    # )
    # -------------------------------------------------------------

    # Mocked results for UI completeness
    compliance_results = {
        "citation_coverage": "Partial",
        "unsupported_claims": True,
        "tone_risk": "Low",
        "hallucination_risk": "Medium",
        "notes": [
            "Some assertions are not directly supported by citations.",
            "Citations are relevant but not referenced inline.",
        ],
    }


# ---------------------------------------------------------------------
# Compliance Results
# ---------------------------------------------------------------------

st.markdown("## 🧠 Compliance Results")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Citation Coverage",
        compliance_results["citation_coverage"],
    )
    st.metric(
        "Tone Risk",
        compliance_results["tone_risk"],
    )

with col2:
    st.metric(
        "Unsupported Claims",
        "Yes" if compliance_results["unsupported_claims"] else "No",
    )
    st.metric(
        "Hallucination Risk",
        compliance_results["hallucination_risk"],
    )


# ---------------------------------------------------------------------
# Review Notes
# ---------------------------------------------------------------------

st.markdown("## 📝 Reviewer Notes")

for note in compliance_results["notes"]:
    st.warning(note)


# ---------------------------------------------------------------------
# Export Compliance Report
# ---------------------------------------------------------------------

st.markdown("## ⬇️ Export Review")

report_text = f"""
COMPLIANCE REVIEW REPORT

Case: {selected_case}
Content Type: {content_type}

CITATION COVERAGE: {compliance_results['citation_coverage']}
UNSUPPORTED CLAIMS: {'Yes' if compliance_results['unsupported_claims'] else 'No'}
TONE RISK: {compliance_results['tone_risk']}
HALLUCINATION RISK: {compliance_results['hallucination_risk']}

REVIEWER NOTES:
- {chr(10).join(compliance_results['notes'])}
""".strip()

render_download_buttons(
    answer_text=report_text,
    citations=citations,
    filename_prefix=f"{case_id}_compliance_review",
)


# ---------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------

st.divider()
st.caption(
    "Compliance checks assist reviewers but do not replace "
    "professional judgment or legal responsibility."
)
