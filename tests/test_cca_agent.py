"""
CCA Agent Tests (Citation, Compliance, Consistency)

These tests validate that the CCA agent:
- detects missing citations
- flags unsupported legal claims
- avoids unsafe legal advice
- reports structured compliance metrics

The tests are model-agnostic and CI-safe.
"""

from __future__ import annotations

from typing import Dict, List

import pytest


# ---------------------------------------------------------------------
# Mock CCA Agent (replace with real import when wired)
# ---------------------------------------------------------------------

try:
    from src.agents.cca_agent import CCAAgent  # type: ignore
except ImportError:
    CCAAgent = None


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------

@pytest.fixture
def cca_agent():
    if CCAAgent is None:
        pytest.skip("CCAAgent not implemented yet")
    return CCAAgent()


@pytest.fixture
def compliant_content() -> Dict:
    return {
        "text": (
            "Section 14 of the Limitation Act permits exclusion of time "
            "spent in bona fide proceedings. In ABC Ltd vs Union of India, "
            "the Supreme Court observed that the provision should be "
            "construed liberally to advance justice."
        ),
        "citations": [
            {
                "id": "SCC-2019-123",
                "source": "ABC Ltd vs Union of India",
            }
        ],
        "content_type": "Argument Draft",
    }


@pytest.fixture
def non_compliant_content() -> Dict:
    return {
        "text": (
            "Section 14 always applies and guarantees condonation of delay. "
            "You should immediately file an application to get relief."
        ),
        "citations": [],
        "content_type": "Argument Draft",
    }


# ---------------------------------------------------------------------
# Core Compliance Tests
# ---------------------------------------------------------------------

def test_compliant_content_passes_checks(cca_agent, compliant_content):
    report = cca_agent.evaluate(
        text=compliant_content["text"],
        citations=compliant_content["citations"],
        content_type=compliant_content["content_type"],
    )

    assert report["citation_coverage"] >= 0.5
    assert report["hallucination_risk"] == "low"
    assert report["advisory_risk"] == "low"
    assert report["overall_status"] in {"pass", "review"}


def test_missing_citations_are_flagged(cca_agent, non_compliant_content):
    report = cca_agent.evaluate(
        text=non_compliant_content["text"],
        citations=non_compliant_content["citations"],
        content_type=non_compliant_content["content_type"],
    )

    assert report["citation_coverage"] == 0.0
    assert report["overall_status"] == "fail"


def test_absolute_claims_increase_hallucination_risk(cca_agent):
    text = (
        "This provision always applies and has no exceptions under law."
    )

    report = cca_agent.evaluate(
        text=text,
        citations=[],
        content_type="Argument Draft",
    )

    assert report["hallucination_risk"] in {"medium", "high"}


def test_direct_legal_advice_is_flagged(cca_agent):
    text = (
        "You should file a writ petition immediately to obtain relief."
    )

    report = cca_agent.evaluate(
        text=text,
        citations=[],
        content_type="Legal Note",
    )

    assert report["advisory_risk"] == "high"
    assert report["overall_status"] == "fail"


# ---------------------------------------------------------------------
# Consistency & Structure
# ---------------------------------------------------------------------

def test_empty_content_fails_validation(cca_agent):
    report = cca_agent.evaluate(
        text="",
        citations=[],
        content_type="Argument Draft",
    )

    assert report["overall_status"] == "fail"
    assert "errors" in report


def test_report_contains_required_fields(cca_agent, compliant_content):
    report = cca_agent.evaluate(
        text=compliant_content["text"],
        citations=compliant_content["citations"],
        content_type=compliant_content["content_type"],
    )

    required_fields = {
        "citation_coverage",
        "hallucination_risk",
        "advisory_risk",
        "overall_status",
    }

    for field in required_fields:
        assert field in report
