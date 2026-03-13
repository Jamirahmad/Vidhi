"""Document Generator Page."""

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

st.set_page_config(page_title="Document Generator", page_icon="🧾", layout="wide")

st.title("🧾 Document Generator")
st.markdown("Generate a review-ready legal draft from your own inputs.")

registered_cases = get_registered_cases()
if not registered_cases:
    st.info("No registered case found. Please complete Case Intake first.")
    st.stop()

case_labels = [f"{c.get('case_id','CASE')} · {c.get('case_title','Untitled Case')}" for c in registered_cases]
selected_label = st.selectbox("Case", options=case_labels)
selected_case = registered_cases[case_labels.index(selected_label)]
case_reference = selected_case.get("case_id", "CASE")

doc_type = st.text_input("Document Type", placeholder="e.g., Research Note")
title = st.text_input("Document Title")
introduction = st.text_area("Introduction / Background", height=120)
body = st.text_area("Main Content", height=260)
conclusion = st.text_area("Conclusion / Next Steps", height=120)

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

document_text = f"""
{title.strip()}

{(doc_type or 'DOCUMENT').upper()}
Case: {case_reference.strip()}

INTRODUCTION
{introduction.strip()}

MAIN CONTENT
{body.strip()}

CONCLUSION
{conclusion.strip()}
""".strip()

st.markdown("## 🧾 Document Preview")
if any([title.strip(), introduction.strip(), body.strip(), conclusion.strip()]):
    st.code(document_text, language="text")
else:
    st.info("Fill in document sections to preview the generated draft.")

render_download_buttons(
    answer_text=document_text,
    citations=citations,
    filename_prefix=(case_reference or "case").replace(" ", "_")[:40] + "_document",
)

st.divider()
st.caption("Generated documents are drafts. Validate facts and citations before use.")
