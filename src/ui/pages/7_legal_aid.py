"""
Legal Aid Page

Provides informational legal guidance, awareness of rights,
and next-step suggestions without offering legal advice.
"""

from __future__ import annotations

import streamlit as st


# ---------------------------------------------------------------------
# Page Config
# ---------------------------------------------------------------------

st.set_page_config(
    page_title="Legal Aid",
    page_icon="⚖️",
    layout="wide",
)


# ---------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------

st.title("⚖️ Legal Aid & Guidance")

st.markdown(
    """
    This page provides **general legal information and guidance**
    to help users understand common legal issues and possible next steps.

    🚨 **This is not legal advice.**  
    For case-specific advice, always consult a qualified legal professional.
    """
)


# ---------------------------------------------------------------------
# Area of Law Selection
# ---------------------------------------------------------------------

st.markdown("## 📂 Select Area of Law")

area_of_law = st.selectbox(
    "Choose a category",
    options=[
        "Civil Disputes",
        "Criminal Matters",
        "Family Law",
        "Employment & Labour",
        "Consumer Protection",
        "Property & Land",
        "Constitutional Remedies",
        "Other",
    ],
)

if not area_of_law:
    st.stop()


# ---------------------------------------------------------------------
# Issue Description
# ---------------------------------------------------------------------

st.markdown("## 📝 Describe the Issue")

issue_description = st.text_area(
    "Briefly describe your situation",
    height=180,
    placeholder=(
        "Example: My consumer complaint has been pending for several years "
        "and I am unsure what remedies are available."
    ),
)

if not issue_description.strip():
    st.info("Please describe the issue to continue.")
    st.stop()


# ---------------------------------------------------------------------
# Generate Guidance
# ---------------------------------------------------------------------

st.markdown("## 💡 General Guidance")

if st.button("Get General Guidance"):
    with st.spinner("Preparing guidance…"):
        # -------------------------------------------------------------
        # PLACEHOLDER: Informational guidance engine
        # -------------------------------------------------------------
        # guidance = legal_aid_service.generate(
        #     area=area_of_law,
        #     issue=issue_description,
        # )
        # -------------------------------------------------------------

        # Mocked informational response
        guidance = {
            "overview": (
                "Delays in adjudication are common in consumer disputes. "
                "Several procedural and constitutional remedies may be available."
            ),
            "possible_steps": [
                "Check the current status of the case with the relevant forum.",
                "Consider filing an application for early hearing.",
                "Explore alternative dispute resolution mechanisms if applicable.",
                "Seek advice from a legal aid clinic or consumer organization.",
            ],
            "important_note": (
                "The suitability of these steps depends on the facts of the case "
                "and applicable law."
            ),
        }

        st.success("General information prepared.")


# ---------------------------------------------------------------------
# Display Guidance
# ---------------------------------------------------------------------

if "guidance" in locals():

    st.markdown("### 📘 Overview")
    st.write(guidance["overview"])

    st.markdown("### 🧭 Possible Next Steps")
    for step in guidance["possible_steps"]:
        st.markdown(f"- {step}")

    st.markdown("### ⚠️ Important Note")
    st.warning(guidance["important_note"])


# ---------------------------------------------------------------------
# Legal Aid Resources
# ---------------------------------------------------------------------

st.markdown("## 🏛 Legal Aid Resources (India)")

st.markdown(
    """
    You may consider reaching out to the following **official and non-profit resources**:
    - **National Legal Services Authority (NALSA)**
    - **State Legal Services Authorities**
    - **District Legal Services Committees**
    - **Recognized Legal Aid Clinics**
    - **Consumer Forums & Lok Adalats**
    """
)


# ---------------------------------------------------------------------
# Disclaimer
# ---------------------------------------------------------------------

st.divider()
st.caption(
    "This page provides general legal information only and does not "
    "constitute legal advice, representation, or a lawyer-client relationship."
)
