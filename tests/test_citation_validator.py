"""
Citation Validator Tests

These tests validate that the citation validation logic:
- detects missing citations
- matches citations to claims
- flags orphan citations
- reports coverage metrics
- remains deterministic and model-agnostic
"""

from __future__ import annotations

from typing import Dict, List

import pytest


# ---------------------------------------------------------------------
# Mock Citation Validator (replace with real import when wired)
# ---------------------------------------------------------------------

try:
    from src.validation.citation_validator import CitationValidator  # type: ignore
except ImportError:
    CitationValidator = None


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------

@pytest.fixture
def validator():
    if CitationValidator is None:
        pytest.skip("CitationValidator not implemented yet")
    return CitationValidator()


@pytest.fixture
def well_cited_text() -> Dict:
    return {
        "text": (
            "Section 14 of the Limitation Act permits exclusion of time "
            "spent in bona fide proceedings. In ABC Ltd vs Union of India, "
            "the Supreme Court interpreted this provision liberally."
        ),
        "citations": [
            {
                "id": "SCC-2019-123",
                "reference": "ABC Ltd vs Union of India",
            }
        ],
    }


@pytest.fixture
def missing_citation_text() -> Dict:
    return {
        "text": (
            "Section 14 always applies and guarantees exclusion of delay "
            "in all circumstances."
        ),
        "citations": [],
    }


@pytest.fixture
def orphan_citation_text() -> Dict:
    return {
        "text": (
            "The court discussed limitation principles without "
            "reference to specific precedent."
        ),
        "citations": [
            {
                "id": "AIR-2005-456",
                "reference": "XYZ vs State",
            }
        ],
    }


# ---------------------------------------------------------------------
# Core Validation Tests
# ---------------------------------------------------------------------

def test_well_cited_text_has_high_coverage(validator, well_cited_text):
    report = validator.validate(
        text=well_cited_text["text"],
        citations=well_cited_text["citations"],
    )

    assert report["coverage_score"] >= 0.5
    assert report["missing_citations"] == []
    assert report["orphan_citations"] == []


def test_missing_citations_are_detected(validator, missing_citation_text):
    report = validator.validate(
        text=missing_citation_text["text"],
        citations=missing_citation_text["citations"],
    )

    assert report["coverage_score"] == 0.0
    assert len(report["missing_citations"]) > 0


def test_orphan_citations_are_detected(validator, orphan_citation_text):
    report = validator.validate(
        text=orphan_citation_text["text"],
        citations=orphan_citation_text["citations"],
    )

    assert len(report["orphan_citations"]) == 1
    assert report["coverage_score"] < 1.0


# ---------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------

def test_empty_text_returns_zero_coverage(validator):
    report = validator.validate(text="", citations=[])

    assert report["coverage_score"] == 0.0
    assert report["missing_citations"] == []
    assert report["orphan_citations"] == []


def test_empty_citations_with_neutral_text(validator):
    text = "This section provides background information only."

    report = validator.validate(text=text, citations=[])

    assert report["coverage_score"] == 0.0


# ---------------------------------------------------------------------
# Report Structure
# ---------------------------------------------------------------------

def test_report_contains_required_fields(validator, well_cited_text):
    report = validator.validate(
        text=well_cited_text["text"],
        citations=well_cited_text["citations"],
    )

    required_fields = {
        "coverage_score",
        "missing_citations",
        "orphan_citations",
    }

    for field in required_fields:
        assert field in report
