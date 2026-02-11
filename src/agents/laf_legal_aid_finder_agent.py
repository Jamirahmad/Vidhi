"""
LAF – Legal Aid Finder Agent

Responsibilities:
- Provide information about available legal aid and pro-bono options
- Suggest appropriate legal services authorities based on jurisdiction
- NEVER determine eligibility or recommend a specific lawyer
- Provide official links and next steps only
"""

from __future__ import annotations

from typing import Any

from src.agents.base_agent import BaseAgent


class LAFLegalAidFinderAgent(BaseAgent):
    """
    LAF - Legal Aid Finder Agent

    Responsibility:
    - Provide guidance on how to find legal aid services.
    - Must avoid hallucinating specific phone numbers / office addresses.
    - Must return structured output.

    Output contract:
    {
        "legal_aid_options": list[str],
        "summary": str
    }
    """

    agent_name = "LAFLegalAidFinderAgent"
    agent_version = "2.0"

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config=config)

    def _execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Expected payload:
        {
            "jurisdiction": str,
            "case_description": str (optional)
        }
        """
        jurisdiction = str(payload.get("jurisdiction", "")).strip()
        case_description = str(payload.get("case_description", "")).strip()

        legal_aid_options: list[str] = []

        if jurisdiction.lower() in {"india", "indian"}:
            legal_aid_options.extend(
                [
                    "National Legal Services Authority (NALSA) – official legal aid framework in India.",
                    "State Legal Services Authority (SLSA) – available in each state for free legal aid.",
                    "District Legal Services Authority (DLSA) – district-level legal aid and legal awareness support.",
                    "Legal aid clinics in law colleges recognized by State Legal Services Authorities.",
                    "NGOs working in legal rights support (women, labor, consumer, tenant, etc.).",
                ]
            )
            summary = (
                "For India, legal aid is commonly provided through NALSA, SLSA, and DLSA. "
                "You can approach your nearest District Court complex for DLSA help."
            )
        else:
            legal_aid_options.extend(
                [
                    "Government-sponsored legal aid office in your jurisdiction.",
                    "Bar Association pro-bono services (many courts provide assistance desks).",
                    "Legal aid NGOs and community legal clinics.",
                    "University law clinics offering free legal assistance.",
                ]
            )
            summary = (
                f"Legal aid guidance prepared for jurisdiction: {jurisdiction or 'UNKNOWN'}. "
                "For accurate location-based details, consult your local court helpdesk or official government portal."
            )

        if case_description:
            summary += " Eligibility for free legal aid may depend on income, case type, or vulnerability category."

        return {
            "legal_aid_options": legal_aid_options,
            "summary": summary.strip(),
        }
