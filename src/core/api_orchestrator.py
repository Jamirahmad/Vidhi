"""API-facing orchestration adapter.

Keeps FastAPI route dependencies stable even if the main
`src.core.orchestrator` implementation evolves.
"""

from __future__ import annotations

from typing import Any

from src.agents.lra_legal_research_agent import LRALegalResearchAgent


class Orchestrator:
    """Minimal adapter used by API routes."""

    def __init__(self) -> None:
        self._research_agent = LRALegalResearchAgent()

    def run_research(
        self,
        *,
        case_context: str,
        jurisdiction: str,
        case_type: str,
        user_constraints: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        agent_result = self._research_agent.run(
            {
                "case_description": case_context,
                "jurisdiction": jurisdiction,
                "issues": [case_type] if case_type else [],
                "constraints": user_constraints or {},
            }
        )

        data = agent_result.get("data", {})

        return {
            "status": agent_result.get("status", "FAILED"),
            "summary": data.get("summary", ""),
            "issues": [case_type] if case_type else [],
            "precedents": [
                {"title": item, "citation": "Unverified", "court": jurisdiction}
                for item in data.get("case_laws", [])
            ],
            "requires_human_review": True,
        }
