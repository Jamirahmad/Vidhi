"""
Common Schemas

This module defines shared, canonical schemas used across agents,
validation layers, retrieval, and orchestration.

All schemas are intentionally lightweight and dict-compatible.
"""

# src/common/schemas.py

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from uuid import uuid4


# -----------------------------------------------------------------------------
# Helper
# -----------------------------------------------------------------------------
def _safe_str(val: Any) -> str:
    if val is None:
        return ""
    return str(val)


# -----------------------------------------------------------------------------
# Agent Execution Result
# -----------------------------------------------------------------------------
@dataclass
class AgentExecutionResult:
    """
    Captures execution results for each agent in the orchestration pipeline.
    """

    agent_name: str
    success: bool
    output: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    execution_time_sec: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "success": self.success,
            "output": self.output or {},
            "error": self.error,
            "execution_time_sec": float(self.execution_time_sec),
        }


# -----------------------------------------------------------------------------
# Orchestrator Request
# -----------------------------------------------------------------------------
@dataclass
class OrchestratorRequest:
    """
    Standard request structure passed into the orchestrator.

    This is the ONLY schema the orchestrator should accept.
    """

    request_id: str
    user_query: str

    # Optional fields
    jurisdiction: str = ""
    document_type: str = ""
    user_profile: Dict[str, Any] = field(default_factory=dict)

    # Optional extra context / metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def from_dict(payload: Dict[str, Any]) -> "OrchestratorRequest":
        if not isinstance(payload, dict):
            raise ValueError("OrchestratorRequest expects dict payload")

        request_id = payload.get("request_id") or str(uuid4())
        user_query = payload.get("user_query") or payload.get("query") or payload.get("question")

        if not user_query or not str(user_query).strip():
            raise ValueError("Missing required field: user_query")

        return OrchestratorRequest(
            request_id=_safe_str(request_id),
            user_query=_safe_str(user_query).strip(),
            jurisdiction=_safe_str(payload.get("jurisdiction")),
            document_type=_safe_str(payload.get("document_type")),
            user_profile=payload.get("user_profile") or {},
            metadata=payload.get("metadata") or {},
        )

    def to_context_dict(self) -> Dict[str, Any]:
        """
        Converts orchestrator request into context dict that can be passed to agents.
        """
        return {
            "request_id": self.request_id,
            "user_query": self.user_query,
            "jurisdiction": self.jurisdiction,
            "document_type": self.document_type,
            "user_profile": self.user_profile,
            "metadata": self.metadata,
        }

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# -----------------------------------------------------------------------------
# Orchestrator Response
# -----------------------------------------------------------------------------
@dataclass
class OrchestratorResponse:
    """
    Standard orchestrator response returned to API/UI.

    This schema ensures output consistency across all pipelines.
    """

    success: bool
    message: str

    # final structured output from pipeline
    output: Dict[str, Any] = field(default_factory=dict)

    # final textual answer (if produced)
    final_answer: str = ""

    # validation outputs
    citation_validation: Optional[Dict[str, Any]] = None
    hallucination_validation: Optional[Dict[str, Any]] = None

    # agent execution trace
    agent_results: List[AgentExecutionResult] = field(default_factory=list)

    # error string if failed
    error: Optional[str] = None

    # execution metrics
    execution_time_sec: float = 0.0

    @staticmethod
    def success_response(
        message: str,
        output: Dict[str, Any],
        final_answer: str = "",
        agent_results: Optional[List[AgentExecutionResult]] = None,
        citation_validation: Optional[Dict[str, Any]] = None,
        hallucination_validation: Optional[Dict[str, Any]] = None,
        execution_time_sec: float = 0.0,
    ) -> "OrchestratorResponse":
        return OrchestratorResponse(
            success=True,
            message=message,
            output=output or {},
            final_answer=final_answer or "",
            agent_results=agent_results or [],
            citation_validation=citation_validation,
            hallucination_validation=hallucination_validation,
            error=None,
            execution_time_sec=float(execution_time_sec),
        )

    @staticmethod
    def error_response(
        message: str,
        error: str,
        agent_results: Optional[List[AgentExecutionResult]] = None,
        execution_time_sec: float = 0.0,
    ) -> "OrchestratorResponse":
        return OrchestratorResponse(
            success=False,
            message=message,
            output={},
            final_answer="",
            agent_results=agent_results or [],
            citation_validation=None,
            hallucination_validation=None,
            error=error,
            execution_time_sec=float(execution_time_sec),
        )

    # Backward compatible aliases for orchestrator code usage
    @staticmethod
    def success(
        message: str,
        output: Dict[str, Any],
        final_answer: str = "",
        agent_results: Optional[List[AgentExecutionResult]] = None,
        citation_validation: Optional[Dict[str, Any]] = None,
        hallucination_validation: Optional[Dict[str, Any]] = None,
        execution_time_sec: float = 0.0,
    ) -> "OrchestratorResponse":
        return OrchestratorResponse.success_response(
            message=message,
            output=output,
            final_answer=final_answer,
            agent_results=agent_results,
            citation_validation=citation_validation,
            hallucination_validation=hallucination_validation,
            execution_time_sec=execution_time_sec,
        )

    @staticmethod
    def error(
        message: str,
        error: str,
        agent_results: Optional[List[AgentExecutionResult]] = None,
        execution_time_sec: float = 0.0,
    ) -> "OrchestratorResponse":
        return OrchestratorResponse.error_response(
            message=message,
            error=error,
            agent_results=agent_results,
            execution_time_sec=execution_time_sec,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "message": self.message,
            "output": self.output or {},
            "final_answer": self.final_answer,
            "citation_validation": self.citation_validation,
            "hallucination_validation": self.hallucination_validation,
            "agent_results": [a.to_dict() for a in self.agent_results],
            "error": self.error,
            "execution_time_sec": float(self.execution_time_sec),
        }
