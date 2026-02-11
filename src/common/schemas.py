"""
Common Schemas

This module defines shared, canonical schemas used across agents,
validation layers, retrieval, and orchestration.

All schemas are intentionally lightweight and dict-compatible.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


# -------------------------------------------------------------------------
# Pipeline Request / Response
# -------------------------------------------------------------------------
@dataclass
class PipelineRequest:
    """
    Input request schema for the Vidhi pipeline.
    """

    request_id: str
    case_description: str
    jurisdiction: str
    document_type: str


@dataclass
class PipelineResponse:
    """
    Output schema for Vidhi pipeline.

    This is the main object returned by orchestrator.
    """

    request_id: str
    status: str  # IN_PROGRESS / SUCCESS / PARTIAL_SUCCESS / FAILED

    issues: Optional["LegalIssuesOutput"] = None
    research: Optional["LegalResearchOutput"] = None
    analysis: Optional["LegalAnalysisOutput"] = None
    arguments: Optional["LegalArgumentsOutput"] = None
    compliance: Optional["ComplianceCheckOutput"] = None
    draft: Optional["DocumentDraftOutput"] = None

    validations: dict[str, Any] = field(default_factory=dict)
    errors: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


# -------------------------------------------------------------------------
# Agent Output Schemas
# -------------------------------------------------------------------------
@dataclass
class LegalIssuesOutput:
    """
    Output schema for LII Agent (Legal Issue Identification).
    """

    primary_issues: list[str] = field(default_factory=list)
    secondary_issues: list[str] = field(default_factory=list)
    summary: str = ""


@dataclass
class LegalResearchOutput:
    """
    Output schema for LRA Agent (Legal Research).
    """

    statutes: list[str] = field(default_factory=list)
    case_laws: list[str] = field(default_factory=list)
    summary: str = ""


@dataclass
class LegalAnalysisOutput:
    """
    Output schema for LAF Agent (Legal Analysis).
    """

    analysis_text: str = ""
    risk_assessment: str = ""  # LOW / MEDIUM / HIGH
    key_findings: list[str] = field(default_factory=list)


@dataclass
class LegalArgumentsOutput:
    """
    Output schema for LAB Agent (Legal Arguments Builder).
    """

    arguments_text: str = ""
    pro_arguments: list[str] = field(default_factory=list)
    counter_arguments: list[str] = field(default_factory=list)


@dataclass
class ComplianceCheckOutput:
    """
    Output schema for CLSA Agent (Compliance and Safety Agent).

    This schema is important because orchestrator uses it as a hard gate.
    """

    can_generate_draft: bool = True
    notes: str = ""

    disclaimer_required: bool = False
    disclaimer_text: str = ""

    flagged_risks: list[str] = field(default_factory=list)


@dataclass
class DocumentDraftOutput:
    """
    Output schema for DGA Agent (Document Generator).
    """

    draft_text: str
    format: str = "text"  # text / markdown / pdf-ready etc.
    metadata: dict[str, Any] = field(default_factory=dict)


# -------------------------------------------------------------------------
# Validation Schemas
# -------------------------------------------------------------------------
@dataclass
class CitationValidationResult:
    """
    Output schema for Citation Validator.

    Citation validator must always return this consistent structure.
    """

    passed: bool
    citation_count: int
    citations_found: list[str] = field(default_factory=list)
    suspicious_citations: list[str] = field(default_factory=list)
    message: str = ""


@dataclass
class HallucinationDetectionResult:
    """
    Output schema for Hallucination Detector.

    hallucination_risk values:
    - LOW
    - MEDIUM
    - HIGH
    """

    hallucination_risk: str
    score: float
    reasons: list[str] = field(default_factory=list)
    flagged_segments: list[str] = field(default_factory=list)
