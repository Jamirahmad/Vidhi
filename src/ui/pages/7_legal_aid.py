"""Legal Aid Page."""

from __future__ import annotations

import requests
import streamlit as st

st.set_page_config(page_title="Legal Aid", page_icon="⚖️", layout="wide")

st.title("⚖️ Legal Aid & Guidance")
st.markdown("This page provides general legal-aid guidance using retrieval-backed context. It does not provide legal advice and always requires human review.")
st.markdown(
    """
    This page provides general legal-aid guidance using retrieval-backed context.
    It does not provide legal advice and always requires human review.
    """
)

st.markdown("## 📂 Area of Law")
area_of_law = st.selectbox(
    "Choose an area of law",
    options=[
        "Select an area of law",
        "Civil Disputes",
        "Criminal Matters",
        "Family Law",
        "Employment & Labour",
        "Consumer Protection",
        "Property & Land",
        "Constitutional Remedies",
        "Other",
    ],
    index=0,
)

st.markdown("## 📝 Describe the Issue")
issue_description = st.text_area(
    "Briefly describe your situation",
    height=180,
    placeholder="Describe your legal issue in your own words...",
)

if st.button("Generate Ethical Guidance"):
    if area_of_law == "Select an area of law":
        st.warning("Please choose an area of law before continuing.")
        st.stop()

    if not issue_description.strip():
        st.warning("Please describe the issue to continue.")
        st.stop()

    payload = {
        "request_id": f"AID-{area_of_law[:10]}",
        "jurisdiction": "India",
        "case_type": area_of_law,
        "case_context": issue_description,
        "constraints": {"mode": "legal_aid", "ethical": "true"},
    }

    with st.spinner("Generating guidance from RAG/LLM backend…"):
        try:
            response = requests.post("http://127.0.0.1:8000/research/run", json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
        except Exception as exc:
            st.error(f"Could not generate guidance from backend: {exc}")
            st.stop()

    guidance_text = "\n".join(result.get("messages", []))
    precedents = result.get("precedents", [])

    st.markdown("### 📘 Guidance")
    st.write(guidance_text or "No guidance returned.")

    st.markdown("### 📚 Retrieved References")
    if precedents:
        for idx, item in enumerate(precedents, start=1):
            st.markdown(f"{idx}. **{item.get('title', 'Untitled')}** — {item.get('citation', 'Source unavailable')}")
    else:
        st.info("No references returned for this request.")

    st.warning(
        "Ethical safeguard: This output is informational only, not legal advice. "
        "Please consult a qualified legal professional before taking action."
    )
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
