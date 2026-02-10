"""
Common Schemas

This module defines shared, canonical schemas used across agents,
validation layers, retrieval, and orchestration.

All schemas are intentionally lightweight and dict-compatible.
"""

from __future__ import annotations

from typing import Dict, List, TypedDict, Literal


# ---------------------------------------------------------------------
# Issue Identification
# ---------------------------------------------------------------------

class IssueReport(TypedDict):
    primary_issues: List[str]
    secondary_issues: List[str]


# ---------------------------------------------------------------------
# Legal Research
# ---------------------------------------------------------------------

class ResearchReport(TypedDict):
    authorities: List[str]
    statutes: List[str]
    key_principles: List[str]


# ---------------------------------------------------------------------
# Legal Analysis & Findings
# ---------------------------------------------------------------------

class AnalysisReport(TypedDict):
    analysis: str
    key_findings: List[str]
    risk_factors: List[str]
    preliminary_conclusion: str


# ---------------------------------------------------------------------
# Argument Construction
# ---------------------------------------------------------------------

class ArgumentReport(TypedDict):
    text: str
    citations: List[str]


# ---------------------------------------------------------------------
# Quality Review (CLSA)
# ---------------------------------------------------------------------

QualityRating = Literal["excellent", "good", "fair", "poor", "unknown"]

class QualityReport(TypedDict):
    overall_rating: QualityRating
    issues: List[str]
    suggestions: List[str]


# ---------------------------------------------------------------------
# Compliance & Safety (CCA)
# ---------------------------------------------------------------------

ComplianceStatus = Literal["pass", "fail", "unknown"]

class ComplianceReport(TypedDict):
    overall_status: ComplianceStatus
    violations: List[str]
    notes: List[str]


# ---------------------------------------------------------------------
# Hallucination Risk
# ---------------------------------------------------------------------

RiskLevel = Literal["low", "medium", "high"]

class HallucinationReport(TypedDict):
    risk_level: RiskLevel
    risk_score: float
    signals: List[str]


# ---------------------------------------------------------------------
# Citation Validation
# ---------------------------------------------------------------------

class CitationValidationReport(TypedDict):
    is_valid: bool
    missing_citations: List[str]
    issues: List[str]


# ---------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------

class RetrievedDocument(TypedDict):
    id: str
    text: str
    score: float
    metadata: Dict


# ---------------------------------------------------------------------
# Orchestrator Output
# ---------------------------------------------------------------------

class OrchestratorResult(TypedDict):
    issues: IssueReport
    research: ResearchReport
    analysis: AnalysisReport
    argument: str
    quality_report: QualityReport
    compliance_report: ComplianceReport
    final_document: str


# ---------------------------------------------------------------------
# Public exports
# ---------------------------------------------------------------------

__all__ = [
    "IssueReport",
    "ResearchReport",
    "AnalysisReport",
    "ArgumentReport",
    "QualityReport",
    "ComplianceReport",
    "HallucinationReport",
    "CitationValidationReport",
    "RetrievedDocument",
    "OrchestratorResult",
]
