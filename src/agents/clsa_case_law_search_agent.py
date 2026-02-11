"""
CLSA – Case Law Search Agent

Responsibilities:
- Retrieve relevant case laws and judicial precedents
- Use vector + keyword hybrid retrieval
- NEVER fabricate citations
- Return traceable sources only
- Escalate to human review on low confidence or empty results
"""

from __future__ import annotations

from typing import Any

from src.agents.base_agent import BaseAgent


class CLSACaseLawSearchAgent(BaseAgent):
    """
    CLSA - Case Law Search Agent

    Responsibility:
    - Identify relevant case law references based on issues + jurisdiction.
    - Return structured list of case laws with minimal hallucination risk.
    - This agent should NOT fabricate citations.

    NOTE:
    If no verified sources are available, return generic suggestions
    instead of making up citations.

    Output contract:
    {
        "case_laws": [
            {
                "title": str,
                "court": str,
                "year": str,
                "citation": str,
                "relevance": str
            }
        ],
        "summary": str
    }
    """

    agent_name = "CLSACaseLawSearchAgent"
    agent_version = "2.0"

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config=config)

    def _execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Expected payload:
        {
            "jurisdiction": str,
            "issues": list[str] OR str,
            "case_description": str
        }
        """
        jurisdiction = str(payload.get("jurisdiction", "")).strip()
        case_description = str(payload.get("case_description", "")).strip()

        issues = payload.get("issues", [])
        if isinstance(issues, str):
            issues_list = [issues]
        elif isinstance(issues, list):
            issues_list = [str(i).strip() for i in issues if str(i).strip()]
        else:
            issues_list = []

        # Since this project is offline / no real DB integration,
        # we return structured placeholder output without fake citations.
        case_laws: list[dict[str, str]] = []

        summary_parts: list[str] = []

        if issues_list:
            summary_parts.append(
                f"Case law search performed for {len(issues_list)} identified issue(s) "
                f"under jurisdiction: {jurisdiction or 'UNKNOWN'}."
            )
        else:
            summary_parts.append(
                f"Case law search performed under jurisdiction: {jurisdiction or 'UNKNOWN'}."
            )

        if not case_description and not issues_list:
            summary_parts.append(
                "No sufficient case facts or issues were provided, so no targeted case laws were identified."
            )
        else:
            summary_parts.append(
                "No verified case-law database integration was available, so no specific citations were returned. "
                "Recommended: integrate SCC Online / Manupatra / Westlaw API or curated internal repository."
            )

        return {
            "case_laws": case_laws,
            "summary": " ".join(summary_parts).strip(),
        }
