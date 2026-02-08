"""
LAB – Legal Argument Builder Agent

Responsibilities:
- Build structured legal arguments and counter-arguments
- Use verified precedents and identified issues only
- NEVER predict outcomes or give legal advice
- Clearly separate supporting vs opposing arguments
- Escalate to human review on ambiguity or weak support
"""

from typing import Dict, Any, List

from src.agents.base_agent import BaseAgent, AgentResultStatus


class ArgumentBuilderAgent(BaseAgent):
    """
    LAB – Legal Argument Builder Agent
    """

    def __init__(self):
        super().__init__(
            name="LAB_ArgumentBuilderAgent",
            requires_human_review=True  # Arguments always need lawyer review
        )

    # ------------------------------------------------------------------
    # Input Validation
    # ------------------------------------------------------------------

    def validate_input(self, input_data: Dict[str, Any]) -> None:
        required_fields = [
            "legal_issues",
            "precedents",
            "limitation_analysis"
        ]

        missing = [f for f in required_fields if f not in input_data]
        if missing:
            raise ValueError(f"Missing required input fields: {missing}")

        if not isinstance(input_data["legal_issues"], list):
            raise TypeError("legal_issues must be a list")

        if not isinstance(input_data["precedents"], list):
            raise TypeError("precedents must be a list")

        if not isinstance(input_data["limitation_analysis"], dict):
            raise TypeError("limitation_analysis must be a dict")

    # ------------------------------------------------------------------
    # Core Logic
    # ------------------------------------------------------------------

    def run(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        issues: List[str] = input_data["legal_issues"]
        precedents: List[Dict[str, Any]] = input_data["precedents"]
        limitation = input_data["limitation_analysis"]

        supporting_arguments: List[str] = []
        counter_arguments: List[str] = []

        # --- Build arguments issue-by-issue ---
        for issue in issues:
            issue_precedents = [
                p for p in precedents
                if issue.lower() in (p.get("summary", "").lower())
            ]

            if not issue_precedents:
                counter_arguments.append(
                    f"No strong precedent found directly supporting the issue: '{issue}'."
                )
                continue

            for p in issue_precedents:
                supporting_arguments.append(
                    f"For the issue '{issue}', reliance may be placed on "
                    f"{p.get('case_title')} ({p.get('court')}, {p.get('year')}), "
                    f"which discusses similar legal principles."
                )

        # --- Limitation-aware counter arguments ---
        if limitation.get("status") != AgentResultStatus.SUCCESS:
            counter_arguments.append(
                "Limitation applicability is unclear or potentially adverse; "
                "this may be raised as a preliminary objection."
            )

        # --- Confidence heuristic ---
        confidence_score = min(
            1.0,
            (len(supporting_arguments) / max(len(issues), 1))
        )

        status = (
            AgentResultStatus.SUCCESS
            if confidence_score >= 0.6
            else AgentResultStatus.UNCERTAIN
        )

        return {
            "status": status,
            "supporting_arguments": supporting_arguments,
            "counter_arguments": counter_arguments,
            "confidence": round(confidence_score, 2),
            "disclaimer": (
                "These arguments are indicative drafts based on identified issues "
                "and precedents and must be reviewed by a qualified legal professional."
            )
        }

    # ------------------------------------------------------------------
    # Output Validation
    # ------------------------------------------------------------------

    def validate_output(self, output_data: Dict[str, Any]) -> None:
        required_fields = [
            "status",
            "supporting_arguments",
            "counter_arguments"
        ]

        missing = [f for f in required_fields if f not in output_data]
        if missing:
            raise ValueError(f"Missing required output fields: {missing}")

        if not isinstance(output_data["supporting_arguments"], list):
            raise TypeError("supporting_arguments must be a list")

        if not isinstance(output_data["counter_arguments"], list):
            raise TypeError("counter_arguments must be a list")
