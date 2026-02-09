"""
System-wide Constants

This module defines enums, string literals, and shared constants
used across Vidhi to avoid magic values and semantic drift.
"""

from enum import Enum
from typing import Final


# ============================================================
# Agent & Workflow Status
# ============================================================

class AgentResultStatus(str, Enum):
    """
    Standardized agent execution outcomes.
    """

    SUCCESS = "SUCCESS"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    UNCERTAIN = "UNCERTAIN"


class WorkflowStatus(str, Enum):
    """
    High-level workflow execution states.
    """

    SUCCESS = "SUCCESS"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    FAILED = "FAILED"
    ESCALATED = "ESCALATED"


# ============================================================
# Agent Names (single source of truth)
# ============================================================

AGENT_LRA: Final[str] = "LRA_LEGAL_RESEARCH_AGENT"
AGENT_CLSA: Final[str] = "CLSA_CASE_LAW_SEARCH_AGENT"
AGENT_LII: Final[str] = "LII_ISSUE_IDENTIFIER_AGENT"
AGENT_LAA: Final[str] = "LAA_LIMITATION_ANALYSIS_AGENT"
AGENT_LAB: Final[str] = "LAB_ARGUMENT_BUILDER_AGENT"
AGENT_DGA: Final[str] = "DGA_DOCUMENT_GENERATION_AGENT"
AGENT_CCA: Final[str] = "CCA_COMPLIANCE_CHECK_AGENT"
AGENT_LAF: Final[str] = "LAF_LEGAL_AID_FINDER_AGENT"


# Ordered agent execution flow (used by orchestrator & graph)
AGENT_EXECUTION_ORDER: Final[list[str]] = [
    AGENT_LRA,
    AGENT_CLSA,
    AGENT_LII,
    AGENT_LAA,
    AGENT_LAB,
    AGENT_DGA,
    AGENT_CCA,
    AGENT_LAF,
]


# ============================================================
# API / Request Context
# ============================================================

DEFAULT_JURISDICTION: Final[str] = "India"
DEFAULT_LANGUAGE: Final[str] = "en"
DEFAULT_TONE: Final[str] = "formal"


# ============================================================
# Compliance & Safety
# ============================================================

COMPLIANCE_CHECK_TYPES: Final[list[str]] = [
    "hallucination",
    "citation_accuracy",
    "ethical_risk",
    "jurisdiction_mismatch",
]

MAX_DOCUMENT_LENGTH_CHARS: Final[int] = 50_000


# ============================================================
# Logging & Tracing
# ============================================================

TRACE_ID_HEADER: Final[str] = "X-Trace-Id"
REQUEST_ID_HEADER: Final[str] = "X-Request-Id"

AGENT_TRACE_LOG_FILE: Final[str] = "logs/agent_traces.log"
APP_LOG_FILE: Final[str] = "logs/app.log"


# ============================================================
# Evaluation / Testing
# ============================================================

CONFIDENCE_THRESHOLD_LOW: Final[float] = 0.4
CONFIDENCE_THRESHOLD_HIGH: Final[float] = 0.75

HALLUCINATION_SEVERITY_HIGH: Final[str] = "HIGH"
HALLUCINATION_SEVERITY_MEDIUM: Final[str] = "MEDIUM"
HALLUCINATION_SEVERITY_LOW: Final[str] = "LOW"


# ============================================================
# Human-in-the-Loop
# ============================================================

HUMAN_REVIEW_REQUIRED_REASONS: Final[list[str]] = [
    "AGENT_FAILURE",
    "LOW_CONFIDENCE",
    "COMPLIANCE_VIOLATION",
    "ETHICAL_RISK",
    "USER_REQUEST",
]


# ============================================================
# Misc
# ============================================================

UTF8_ENCODING: Final[str] = "utf-8"
