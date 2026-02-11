# src/common/exceptions.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


class VidhiError(Exception):
    """
    Base exception for the Vidhi application.
    All custom exceptions should inherit from this.
    """

    def __init__(
        self,
        message: str,
        *,
        error_code: str = "VIDHI_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": True,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
        }


# -----------------------------
# Config / Setup Errors
# -----------------------------
class ConfigError(VidhiError):
    def __init__(self, message: str, *, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, error_code="CONFIG_ERROR", details=details)


# -----------------------------
# Agent Errors
# -----------------------------
class AgentError(VidhiError):
    def __init__(
        self,
        message: str,
        *,
        agent_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        if details is None:
            details = {}
        if agent_name:
            details["agent_name"] = agent_name

        super().__init__(message, error_code="AGENT_ERROR", details=details)


class AgentExecutionError(AgentError):
    def __init__(
        self,
        message: str,
        *,
        agent_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, agent_name=agent_name, details=details)
        self.error_code = "AGENT_EXECUTION_ERROR"


class AgentContractError(AgentError):
    """
    Raised when an agent returns output that violates the contract,
    e.g. not returning a dict, missing keys, wrong types, etc.
    """

    def __init__(
        self,
        message: str,
        *,
        agent_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, agent_name=agent_name, details=details)
        self.error_code = "AGENT_CONTRACT_ERROR"


# -----------------------------
# Validation Errors
# -----------------------------
class ValidationError(VidhiError):
    def __init__(self, message: str, *, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, error_code="VALIDATION_ERROR", details=details)


class CitationValidationError(ValidationError):
    def __init__(self, message: str, *, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, details=details)
        self.error_code = "CITATION_VALIDATION_ERROR"


class HallucinationValidationError(ValidationError):
    def __init__(self, message: str, *, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, details=details)
        self.error_code = "HALLUCINATION_VALIDATION_ERROR"


# -----------------------------
# Orchestrator Errors
# -----------------------------
class OrchestratorError(VidhiError):
    def __init__(self, message: str, *, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, error_code="ORCHESTRATOR_ERROR", details=details)


class OrchestratorTimeoutError(OrchestratorError):
    def __init__(self, message: str, *, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, details=details)
        self.error_code = "ORCHESTRATOR_TIMEOUT_ERROR"


class OrchestratorGuardrailError(OrchestratorError):
    def __init__(self, message: str, *, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, details=details)
        self.error_code = "ORCHESTRATOR_GUARDRAIL_ERROR"


# -----------------------------
# External / Dependency Errors
# -----------------------------
class ExternalServiceError(VidhiError):
    def __init__(
        self,
        message: str,
        *,
        service_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        if details is None:
            details = {}
        if service_name:
            details["service_name"] = service_name

        super().__init__(message, error_code="EXTERNAL_SERVICE_ERROR", details=details)


# -----------------------------
# Utility
# -----------------------------
def safe_exception_dict(ex: Exception) -> Dict[str, Any]:
    """
    Converts exceptions into a consistent dict output for API responses.
    Ensures that unknown exceptions don't crash serialization.
    """
    if isinstance(ex, VidhiError):
        return ex.to_dict()

    return {
        "error": True,
        "error_code": "UNKNOWN_ERROR",
        "message": str(ex),
        "details": {},
    }
