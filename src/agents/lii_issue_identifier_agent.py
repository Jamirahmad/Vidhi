"""
LII – Legal Issue Identifier Agent

Responsibilities:
- Extract key legal issues from case facts
- Identify potentially applicable statutes and sections
- Clearly separate facts vs legal questions
- NEVER classify guilt, liability, or outcome
"""

from typing import Dict, Any, List

from src.agents.base_agent import BaseAgent, AgentResultStatus


class IssueIdentifierAgent(BaseAgent):
    """
    LII – Legal Issue Identifier Agent
    """

    def __init__(self):
        super().__init__(
            name="LII_IssueIdentifierAgent",
            requires_human_review=True  # Issue framing is lawyer-sensitive
        )

    # ------------------------------------------------------------------
    # Input Validation
    # ------------------------------------------------------------------

    def validate_input(self, input_data: Dict[str, Any]) -> None:
        required_fields = [
            "case_facts",
            "case_type",
            "jurisdiction"
        ]

        missing = [f for f in required_fields if f not in input_data]
        if missing:
            raise ValueError(f"Missing required input fields: {missing}")

        if not isinstance(input_data["case_facts"], str):
            raise TypeError("case_facts must be a string")

    # ------------------------------------------------------------------
    # Core Logic
    # ------------------------------------------------------------------

    def run(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        case_facts: str = input_data["case_facts"].lower()
        case_type: str = input_data["case_type"].lower()

        identified_issues: List[str] = []
        applicable_sections: List[str] = []
        ambiguity_flags: List[str] = []

        # --- Criminal law heuristics ---
        if case_type == "criminal":
            if "cheat" in case_facts or "fraud" in case_facts:
                identified_issues.append("Whether the ingredients of cheating are made out")
                applicable_sections.append("IPC Section 420")

            if "assault" in case_facts or "hurt" in case_facts:
                identified_issues.append("Whether the act amounts to causing hurt or grievous hurt")
                applicable_sections.append("IPC Sections 319–325")

            if "arrest" in case_facts or "custody" in case_facts:
                identified_issues.append("Whether arrest and detention procedures were lawful")
                applicable_sections.append("CrPC Sections 41, 50")

        # --- Civil law heuristics ---
        if case_type == "civil":
            if "agreement" in case_facts or "contract" in case_facts:
                identified_issues.append("Whether a valid and enforceable contract exists")
                applicable_sections.append("Indian Contract Act, 1872")

            if "property" in case_facts or "possession" in case_facts:
                identified_issues.append("Whether the plaintiff has a lawful right over the property")
                applicable_sections.append("Specific Relief Act / CPC")

        # --- Consumer disputes ---
        if case_type == "consumer":
            identified_issues.append("Whether there is deficiency in service or unfair trade practice")
            applicable_sections.append("Consumer Protection Act, 2019")

        # --- Fallback for low extraction ---
        if not identified_issues:
            ambiguity_flags.append(
                "Unable to confidently identify legal issues from provided facts"
            )

        status = (
            AgentResultStatus.SUCCESS
            if identified_issues
            else AgentResultStatus.UNCERTAIN
        )

        return {
            "status": status,
            "legal_issues": identified_issues,
            "applicable_sections": applicable_sections,
            "ambiguity_flags": ambiguity_flags,
            "disclaimer": (
                "Identified issues and sections are indicative only and must be "
                "verified by a qualified legal professional."
            )
        }

    # ------------------------------------------------------------------
    # Output Validation
    # ------------------------------------------------------------------

    def validate_output(self, output_data: Dict[str, Any]) -> None:
        required_fields = [
            "status",
            "legal_issues",
            "applicable_sections"
        ]

        missing = [f for f in required_fields if f not in output_data]
        if missing:
            raise ValueError(f"Missing required output fields: {missing}")

        if not isinstance(output_data["legal_issues"], list):
            raise TypeError("legal_issues must be a list")

        if not isinstance(output_data["applicable_sections"], list):
            raise TypeError("applicable_sections must be a list")
