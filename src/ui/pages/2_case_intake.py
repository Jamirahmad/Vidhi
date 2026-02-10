"""
Case Intake Page

Collects case metadata and source documents for ingestion.
Acts as the controlled entry point into the ingestion pipeline.
"""

from __future__ import annotations

from typing import Optional

import streamlit as st

from src.ui.components.case_form import render_case_form
from src.ui.components.download_buttons import render_download_buttons


# ---------------------------------------------------------------------
# Page Config
# ---------------------------------------------------------------------

st.set_page_config(
    page_title="Case Intake",
    page_icon="📁",
    layout="wide",
)


# ---------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------

st.title("📁 Case Intake")
st.markdown(
    """
    Use this page to **register a case and upload source documents**.
    All documents will be processed, indexed, and made available
    for retrieval and citation-based analysis.
    """
)


# ---------------------------------------------------------------------
# Case Metadata
# ---------------------------------------------------------------------

st.markdown("## 🧾 Case Information")

case_data = render_case_form(
    form_key="case_intake_form",
    submit_label="Register Case",
)

if not case_data:
    st.stop()

st.success("Case registered successfully.")
st.json(case_data)


# ---------------------------------------------------------------------
# Document Upload
# ---------------------------------------------------------------------

st.markdown("## 📤 Upload Documents")

uploaded_files = st.file_uploader(
    label="Upload case documents (PDF, DOCX, TXT)",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True,
)

if not uploaded_files:
    st.info("Please upload at least one document to continue.")
    st.stop()

st.success(f"{len(uploaded_files)} document(s) selected.")


# ---------------------------------------------------------------------
# Review & Confirm
# ---------------------------------------------------------------------

st.markdown("## ✅ Review & Confirm")

with st.expander("Review uploaded documents", expanded=True):
    for file in uploaded_files:
        st.markdown(
            f"- **{file.name}** "
            f"({file.size // 1024} KB)"
        )

confirm = st.checkbox(
    "I confirm that the uploaded documents belong to this case "
    "and are safe to process."
)

if not confirm:
    st.warning("Please confirm before proceeding.")
    st.stop()


# ---------------------------------------------------------------------
# Ingestion Trigger (placeholder)
# ---------------------------------------------------------------------

st.markdown("## 🚀 Start Ingestion")

if st.button("Ingest Case Documents"):
    with st.spinner("Ingesting documents…"):
        # -------------------------------------------------------------
        # PLACEHOLDER: Backend ingestion hook
        # -------------------------------------------------------------
        # ingestion_pipeline.ingest(
        #     case_metadata=case_data,
        #     files=uploaded_files,
        # )
        # -------------------------------------------------------------

        st.success("Documents submitted for ingestion.")

        # Optional: allow immediate download of submitted metadata
        render_download_buttons(
            raw_content=str(case_data),
            filename_prefix=case_data["case_id"],
        )


# ---------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------

st.divider()
st.caption(
    "Documents are processed asynchronously. "
    "You can proceed to analysis once ingestion completes."
)
