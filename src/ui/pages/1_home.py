"""
Home Page

Entry point for the Legal AI Research Assistant.
Sets context, expectations, and navigation.
"""

from __future__ import annotations

import streamlit as st


# ---------------------------------------------------------------------
# Page Config
# ---------------------------------------------------------------------

st.set_page_config(
    page_title="Legal Research Assistant",
    page_icon="⚖️",
    layout="wide",
)


# ---------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------

st.title("⚖️ Legal Research Assistant")

st.markdown(
    """
    Welcome to the **Legal Research Assistant** — a system designed to help you
    **analyze case documents, retrieve relevant precedents, and generate
    grounded answers with citations**.

    This tool is built for **accuracy, traceability, and review**, not blind automation.
    """
)


# ---------------------------------------------------------------------
# What This Tool Does
# ---------------------------------------------------------------------

st.markdown("### 🔍 What you can do here")

st.markdown(
    """
    - Upload or fetch **judgments, petitions, and legal documents**
    - Ask **case-specific legal questions**
    - Retrieve **relevant precedents and excerpts**
    - Generate answers **with verifiable citations**
    - Preview source documents before trusting the output
    """
)


# ---------------------------------------------------------------------
# How It Works
# ---------------------------------------------------------------------

with st.expander("🧠 How it works (high level)", expanded=False):
    st.markdown(
        """
        1. **Ingestion**  
           Documents are cleaned, parsed, chunked, and stored with metadata.

        2. **Retrieval**  
           Relevant chunks are retrieved using semantic search and reranking.

        3. **Answer Generation**  
           Answers are generated strictly from retrieved sources.

        4. **Verification**  
           Every answer is backed by citations you can inspect and preview.
        """
    )


# ---------------------------------------------------------------------
# Trust & Limitations
# ---------------------------------------------------------------------

st.markdown("### ⚠️ Important limitations")

st.warning(
    """
    - This system **does not replace legal advice**
    - Outputs may be incomplete or context-dependent
    - Always verify citations before relying on an answer
    - Use this tool as a **research assistant**, not a decision-maker
    """
)


# ---------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------

st.markdown("### 🚀 Get started")

col1, col2 = st.columns(2)

with col1:
    st.page_link(
        "pages/2_case_analysis.py",
        label="📁 Start Case Analysis",
        help="Upload or select documents and ask questions",
    )

with col2:
    st.page_link(
        "pages/3_about.py",
        label="ℹ️ About the System",
        help="Learn about architecture, design choices, and safeguards",
    )


# ---------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------

st.divider()

st.caption(
    "Built with a focus on transparency, auditability, and responsible AI use."
)
