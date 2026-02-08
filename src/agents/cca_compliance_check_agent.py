"""
CCA – Compliance Check Agent

Responsibilities:
- Validate court-specific filing requirements
- Check document structure & mandatory sections
- Flag missing annexures, affidavits, signatures
- Enforce human review on any uncertainty

This agent NEVER auto-fixes content.
It only validates and flags issues.
"""

from typing import Dict, Any, List

from src.agents.base_agent import BaseAgent, AgentResultStatus


class ComplianceCheckAgent(BaseAgent):
    """
    Compliance Guard Agent (CCA)
    """

    def __init__(self):
        super().__init__(
            name="CCA_ComplianceCheckAgent",
            requires_human_review=True  # Compliance ALWAYS needs lawyer sign-off
        )

    # ------------------------------------------------------------------
    # Input Validation
    # ------------------------------------------------------------------

    def validate_input(self, input_data: Dict[str, Any]) -> None:
        required_fields = [
            "draft_document",
            "jurisdiction",
            "court",
            "case_type"
        ]

        missing = [field for field in required_fields if field not in input_data]

        if missing:
            raise ValueError(f"Missing required input fields: {missing}")

        if not isinstance(input_data["draft_document"], str):
            raise TypeError("draft_document must be a string")

    # ------------------------------------------------------------------
    # Core Logic
    # ------------------------------------------------------------------

    def run(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        draft = input_data["draft_document"]
        jurisdiction = input_data["jurisdiction"]
        court = input_data["court"]
        case_type = input_data["case_type"]

        issues: List[str] = []
        checks_performed: List[str] = []

        # --- Universal Checks ---
        checks_performed.append("basic_structure_check")
        if len(draft.strip()) < 500:
            issues.append("Draft appears unusually short for a legal filing")

        # --- Mandatory Sections ---
        mandatory_sections = [
            "Facts",
            "Prayer",
            "Verification"
        ]

        for section in mandatory_sections:
            checks_performed.append(f"section_check:{section}")
            if section.lower() not in draft.lower():
                issues.append(f"Missing mandatory section: {section}")

        # --- Case-Type Specific Checks ---
        if case_type.lower() == "criminal":
            checks_performed.append("criminal_case_checks")
            if "IPC" not in draft and "CrPC" not in draft:
                issues.append("No IPC / CrPC sections referenced in criminal case")

        if case_type.lower() == "civil":
            checks_performed.append("civil_case_checks")
            if "CPC" not in draft:
                issues.append("No CPC sections referenced in civil case")

        # --- Court-Specific Checks (High-Level) ---
        checks_performed.append("court_specific_checks")
        if court.lower() == "supreme court" and "Article 136" not in draft:
            issues.append("Possible missing reference to Article 136 for Supreme Court filing")

        # --- Annexures & Signatures ---
        checks_performed.append("annexure_check")
        if "Annexure" not in draft:
            issues.append("No annexures referenced")

        checks_performed.append("signature_check")
        if "Advocate" not in draft and "Counsel" not in draft:
            issues.append("Advocate signature / designation not found")

        status = (
            AgentResultStatus.SUCCESS
            if not issues
            else AgentResultStatus.UNCERTAIN
        )

        return {
            "status": status,
            "issues_found": issues,
            "checks_performed": checks_performed,
            "jurisdiction": jurisdiction,
            "court": court,
            "case_type": case_type,
            "compliance_summary": (
                "No major compliance issues detected"
                if not issues
                else "Compliance issues detected – lawyer review required"
            )
        }

    # ------------------------------------------------------------------
    # Output Validation
    # ------------------------------------------------------------------

    def validate_output(self, output_data: Dict[str, Any]) -> None:
        required_fields = [
            "status",
            "issues_found",
            "checks_performed",
            "compliance_summary"
        ]

        missing = [field for field in required_fields if field not in output_data]

        if missing:
            raise ValueError(f"Missing required output fields: {missing}")

        if not isinstance(output_data["issues_found"], list):
            raise TypeError("issues_found must be a list")
