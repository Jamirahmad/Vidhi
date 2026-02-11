
"""
LAA – Limitation Analysis Agent

Responsibilities:
- Assess whether a claim appears within limitation period
- Identify applicable limitation articles/sections (indicative only)
- Flag ambiguity, exceptions, and condonation possibilities
- NEVER give a final legal opinion
"""

from __future__ import annotations

from typing import Any

from src.agents.base_agent import BaseAgent


class LAALimitationAnalysisAgent(BaseAgent):
    """
    LAA - Limitation Analysis Agent

    Responsibility:
    - Identify potential limitation period considerations.
    - Provide structured and safe output (no fabricated statutory timelines).

    NOTE:
    Without exact filing dates and statute references, limitation analysis
    must be generic and advisory.

    Output contract:
    {
        "limitation_summary": str,
        "potential_time_bars": list[str],
        "recommended_actions": list[str]
    }
    """

    agent_name = "LAALimitationAnalysisAgent"
    agent_version = "2.0"

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config=config)

    def _execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Expected payload:
        {
            "case_description": str,
            "jurisdiction": str,
            "document_type": str
        }
        """
        case_description = str(payload.get("case_description", "")).strip()
        jurisdiction = str(payload.get("jurisdiction", "")).strip()
        document_type = str(payload.get("document_type", "")).strip()

        potential_time_bars: list[str] = []
        recommended_actions: list[str] = []

        if not case_description:
            limitation_summary = (
                "No case details were provided. Limitation analysis cannot be performed without facts "
                "such as incident date, cause of action date, and filing timeline."
            )
            return {
                "limitation_summary": limitation_summary,
                "potential_time_bars": [],
                "recommended_actions": [
                    "Provide the incident date / cause of action date.",
                    "Provide filing date or expected filing timeline.",
                    "Confirm the applicable statute governing the dispute.",
                ],
            }

        # Generic risk-based output
        limitation_summary = (
            f"Limitation analysis was performed for jurisdiction: {jurisdiction or 'UNKNOWN'}. "
            "Exact limitation period depends on the type of claim and relevant statute. "
            "Since specific dates and statutory references are not provided, this assessment is general."
        )

        # Heuristic hints (not hard legal advice)
        if "delay" in case_description.lower():
            potential_time_bars.append(
                "The facts mention delay. This may raise limitation period concerns depending on the cause of action."
            )

        if "years" in case_description.lower() or "months" in case_description.lower():
            potential_time_bars.append(
                "Time duration is mentioned. Verify whether the period exceeds limitation thresholds under applicable law."
            )

        recommended_actions.extend(
            [
                "Identify the exact cause of action date.",
                "Check the applicable Limitation Act / statute relevant to the dispute.",
                "Confirm if any exception applies (e.g., fraud discovery, continuing cause, disability).",
                "If delay exists, evaluate whether condonation of delay can be requested (if legally permissible).",
            ]
        )

        if document_type:
            recommended_actions.append(
                f"Ensure the limitation considerations are addressed explicitly in the {document_type}."
            )

        return {
            "limitation_summary": limitation_summary,
            "potential_time_bars": potential_time_bars,
            "recommended_actions": recommended_actions,
        }
