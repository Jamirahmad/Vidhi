
"""
LAA – Limitation Analysis Agent

Responsibilities:
- Assess whether a claim appears within limitation period
- Identify applicable limitation articles/sections (indicative only)
- Flag ambiguity, exceptions, and condonation possibilities
- NEVER give a final legal opinion
"""

from datetime import datetime
from typing import Dict, Any, Optional

from src.agents.base_agent import BaseAgent, AgentResultStatus


class LimitationAnalysisAgent(BaseAgent):
    """
    LAA – Limitation Analysis Agent
    """

    def __init__(self):
        super().__init__(
            name="LAA_LimitationAnalysisAgent",
            requires_human_review=True  # Limitation is always lawyer-sensitive
        )

    # ------------------------------------------------------------------
    # Input Validation
    # ------------------------------------------------------------------

    def validate_input(self, input_data: Dict[str, Any]) -> None:
        required_fields = [
            "cause_of_action_date",
            "current_date",
            "case_type",
            "jurisdiction"
        ]

        missing = [f for f in required_fields if f not in input_data]
        if missing:
            raise ValueError(f"Missing required input fields: {missing}")

        try:
            datetime.fromisoformat(input_data["cause_of_action_date"])
            datetime.fromisoformat(input_data["current_date"])
        except ValueError:
            raise ValueError("Dates must be in ISO format (YYYY-MM-DD)")

    # ------------------------------------------------------------------
    # Core Logic
    # ------------------------------------------------------------------

    def run(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        cause_date = datetime.fromisoformat(input_data["cause_of_action_date"])
        current_date = datetime.fromisoformat(input_data["current_date"])
        case_type = input_data["case_type"].lower()
        jurisdiction = input_data["jurisdiction"]

        days_elapsed = (current_date - cause_date).days

        # --- Indicative limitation mapping (NON-EXHAUSTIVE) ---
        limitation_days_map = {
            "civil": 3 * 365,        # Typical civil suits (varies widely)
            "consumer": 2 * 365,     # Consumer Protection Act
            "criminal": None,        # No limitation for serious offences
            "service": 1 * 365
        }

        limitation_days = limitation_days_map.get(case_type)

        analysis_notes = []
        status = AgentResultStatus.UNCERTAIN

        if limitation_days is None:
            analysis_notes.append(
                "Limitation depends on offence severity; many criminal offences have no limitation."
            )
            status = AgentResultStatus.UNCERTAIN

        else:
            if days_elapsed <= limitation_days:
                analysis_notes.append(
                    f"Elapsed time ({days_elapsed} days) appears within indicative limitation period."
                )
                status = AgentResultStatus.SUCCESS
            else:
                analysis_notes.append(
                    f"Elapsed time ({days_elapsed} days) exceeds indicative limitation period."
                )
                analysis_notes.append(
                    "Condonation of delay or exception provisions may apply (to be reviewed by a lawyer)."
                )
                status = AgentResultStatus.UNCERTAIN

        return {
            "status": status,
            "case_type": case_type,
            "jurisdiction": jurisdiction,
            "cause_of_action_date": cause_date.date().isoformat(),
            "current_date": current_date.date().isoformat(),
            "days_elapsed": days_elapsed,
            "indicative_limitation_days": limitation_days,
            "analysis_notes": analysis_notes,
            "disclaimer": (
                "This is an indicative limitation analysis only and must be "
                "reviewed by a qualified legal professional."
            )
        }

    # ------------------------------------------------------------------
    # Output Validation
    # ------------------------------------------------------------------

    def validate_output(self, output_data: Dict[str, Any]) -> None:
        required_fields = [
            "status",
            "days_elapsed",
            "analysis_notes"
        ]

        missing = [f for f in required_fields if f not in output_data]
        if missing:
            raise ValueError(f"Missing required output fields: {missing}")

        if not isinstance(output_data["analysis_notes"], list):
            raise TypeError("analysis_notes must be a list")
