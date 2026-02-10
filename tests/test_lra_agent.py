"""
LRA Agent Tests (Legal Research Agent)

These tests validate that the Legal Research Agent:
- performs issue-driven legal research
- returns relevant authorities and references
- structures research output clearly
- avoids legal conclusions or advice
- behaves deterministically and safely

The tests are model-agnostic and CI-safe.
"""

from __future__ import annotations

from typing import Dict, List

import pytest


# ---------------------------------------------------------------------
# Mock LRA Agent (replace with real import when wired)
# ---------------------------------------------------------------------

try:
    from src.agents.lra_agent import LRAAgent  # type: ignore
except ImportError:
    LRAAgent = None


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------

@pytest.fixture
def lra_agent():
    if LRAAgent is None:
        pytest.skip("LRAAgent not implemented yet")
    return LRAAgent()


@pytest.fixture
def research_request() -> Dict:
    return {
        "issue": "Applicability of Section 14 of the Limitation Act",
        "jurisdiction": "India",
    }


@pytest.fixture
def detailed_research_request() -> Dict:
    return {
        "issue": "Condonation of delay under Section 14 of the Limitation Act",
        "jurisdiction": "India",
        "court_level": "Supreme Court",
    }


# ---------------------------------------------------------------------
# Core Research Tests
# ---------------------------------------------------------------------

def test_research_is_performed(lra_agent, research_request):
    report = lra_agent.research(**research_request)

    assert isinstance(report, dict)
    assert len(report) > 0


def test_research_contains_required_sections(lra_agent, research_request):
    report = lra_agent.research(**research_request)

    required_fields = {
        "authorities",
        "statutes",
        "key_principles",
    }

    for field in required_fields:
        assert field in report


def test_authorities_are_listed(lra_agent, research_request):
    report = lra_agent.research(**research_request)

    assert isinstance(report["authorities"], list)
    assert len(report["authorities"]) > 0


def test_statutes_are_listed(lra_agent, research_request):
    report = lra_agent.research(**research_request)

    assert isinstance(report["statutes"], list)
    assert len(report["statutes"]) > 0


# ---------------------------------------------------------------------
# Relevance & Scope
# ---------------------------------------------------------------------

def test_research_is_issue_aligned(lra_agent, research_request):
    report = lra_agent.research(**research_request)

    combined_text = " ".join(
        report.get("key_principles", []) +
        report.get("statutes", []) +
        report.get("authorities", [])
    ).lower()

    assert any(
        keyword in combined_text
        for keyword in ["limitation", "delay", "section 14"]
    )


def test_research_varies_by_detail_level(
    lra_agent,
    research_request,
    detailed_research_request,
):
    basic_report = lra_agent.research(**research_request)
    detailed_report = lra_agent.research(**detailed_research_request)

    assert basic_report != detailed_report


# ---------------------------------------------------------------------
# Safety & Neutrality
# ---------------------------------------------------------------------

def test_research_avoids_legal_conclusions(lra_agent, research_request):
    report = lra_agent.research(**research_request)

    combined_text = " ".join(
        report.get("key_principles", []) +
        report.get("authorities", [])
    ).lower()

    conclusion_phrases = [
        "is entitled to",
        "must be allowed",
        "ought to succeed",
        "guarantees relief",
    ]

    for phrase in conclusion_phrases:
        assert phrase not in combined_text


def test_research_avoids_direct_legal_advice(lra_agent, research_request):
    report = lra_agent.research(**research_request)

    combined_text = " ".join(report.values()).lower()

    unsafe_phrases = [
        "you should file",
        "you must file",
        "immediately file",
        "it is mandatory to",
    ]

    for phrase in unsafe_phrases:
        assert phrase not in combined_text


# ---------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------

def test_unknown_jurisdiction_is_handled_gracefully(lra_agent):
    report = lra_agent.research(
        issue="Some legal issue",
        jurisdiction="Unknown",
    )

    assert isinstance(report, dict)
    assert "authorities" in report


def test_empty_issue_is_handled_safely(lra_agent):
    report = lra_agent.research(
        issue="",
        jurisdiction="India",
    )

    assert isinstance(report, dict)
    assert "key_principles" in report


# ---------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------

def test_research_is_deterministic(lra_agent, research_request):
    report_1 = lra_agent.research(**research_request)
    report_2 = lra_agent.research(**research_request)

    assert report_1 == report_2
