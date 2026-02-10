"""
Argument Builder Page

Helps users construct structured legal arguments
based on retrieved answers and verified citations.
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
    page_title="Argument Builder",
    page_icon="🧠",
    layout="wide",
)


# ---------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------

st.title("🧠 Argument Builder")

st.markdown(
    """
    Use this page to **build a structured legal argument** based on
    research findings and verified citations.

    This tool follows a clear **Issue → Rule → Analysis → Conclusion (IRAC)**
    style to keep arguments precise and reviewable.
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


# ---------------------------------------------------------------------
# Issue
# ---------------------------------------------------------------------

st.markdown("## 1️⃣ Issue")

issue = st.text_area(
    "State the legal issue clearly",
    placeholder=(
        "Example: Whether the time spent before an incorrect forum "
        "can be excluded under Section 14 of the Limitation Act."
    ),
    height=120,
)


# ---------------------------------------------------------------------
# Rule
# ---------------------------------------------------------------------

st.markdown("## 2️⃣ Rule")

rule = st.text_area(
    "State the applicable legal rule or principle",
    placeholder=(
        "Example: Section 14 of the Limitation Act permits exclusion "
        "of time spent in proceedings prosecuted with due diligence "
        "and good faith before a court lacking jurisdiction."
    ),
    height=140,
)


# ---------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------

st.markdown("## 3️⃣ Analysis")

analysis = st.text_area(
    "Apply the rule to the facts",
    placeholder=(
        "Explain how the rule applies to the facts of the case, "
        "referring to relevant precedents and reasoning."
    ),
    height=200,
)


# ---------------------------------------------------------------------
# Conclusion
# ---------------------------------------------------------------------

st.markdown("## 4️⃣ Conclusion")

conclusion = st.text_area(
    "State the conclusion",
    placeholder=(
        "Example: Therefore, the petitioner is entitled to exclusion "
        "of the period spent before the incorrect forum."
    ),
    height=120,
)


# ---------------------------------------------------------------------
# Supporting Citations (Placeholder)
# ---------------------------------------------------------------------

st.markdown("## 📚 Supporting Citations")

# NOTE: Replace with citations selected from Case Research later
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
# Review Argument
# ---------------------------------------------------------------------

st.markdown("## 🧾 Review Draft Argument")

argument_text = f"""
ISSUE:
{issue.strip()}

RULE:
{rule.strip()}

ANALYSIS:
{analysis.strip()}

CONCLUSION:
{conclusion.strip()}
""".strip()

if argument_text.replace("\n", "").strip():
    st.code(argument_text, language="text")
else:
    st.info("Start filling the sections above to preview the argument.")


# ---------------------------------------------------------------------
# Save / Export
# ---------------------------------------------------------------------

st.markdown("## ⬇️ Export Argument")

render_download_buttons(
    answer_text=argument_text,
    citations=citations,
    filename_prefix=selected_case.split("·")[0].strip() + "_argument",
)


# ---------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------

st.divider()
st.caption(
    "Arguments generated here are drafts meant for review and refinement. "
    "Always verify citations and tailor reasoning to the specific facts."
)
