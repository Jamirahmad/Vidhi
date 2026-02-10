"""
Main Streamlit Application Entry Point

This file bootstraps the Legal Intelligence Platform UI.
All individual pages are located under src/ui/pages/.
"""

from __future__ import annotations

import streamlit as st


# ---------------------------------------------------------------------
# App Configuration
# ---------------------------------------------------------------------

st.set_page_config(
    page_title="Legal Intelligence Platform",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------
# Sidebar – Global Navigation / Branding
# ---------------------------------------------------------------------

with st.sidebar:
    st.markdown("## ⚖️ Legal Intelligence Platform")

    st.caption(
        """
        Research • Reasoning • Drafting • Compliance
        """
    )

    st.divider()

    st.markdown(
        """
        ### 📚 Workflow
        1. Case Intake  
        2. Case Research  
        3. Argument Builder  
        4. Document Generator  
        5. Compliance Check  
        6. Legal Aid  

        ---
        """
    )

    st.markdown(
        """
        ### ℹ️ About
        This platform assists legal professionals and researchers
        in drafting, reviewing, and validating legal content.

        **Human review is always required.**
        """
    )


# ---------------------------------------------------------------------
# Main Landing Content
# ---------------------------------------------------------------------

st.title("⚖️ Legal Intelligence Platform")

st.markdown(
    """
    Welcome to the **Legal Intelligence Platform**.

    This application helps you:
    - 🔍 Research legal questions with traceable citations
    - 🧠 Build structured legal arguments
    - 🧾 Generate review-ready legal documents
    - ✅ Perform compliance and citation checks
    - ⚖️ Access general legal aid information

    Use the **navigation menu on the left** to begin.
    """
)

st.info(
    """
    💡 Tip: Follow the workflow order for best results:
    **Case Intake → Research → Argument → Document → Compliance**
    """
)


# ---------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------

st.divider()

st.caption(
    "© 2026 Legal Intelligence Platform • "
    "For informational and research assistance only."
)
