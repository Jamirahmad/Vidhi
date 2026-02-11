"""
LAB – Legal Argument Builder Agent

Responsibilities:
- Build structured legal arguments and counter-arguments
- Use verified precedents and identified issues only
- NEVER predict outcomes or give legal advice
- Clearly separate supporting vs opposing arguments
- Escalate to human review on ambiguity or weak support
"""

from __future__ import annotations

from typing import Any

from src.agents.base_agent import BaseAgent


class LABArgumentBuilderAgent(BaseAgent):
    """
    LAB - Legal Argument Builder Agent

    Responsibility:
    - Build structured pro and counter arguments based on issues + analysis.
    - Should avoid fabricated case citations.
    - Should produce argument structure suitable for legal drafting.

    Output contract:
    {
        "arguments_text": str,
        "pro_arguments": list[str],
        "counter_arguments": list[str]
    }
    """

    agent_name = "LABArgumentBuilderAgent"
    agent_version = "2.0"

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config=config)

    def _execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Expected payload:
        {
            "issues": dict OR list[str] OR str,
            "analysis_text": str (optional),
            "case_description": str (optional)
        }
        """
        issues_obj = payload.get("issues", [])
        analysis_text = str(payload.get("analysis_text", "")).strip()
        case_description = str(payload.get("case_description", "")).strip()

        issues: list[str] = []

        if isinstance(issues_obj, dict):
            primary = issues_obj.get("primary_issues", []) or []
            secondary = issues_obj.get("secondary_issues", []) or []
            issues = [str(i).strip() for i in (primary + secondary) if str(i).strip()]

        elif isinstance(issues_obj, list):
            issues = [str(i).strip() for i in issues_obj if str(i).strip()]

        elif isinstance(issues_obj, str):
            issues = [issues_obj.strip()] if issues_obj.strip() else []

        pro_arguments: list[str] = []
        counter_arguments: list[str] = []

        # If no issues found, return generic argument format
        if not issues:
            pro_arguments.append(
                "The facts provided may support the claimant's position depending on evidence and applicable law."
            )
            counter_arguments.append(
                "The opposing party may dispute the claim based on lack of evidence, procedural defects, or limitation issues."
            )

        else:
            for issue in issues:
                pro_arguments.append(
                    f"On the issue of '{issue}', the claimant may argue that the facts establish a legal right or breach."
                )
                pro_arguments.append(
                    f"The claimant may further argue that the conduct of the opposing party violates applicable statutory obligations."
                )

                counter_arguments.append(
                    f"On the issue of '{issue}', the opposing party may argue that the claim is not maintainable due to lack of legal basis."
                )
                counter_arguments.append(
                    "The opposing party may argue that the claimant has not produced sufficient documentary or factual evidence."
                )

        # Add analysis-driven refinement
        if analysis_text:
            pro_arguments.append(
                "The legal analysis supports the claimant’s position by highlighting key statutory interpretation and factual alignment."
            )
            counter_arguments.append(
                "However, the opposing party may challenge the analysis by presenting alternative statutory interpretation or disputing facts."
            )

        if case_description:
            pro_arguments.append(
                "The factual background strengthens the claimant’s case if the timeline and evidence are consistent."
            )
            counter_arguments.append(
                "If inconsistencies exist in the factual timeline, the opposing party may use them to weaken credibility."
            )

        # Build argument narrative text
        lines: list[str] = []
        lines.append("PRO ARGUMENTS:")
        for idx, arg in enumerate(pro_arguments, start=1):
            lines.append(f"{idx}. {arg}")

        lines.append("")
        lines.append("COUNTER ARGUMENTS:")
        for idx, arg in enumerate(counter_arguments, start=1):
            lines.append(f"{idx}. {arg}")

        arguments_text = "\n".join(lines).strip()

        return {
            "arguments_text": arguments_text,
            "pro_arguments": pro_arguments,
            "counter_arguments": counter_arguments,
        }
