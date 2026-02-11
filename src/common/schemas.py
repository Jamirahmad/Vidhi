"""
Common Schemas

This module defines shared, canonical schemas used across agents,
validation layers, retrieval, and orchestration.

All schemas are intentionally lightweight and dict-compatible.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Optional


def _safe_list(value: Any) -> list:
    """Convert value into a safe list."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _safe_str(value: Any, default: str = "") -> str:
    """Convert value into safe string."""
    if value is None:
        return default
    return str(value).strip()


@dataclass
class AgentError:
    agent: str
    error: str
    stage: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class IssuesOutput:
    """
    Output schema for LII Agent (Legal Issue Identifier).
    """

    primary_issues: list[str] = field(default_factory=list)
    secondary_issues: list[str] = field(default_factory=list)

    def normalize(self) -> "IssuesOutput":
        self.primary_issues = [_safe_str(x) for x in _safe_list(self.primary_issues)]
        self.secondary_issues = [_safe_str(x) for x in _safe_list(self.secondary_issues)]
        self.primary_issues = [x for x in self.primary_issues if x]
        self.secondary_issues = [x for x in self.secondary_issues if x]
        return self

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ResearchOutput:
    """
    Output schema for LRA Agent (Legal Research Agent).
    """

    statutes: list[str] = field(default_factory=list)
    case_laws: list[str] = field(default_factory=list)
    legal_principles: list[str] = field(default_factory=list)
    notes: str = ""

    def normalize(self) -> "ResearchOutput":
        self.statutes = [_safe_str(x) for x in _safe_list(self.statutes)]
        self.case_laws = [_safe_str(x) for x in _safe_list(self.case_laws)]
        self.legal_principles = [_safe_str(x) for x in _safe_list(self.legal_principles)]
        self.notes = _safe_str(self.notes)

        self.statutes = [x for x in self.statutes if x]
        self.case_laws = [x for x in self.case_laws if x]
        self.legal_principles = [x for x in self.legal_principles if x]
        return self

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AnalysisOutput:
    """
    Output schema for LAF Agent (Legal Analysis Framework Agent).
    """

    arguments_for: list[str] = field(default_factory=list)
    arguments_against: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    remedies: list[str] = field(default_factory=list)
    conclusion: str = ""

    def normalize(self) -> "AnalysisOutput":
        self.arguments_for = [_safe_str(x) for x in _safe_list(self.arguments_for)]
        self.arguments_against = [_safe_str(x) for x in _safe_list(self.arguments_against)]
        self.risks = [_safe_str(x) for x in _safe_list(self.risks)]
        self.remedies = [_safe_str(x) for x in _safe_list(self.remedies)]
        self.conclusion = _safe_str(self.conclusion)

        self.arguments_for = [x for x in self.arguments_for if x]
        self.arguments_against = [x for x in self.arguments_against if x]
        self.risks = [x for x in self.risks if x]
        self.remedies = [x for x in self.remedies if x]
        return self

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ArgumentBuilderOutput:
    """
    Output schema for LAB Agent (Legal Argument Builder).
    """

    final_arguments: list[str] = field(default_factory=list)
    supporting_points: list[str] = field(default_factory=list)

    def normalize(self) -> "ArgumentBuilderOutput":
        self.final_arguments = [_safe_str(x) for x in _safe_list(self.final_arguments)]
        self.supporting_points = [_safe_str(x) for x in _safe_list(self.supporting_points)]

        self.final_arguments = [x for x in self.final_arguments if x]
        self.supporting_points = [x for x in self.supporting_points if x]
        return self

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CitationCheckOutput:
    """
    Output schema for CLSA Agent (Citation and Legal Source Analyzer).
    """

    citations_found: list[str] = field(default_factory=list)
    missing_citations: list[str] = field(default_factory=list)
    citation_quality_notes: str = ""

    def normalize(self) -> "CitationCheckOutput":
        self.citations_found = [_safe_str(x) for x in _safe_list(self.citations_found)]
        self.missing_citations = [_safe_str(x) for x in _safe_list(self.missing_citations)]
        self.citation_quality_notes = _safe_str(self.citation_quality_notes)

        self.citations_found = [x for x in self.citations_found if x]
        self.missing_citations = [x for x in self.missing_citations if x]
        return self

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ComplianceOutput:
    """
    Output schema for CCA Agent (Compliance & Caution Agent).
    """

    disclaimer: str = ""
    compliance_warnings: list[str] = field(default_factory=list)
    restricted_content_detected: bool = False

    def normalize(self) -> "ComplianceOutput":
        self.disclaimer = _safe_str(self.disclaimer)
        self.compliance_warnings = [_safe_str(x) for x in _safe_list(self.compliance_warnings)]
        self.compliance_warnings = [x for x in self.compliance_warnings if x]
        self.restricted_content_detected = bool(self.restricted_content_detected)
        return self

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DocumentDraftOutput:
    """
    Output schema for DGA Agent (Document Generation Agent).
    """

    title: str = ""
    document_body: str = ""
    references: list[str] = field(default_factory=list)

    def normalize(self) -> "DocumentDraftOutput":
        self.title = _safe_str(self.title)
        self.document_body = _safe_str(self.document_body)
        self.references = [_safe_str(x) for x in _safe_list(self.references)]
        self.references = [x for x in self.references if x]
        return self

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PipelineResponse:
    """
    Unified output schema from the orchestrator.

    This should be the ONLY response object returned to the caller layer.
    """

    request_id: str = ""
    jurisdiction: str = ""
    document_type: str = ""
    case_description: str = ""

    issues: dict[str, Any] = field(default_factory=dict)
    research: dict[str, Any] = field(default_factory=dict)
    analysis: dict[str, Any] = field(default_factory=dict)
    arguments: dict[str, Any] = field(default_factory=dict)
    citations: dict[str, Any] = field(default_factory=dict)
    compliance: dict[str, Any] = field(default_factory=dict)
    draft: dict[str, Any] = field(default_factory=dict)

    errors: list[dict[str, Any]] = field(default_factory=list)

    def add_error(self, agent: str, error: str, stage: Optional[str] = None) -> None:
        self.errors.append(
            AgentError(agent=agent, error=error, stage=stage).to_dict()
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
