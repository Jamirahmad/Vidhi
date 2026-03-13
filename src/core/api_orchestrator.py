"""API-facing orchestration adapter."""

from __future__ import annotations

from typing import Any

from src.core.research_service import RAGResearchService


class Orchestrator:
    """Adapter used by API routes with real RAG-backed research flow."""

    def __init__(self) -> None:
        self._research_service = RAGResearchService()

    def run_research(
        self,
        *,
        case_context: str,
        jurisdiction: str,
        case_type: str,
        user_constraints: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self._research_service.run(
            case_context=case_context,
            jurisdiction=jurisdiction,
            case_type=case_type,
            constraints=user_constraints,
        )
