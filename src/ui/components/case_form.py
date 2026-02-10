"""
Case Form Component

Reusable UI component for capturing case / document ingestion details.
Designed for Streamlit-based applications.
"""

from __future__ import annotations

from typing import Dict, Optional

import streamlit as st


# ---------------------------------------------------------------------
# Case Form
# ---------------------------------------------------------------------

def render_case_form(
    *,
    form_key: str = "case_form",
    submit_label: str = "Submit Case",
) -> Optional[Dict[str, str]]:
    """
    Render a case input form.

    Returns:
        dict of form values if submitted, else None
    """

    with st.form(key=form_key):
        st.subheader("📁 Case Details")

        col1, col2 = st.columns(2)

        with col1:
            case_id = st.text_input(
                "Case ID *",
                placeholder="e.g. SC-2024-1234",
            )

            court = st.selectbox(
                "Court / Tribunal *",
                options=[
                    "Supreme Court",
                    "High Court",
                    "Tribunal",
                    "Other",
                ],
            )

            jurisdiction = st.text_input(
                "Jurisdiction",
                placeholder="e.g. India, Maharashtra",
            )

        with col2:
            case_title = st.text_input(
                "Case Title *",
                placeholder="Petitioner vs Respondent",
            )

            year = st.text_input(
                "Year",
                placeholder="e.g. 2024",
            )

            bench = st.text_input(
                "Bench / Judge",
                placeholder="Optional",
            )

        st.markdown("### 📄 Document Information")

        document_type = st.selectbox(
            "Document Type *",
            options=[
                "Judgment",
                "Order",
                "Petition",
                "Affidavit",
                "Notice",
                "Other",
            ],
        )

        source = st.selectbox(
            "Source *",
            options=[
                "Upload",
                "Indian Kanoon",
                "Court Website",
                "Other",
            ],
        )

        remarks = st.text_area(
            "Remarks",
            placeholder="Optional notes about this case or document",
        )

        submitted = st.form_submit_button(submit_label)

        if not submitted:
            return None

        # -------------------------------------------------------------
        # Validation
        # -------------------------------------------------------------

        errors = []

        if not case_id.strip():
            errors.append("Case ID is required")

        if not case_title.strip():
            errors.append("Case Title is required")

        if errors:
            for err in errors:
                st.error(err)
            return None

        # -------------------------------------------------------------
        # Normalized payload
        # -------------------------------------------------------------

        return {
            "case_id": case_id.strip(),
            "case_title": case_title.strip(),
            "court": court,
            "jurisdiction": jurisdiction.strip(),
            "year": year.strip(),
            "bench": bench.strip(),
            "document_type": document_type,
            "source": source,
            "remarks": remarks.strip(),
        }
