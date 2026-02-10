"""
LAF Agent Tests (Legal Analysis & Findings Agent)

These tests validate that the LAF agent:
- performs issue-focused legal analysis
- identifies findings and considerations
- highlights risks and uncertainties
- avoids drafting arguments or giving legal advice
- produces structured, deterministic output

The tests are model-agnostic and CI-safe.
"""

from __future__ import annotations

from typing import Dict

import pytest


# ---------------------------------------------------------------------
# Mock LAF Agent (replace with real import when wired)
# ---------------------------------------------------------------------

try:
    from src.agents.laf_agent import LAFAgent  # type: ignore
except ImportError:
    LAFAgent = None


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------

@pytest.fixture
def laf_agent():
    if LAFAgent is None:
        pytest.skip("LAFAgent not implemented yet")
    return LAFAgent()


@pytest.fixture
def valid_analysis_request() -> Dict:
    return {
        "issue": "Whether delay can be condoned under Section 14 of the Limitation Act.",
        "facts": (
            "The petitioner pursued a remedy before a forum that "
            "was later found to lack jurisdiction."
        ),
        "research_points": [
            "Section 14 requires due diligence and good faith.",
            "Courts interpret Section 14 liberally in appropriate cases.",
        ],
    }


@pytest.fixture
def minimal_analysis_request() -> Dict:
    return {
        "issue": "Applicability of Section 14 of the Limitation Act.",
        "facts": "",
        "research_points": [],
    }


# ---------------------------------------------------------------------
# Core Analysis Tests
# ---------------------------------------------------------------------

def test_analysis_is_generated(laf_agent, valid_analysis_request):
    report = laf_agent.analyze(**valid_analysis_request)

    assert isinstance(report, dict)
    assert len(report) > 0


def test_analysis_contains_required_sections(laf_agent, valid_analysis_request):
    report = laf_agent.analyze(**valid_analysis_request)

    required_fields = {
        "analysis",
        "key_findings",
        "risk_factors",
        "preliminary_conclusion",
    }

    for field in required_fields:
        assert field in report


def test_analysis_addresses_the_issue(laf_agent, valid_analysis_request):
    report = laf_agent.analyze(**valid_analysis_request)

    issue = valid_analysis_request["issue"].lower()
    combined_text = (
        report.get("analysis", "") +
        report.get("preliminary_conclusion", "")
    ).lower()

    assert any(word in combined_text for word in issue.split()[:3])


# ---------------------------------------------------------------------
# Findings & Risk Awareness
# ---------------------------------------------------------------------

def test_findings_are_listed(laf_agent, valid_analysis_request):
    report = laf_agent.analyze(**valid_analysis_request)

    assert isinstance(report["key_findings"], list)
    assert len(report["key_findings"]) > 0


def test_risk_factors_are_identified(laf_agent, valid_analysis_request):
    report = laf_agent.analyze(**valid_analysis_request)

    assert isinstance(report["risk_factors"], list)


# ---------------------------------------------------------------------
# Safety & Scope Control
# ---------------------------------------------------------------------

def test_analysis_avoids_direct_legal_advice(laf_agent, valid_analysis_request):
    report = laf_agent.analyze(**valid_analysis_request)

    combined_text = " ".join(
        [report.get("analysis", ""), report.get("preliminary_conclusion", "")]
    ).lower()

    unsafe_phrases = [
        "you should file",
        "you must file",
        "it is mandatory to",
        "immediately file",
        "guarantees success",
    ]

    for phrase in unsafe_phrases:
        assert phrase not in combined_text


def test_analysis_uses_cautious_language(laf_agent, valid_analysis_request):
    report = laf_agent.analyze(**valid_analysis_request)

    text = report.get("preliminary_conclusion", "").lower()
    assert any(
        phrase in text
        for phrase in ["may", "depending on", "subject to", "likely"]
    )


def test_analysis_avoids_absolute_claims(laf_agent, valid_analysis_request):
    report = laf_agent.analyze(**valid_analysis_request)

    combined_text = " ".join(report.values()).lower()

    absolute_phrases = [
        "always applies",
        "never applies",
        "no exception",
        "guarantees",
    ]

    for phrase in absolute_phrases:
        assert phrase not in combined_text


# ---------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------

def test_minimal_input_is_handled_gracefully(laf_agent, minimal_analysis_request):
    report = laf_agent.analyze(**minimal_analysis_request)

    assert isinstance(report, dict)
    assert "analysis" in report


def test_empty_issue_is_handled_safely(laf_agent):
    report = laf_agent.analyze(
        issue="",
        facts="",
        research_points=[],
    )

    assert isinstance(report, dict)
    assert "analysis" in report


# ---------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------

def test_analysis_is_deterministic(laf_agent, valid_analysis_request):
    report_1 = laf_agent.analyze(**valid_analysis_request)
    report_2 = laf_agent.analyze(**valid_analysis_request)

    assert report_1 == report_2
