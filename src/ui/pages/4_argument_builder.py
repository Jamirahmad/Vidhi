"""Argument Builder Page."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List

import sys
from pathlib import Path

# Ensure project root is importable when Streamlit runs from nested cwd (e.g. Windows).
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.ui.components.citation_viewer import render_citation_viewer
from src.ui.components.download_buttons import render_download_buttons
from src.ui.components.app_state import get_registered_cases, get_latest_citations


from typing import Dict, List

import streamlit as st

# Ensure project root is importable when Streamlit runs from nested cwd (e.g. Windows).
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.ui.components.citation_viewer import render_citation_viewer
from src.ui.components.download_buttons import render_download_buttons
from src.ui.components.app_state import get_registered_cases, get_latest_citations

st.set_page_config(page_title="Argument Builder", page_icon="🧠", layout="wide")

st.title("🧠 Argument Builder")
st.markdown("Build a structured legal argument in IRAC form.")

registered_cases = get_registered_cases()
if not registered_cases:
    st.info("No registered case found. Please complete Case Intake first.")
    st.stop()

case_labels = [f"{c.get('case_id','CASE')} · {c.get('case_title','Untitled Case')}" for c in registered_cases]
selected_label = st.selectbox("Case", options=case_labels)
selected_case = registered_cases[case_labels.index(selected_label)]
case_reference = selected_case.get("case_id", "CASE")

issue = st.text_area("1️⃣ Issue", height=110)
rule = st.text_area("2️⃣ Rule", height=120)
analysis = st.text_area("3️⃣ Analysis", height=200)
conclusion = st.text_area("4️⃣ Conclusion", height=120)

st.markdown("## 📚 Supporting Citations (JSON)")
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

st.markdown("## 🧾 Review Draft Argument")
if any([issue.strip(), rule.strip(), analysis.strip(), conclusion.strip()]):
    st.code(argument_text, language="text")
else:
    st.info("Provide argument sections to preview your draft.")

render_download_buttons(
    answer_text=argument_text,
    citations=citations,
    filename_prefix=(case_reference or "case").replace(" ", "_")[:40] + "_argument",
)

st.divider()
st.caption("Draft output only. Human legal review is required.")
