"""
Case Research Page

Allows users to ask legal questions against ingested case data,
review retrieved answers, inspect citations, and preview source documents.
"""

from __future__ import annotations

import sys
from pathlib import Path

import sys
from pathlib import Path

# Ensure project root is importable when Streamlit runs from nested cwd (e.g. Windows).
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from typing import Dict, List

import requests
import streamlit as st

# Ensure project root is importable when Streamlit runs from nested cwd (e.g. Windows).
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.ui.components.citation_viewer import render_citation_viewer
from src.ui.components.document_preview import render_document_preview
from src.ui.components.download_buttons import render_download_buttons
from src.ui.components.app_state import get_registered_cases, set_latest_citations

st.set_page_config(page_title="Case Research", page_icon="🔍", layout="wide")

st.title("🔍 Case Research")
st.markdown(
    """
    Use this page to **research a case by asking focused legal questions**.
    Answers are generated from API retrieval + synthesis and accompanied by citations.
    """
)

st.markdown("## 📁 Select Registered Case")
registered_cases = get_registered_cases()
if not registered_cases:
    st.info("No registered case found. Please complete Case Intake first.")
    st.stop()

case_labels = [f"{c.get('case_id','CASE')} · {c.get('case_title','Untitled Case')}" for c in registered_cases]
selected_label = st.selectbox("Case", options=case_labels)
selected_case = registered_cases[case_labels.index(selected_label)]
case_reference = selected_case.get("case_id", "CASE")
st.markdown("## ❓ Ask a Legal Question")
query = st.text_area("Enter your question", height=100)

jurisdiction = st.text_input("Jurisdiction", value=selected_case.get("jurisdiction", "India"))
case_type = st.text_input("Case Type", value=selected_case.get("case_type", "civil"))

if not st.button("🔍 Run Research"):
    st.stop()

if not query.strip() or not case_reference.strip():
    st.warning("Please provide both case reference and question.")
    st.stop()

payload = {
    "request_id": f"UI-{case_reference[:20]}",
    "jurisdiction": jurisdiction,
    "case_type": case_type,
    "case_context": query,
    "constraints": {},
}

with st.spinner("Calling research API…"):
    try:
        response = requests.post("http://127.0.0.1:8000/research/run", json=payload, timeout=30)
        response.raise_for_status()
        api_result = response.json()
    except Exception as exc:
        st.error(f"Research API unavailable or failed: {exc}")
        st.stop()

answer_text = "\n".join(api_result.get("messages", []))
precedents = api_result.get("precedents", [])

citations: List[Dict[str, str]] = [
    {
        "case_id": case_reference,
        "case_title": item.get("title", "Retrieved Source"),
        "court": item.get("court", jurisdiction),
        "year": "",
        "bench": "",
        "document_type": "Retrieved Document",
        "source": item.get("citation", "") or "RAG Corpus",
        "excerpt": "",
        "storage_path": "",
    }
    for item in precedents
]

set_latest_citations(citations)

st.markdown("## 📝 Answer")
st.success("Research response received.")
st.markdown(answer_text or "No answer text returned by API.")

st.markdown("## 📚 Citations")
render_citation_viewer(citations=citations, expanded=False)

st.markdown("## 📄 Source Preview")
render_document_preview(file_path=None, text_content=answer_text)

render_download_buttons(
    answer_text=answer_text,
    citations=citations,
    raw_content=answer_text,
    filename_prefix=case_reference.replace(" ", "_")[:40],
)

st.divider()
st.caption("Always verify cited passages in original sources before relying on outputs.")
