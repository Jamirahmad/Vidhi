"""
LAF – Legal Aid Finder Agent

Responsibilities:
- Provide information about available legal aid and pro-bono options
- Suggest appropriate legal services authorities based on jurisdiction
- NEVER determine eligibility or recommend a specific lawyer
- Provide official links and next steps only
"""

from typing import Dict, Any, List

from src.agents.base_agent import BaseAgent, AgentResultStatus


class LegalAidFinderAgent(BaseAgent):
    """
    LAF – Legal Aid Finder Agent
    """

    def __init__(self):
        super().__init__(
            name="LAF_LegalAidFinderAgent",
            requires_human_review=True  # Guidance impacts access to justice
        )

    # ------------------------------------------------------------------
    # Input Validation
    # ------------------------------------------------------------------

    def validate_input(self, input_data: Dict[str, Any]) -> None:
        required_fields = [
            "jurisdiction",
            "case_type",
            "user_profile"
        ]

        missing = [f for f in required_fields if f not in input_data]
        if missing:
            raise ValueError(f"Missing required input fields: {missing}")

        if not isinstance(input_data["user_profile"], dict):
            raise TypeError("user_profile must be a dictionary")

    # ------------------------------------------------------------------
    # Core Logic
    # ------------------------------------------------------------------

    def run(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        jurisdiction = input_data["jurisdiction"]
        case_type = input_data["case_type"].lower()

        suggestions: List[Dict[str, str]] = []

        # --- National Legal Services Authority ---
        suggestions.append({
            "name": "National Legal Services Authority (NALSA)",
            "description": (
                "Statutory body providing free legal services under the Legal Services "
                "Authorities Act, 1987."
            ),
            "website": "https://nalsa.gov.in",
            "scope": "Nationwide"
        })

        # --- State Legal Services Authority ---
        suggestions.append({
            "name": f"{jurisdiction} State Legal Services Authority",
            "description": (
                "Provides free legal aid and Lok Adalat services at the state and "
                "district level."
            ),
            "website": "https://nalsa.gov.in/state-legal-services-authorities",
            "scope": jurisdiction
        })

        # --- Court-based Legal Services ---
        suggestions.append({
            "name": "District / Taluk Legal Services Committee",
            "description": (
                "Legal aid clinics attached to district and taluk courts."
            ),
            "website": "https://nalsa.gov.in/legal-services-clinics",
            "scope": "District level"
        })

        # --- Specialized forums ---
        if case_type in {"consumer", "women", "child"}:
            suggestions.append({
                "name": "Specialized Legal Aid Clinics",
                "description": (
                    "Legal aid clinics for women, children, and consumer disputes."
                ),
                "website": "https://nalsa.gov.in/schemes",
                "scope": "Case-type specific"
            })

        return {
            "status": AgentResultStatus.SUCCESS,
            "jurisdiction": jurisdiction,
            "case_type": case_type,
            "legal_aid_options": suggestions,
            "disclaimer": (
                "This information is provided for awareness only. "
                "Eligibility and appointment of legal aid counsel "
                "are determined by the respective legal services authorities."
            )
        }

    # ------------------------------------------------------------------
    # Output Validation
    # ------------------------------------------------------------------

    def validate_output(self, output_data: Dict[str, Any]) -> None:
        required_fields = [
            "status",
            "legal_aid_options"
        ]

        missing = [f for f in required_fields if f not in output_data]
        if missing:
            raise ValueError(f"Missing required output fields: {missing}")

        if not isinstance(output_data["legal_aid_options"], list):
            raise TypeError("legal_aid_options must be a list")
