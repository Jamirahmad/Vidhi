# src/common/exceptions.py

from __future__ import annotations

from typing import Any, Optional


class VidhiError(Exception):
    """
    Base exception class for the Vidhi application.
    All custom exceptions should inherit from this.
    """

    def __init__(
        self,
        message: str,
        *,
        error_code: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.metadata = metadata or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "metadata": self.metadata,
        }


class ConfigError(VidhiError):
    """Raised when configuration is missing or invalid."""


class AgentExecutionError(VidhiError):
    """
    Raised when an agent fails to execute successfully.
    Useful for orchestration layer to capture agent-specific failures.
    """

    def __init__(
        self,
        agent_name: str,
        message: str,
        *,
        error_code: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        original_exception: Optional[Exception] = None,
    ):
        super().__init__(
            message=message,
            error_code=error_code or "AGENT_EXECUTION_FAILED",
            metadata=metadata,
        )
        self.agent_name = agent_name
        self.original_exception = original_exception

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["agent_name"] = self.agent_name
        if self.original_exception:
            data["original_exception"] = str(self.original_exception)
        return data


class ValidationError(VidhiError):
    """Raised when validation of an agent output or pipeline step fails."""


class CitationValidationError(ValidationError):
    """Raised when citation validation fails."""


class HallucinationDetectedError(ValidationError):
    """Raised when hallucination detector identifies high-risk hallucination."""


class SafetyGuardrailViolationError(VidhiError):
    """
    Raised when the safety guardrails block a request or output.
    """

    def __init__(
        self,
        message: str,
        *,
        violation_type: str = "UNKNOWN",
        error_code: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code=error_code or "SAFETY_GUARDRAIL_VIOLATION",
            metadata=metadata,
        )
        self.violation_type = violation_type

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["violation_type"] = self.violation_type
        return data


class PipelineError(VidhiError):
    """
    Raised when the orchestrator fails in a non-agent specific manner.
    Example: missing pipeline step, broken state, corrupted output.
    """


class ExternalServiceError(VidhiError):
    """
    Raised when external dependencies fail (OpenAI API, ChromaDB, filesystem, etc.)
    """


class DataNotFoundError(VidhiError):
    """Raised when expected case law / statute / document data is missing."""


class UnsupportedJurisdictionError(VidhiError):
    """Raised when user requests a jurisdiction not supported by the system."""


class UnsupportedDocumentTypeError(VidhiError):
    """Raised when user requests a document type not supported by the system."""
