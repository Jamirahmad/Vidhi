"""Legal Aid Page."""

from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="Legal Aid", page_icon="⚖️", layout="wide")

st.title("⚖️ Legal Aid & Guidance")
st.markdown(
    """
    This page collects legal-aid requests and displays backend responses.
    It does not provide legal advice.
    """
)

area_of_law = st.text_input("Area of Law", placeholder="e.g., Consumer Protection")
issue_description = st.text_area("Describe the issue", height=180)

if not area_of_law.strip() or not issue_description.strip():
    st.info("Provide area of law and issue details to continue.")
    st.stop()

if st.button("Get General Guidance"):
    st.session_state["legal_aid_request"] = {
        "area_of_law": area_of_law.strip(),
        "issue_description": issue_description.strip(),
    }
    st.success("Request captured. Connect a legal-aid backend to generate guidance.")

if "legal_aid_response" in st.session_state:
    response = st.session_state["legal_aid_response"]
    st.markdown("### 📘 Guidance Response")
    st.write(response)
else:
    st.warning("No live legal-aid response available in this environment.")

st.divider()
st.caption(
    "This page provides informational workflow support only and does not constitute legal advice."
)
