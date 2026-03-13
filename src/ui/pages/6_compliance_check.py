"""Compliance Check Page."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import sys
from pathlib import Path

# Ensure project root is importable when Streamlit runs from nested cwd (e.g. Windows).
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from typing import Dict, List

import streamlit as st

# Ensure project root is importable when Streamlit runs from nested cwd (e.g. Windows).
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.ui.components.citation_viewer import render_citation_viewer
from src.ui.components.download_buttons import render_download_buttons
from src.ui.components.app_state import get_registered_cases, get_latest_citations

st.set_page_config(page_title="Compliance Check", page_icon="✅", layout="wide")

st.title("✅ Compliance Check")
st.markdown("Review user-provided content for citation and consistency risks.")

registered_cases = get_registered_cases()
if not registered_cases:
    st.info("No registered case found. Please complete Case Intake first.")
    st.stop()

case_labels = [f"{c.get('case_id','CASE')} · {c.get('case_title','Untitled Case')}" for c in registered_cases]
selected_label = st.selectbox("Case", options=case_labels)
selected_case = registered_cases[case_labels.index(selected_label)]
case_reference = selected_case.get("case_id", "CASE")

content_type = st.text_input("Content Type", placeholder="e.g., Argument Draft")
content_text = st.text_area("Content Under Review", height=260)

if not content_text.strip():
    st.info("Provide content to run compliance checks.")
    st.stop()

st.markdown("## 📚 Referenced Citations (JSON)")
citations_json = st.text_area(
    "Paste citations JSON list (optional)",
    placeholder='[{"case_title":"...","court":"...","source":"..."}]',
    height=120,
)

citations: List[Dict[str, str]] = get_latest_citations()
if citations_json.strip():
    try:
        parsed = json.loads(citations_json)
        if isinstance(parsed, list):
            citations = [item for item in parsed if isinstance(item, dict)]
    except Exception:
        st.warning("Invalid citation JSON. Continuing without citations.")

render_citation_viewer(citations=citations, expanded=False)

if not st.button("Run Compliance Check"):
    st.stop()

sentences = [s for s in re.split(r"[.!?]\s+", content_text) if s.strip()]
citation_refs = re.findall(r"\[(\d+)\]", content_text)

coverage_ratio = (len(citation_refs) / max(1, len(sentences)))
if coverage_ratio >= 0.6:
    coverage = "High"
elif coverage_ratio >= 0.25:
    coverage = "Partial"
else:
    coverage = "Low"

unsupported_claims = len(citation_refs) == 0 and len(content_text.split()) > 40
hallucination_risk = "Low" if citations else "Medium"
tone_risk = "Low" if "must" not in content_text.lower() else "Medium"

notes: List[str] = []
if unsupported_claims:
    notes.append("No inline citation references detected for substantial content.")
if not citations:
    notes.append("No citation metadata was supplied for verification.")
if not notes:
    notes.append("No critical compliance red flags detected by heuristic checks.")

st.markdown("## 🧠 Compliance Results")
col1, col2 = st.columns(2)
with col1:
    st.metric("Citation Coverage", coverage)
    st.metric("Tone Risk", tone_risk)
with col2:
    st.metric("Unsupported Claims", "Yes" if unsupported_claims else "No")
    st.metric("Hallucination Risk", hallucination_risk)

st.markdown("## 📝 Reviewer Notes")
for note in notes:
    st.warning(note)

report_text = f"""
COMPLIANCE REVIEW REPORT

Case: {case_reference}
Content Type: {content_type}

CITATION COVERAGE: {coverage}
UNSUPPORTED CLAIMS: {'Yes' if unsupported_claims else 'No'}
TONE RISK: {tone_risk}
HALLUCINATION RISK: {hallucination_risk}

REVIEWER NOTES:
- {chr(10).join(notes)}
""".strip()

render_download_buttons(
    answer_text=report_text,
    citations=citations,
    filename_prefix=(case_reference or "case").replace(" ", "_")[:40] + "_compliance",
)

st.divider()
st.caption("Compliance checks are assistive only and require human legal review.")
