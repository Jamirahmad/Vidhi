"""
LII Agent Tests (Legal Issue Identification & Intelligence Agent)

These tests validate that the LII agent:
- extracts clear legal issues from raw case descriptions
- distinguishes primary and secondary issues
- avoids legal conclusions or advice
- produces structured, deterministic output
- handles vague or incomplete inputs safely

The tests are model-agnostic and CI-safe.
"""

from __future__ import annotations

from typing import Dict, List

import pytest


# ---------------------------------------------------------------------
# Mock LII Agent (replace with real import when wired)
# ---------------------------------------------------------------------

try:
    from src.agents.lii_agent import LIIAgent  # type: ignore
except ImportError:
    LIIAgent = None


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------

@pytest.fixture
def lii_agent():
    if LIIAgent is None:
        pytest.skip("LIIAgent not implemented yet")
    return LIIAgent()


@pytest.fixture
def clear_case_description() -> Dict:
    return {
        "case_description": (
            "The petitioner filed an appeal before an authority that "
            "was later held to lack jurisdiction. After dismissal, a "
            "fresh proceeding was initiated, leading to delay issues "
            "under the Limitation Act."
        )
    }


@pytest.fixture
def complex_case_description() -> Dict:
    return {
        "case_description": (
            "An administrative order was challenged on grounds of "
            "violation of natural justice. The petition was dismissed "
            "on technical grounds, and a subsequent writ petition "
            "raised issues of limitation, jurisdiction, and procedural fairness."
        )
    }


@pytest.fixture
def vague_case_description() -> Dict:
    return {
        "case_description": (
            "There is a dispute related to a legal matter involving delay "
            "and some procedural problems."
        )
    }


# ---------------------------------------------------------------------
# Core Issue Identification Tests
# ---------------------------------------------------------------------

def test_issues_are_identified(lii_agent, clear_case_description):
    report = lii_agent.identify_issues(**clear_case_description)

    assert isinstance(report, dict)
    assert "primary_issues" in report
    assert isinstance(report["primary_issues"], list)
    assert len(report["primary_issues"]) > 0


def test_secondary_issues_are_optional(lii_agent, clear_case_description):
    report = lii_agent.identify_issues(**clear_case_description)

    assert "secondary_issues" in report
    assert isinstance(report["secondary_issues"], list)


def test_primary_issue_is_legally_framed(lii_agent, clear_case_description):
    report = lii_agent.identify_issues(**clear_case_description)

    issue_text = " ".join(report["primary_issues"]).lower()
    assert any(
        keyword in issue_text
        for keyword in ["limitation", "jurisdiction", "delay"]
    )


# ---------------------------------------------------------------------
# Complex Input Handling
# ---------------------------------------------------------------------

def test_multiple_issues_are_detected(lii_agent, complex_case_description):
    report = lii_agent.identify_issues(**complex_case_description)

    total_issues = (
        len(report.get("primary_issues", [])) +
        len(report.get("secondary_issues", []))
    )

    assert total_issues >= 2


def test_issue_classification_is_consistent(lii_agent, complex_case_description):
    report = lii_agent.identify_issues(**complex_case_description)

    assert isinstance(report.get("primary_issues"), list)
    assert isinstance(report.get("secondary_issues"), list)


# ---------------------------------------------------------------------
# Safety & Scope Control
# ---------------------------------------------------------------------

def test_issues_do_not_contain_legal_advice(lii_agent, clear_case_description):
    report = lii_agent.identify_issues(**clear_case_description)

    combined_text = " ".join(
        report.get("primary_issues", []) +
        report.get("secondary_issues", [])
    ).lower()

    unsafe_phrases = [
        "you should file",
        "must be allowed",
        "ought to succeed",
        "guarantees relief",
    ]

    for phrase in unsafe_phrases:
        assert phrase not in combined_text


def test_issues_do_not_contain_conclusions(lii_agent, clear_case_description):
    report = lii_agent.identify_issues(**clear_case_description)

    combined_text = " ".join(
        report.get("primary_issues", []) +
        report.get("secondary_issues", [])
    ).lower()

    conclusion_phrases = [
        "is entitled to",
        "clearly illegal",
        "unconstitutional",
    ]

    for phrase in conclusion_phrases:
        assert phrase not in combined_text


# ---------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------

def test_vague_description_still_returns_generic_issues(
    lii_agent,
    vague_case_description,
):
    report = lii_agent.identify_issues(**vague_case_description)

    assert isinstance(report, dict)
    assert "primary_issues" in report
    assert len(report["primary_issues"]) > 0


def test_empty_description_is_handled_gracefully(lii_agent):
    report = lii_agent.identify_issues(case_description="")

    assert isinstance(report, dict)
    assert "primary_issues" in report


# ---------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------

def test_issue_identification_is_deterministic(
    lii_agent,
    clear_case_description,
):
    report_1 = lii_agent.identify_issues(**clear_case_description)
    report_2 = lii_agent.identify_issues(**clear_case_description)

    assert report_1 == report_2
