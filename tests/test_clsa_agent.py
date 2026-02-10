"""
CLSA Agent Tests (Clarity, Logic, Structure, Alignment)

These tests validate that the CLSA agent evaluates:
- clarity of language
- logical flow
- structural completeness
- alignment with the stated issue

The tests are deterministic, model-agnostic, and CI-safe.
"""

from __future__ import annotations

from typing import Dict

import pytest


# ---------------------------------------------------------------------
# Mock CLSA Agent (replace with real import when wired)
# ---------------------------------------------------------------------

try:
    from src.agents.clsa_agent import CLSAAgent  # type: ignore
except ImportError:
    CLSAAgent = None


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------

@pytest.fixture
def clsa_agent():
    if CLSAAgent is None:
        pytest.skip("CLSAAgent not implemented yet")
    return CLSAAgent()


@pytest.fixture
def well_structured_argument() -> Dict:
    return {
        "issue": (
            "Whether delay can be condoned under Section 14 of "
            "the Limitation Act."
        ),
        "text": (
            "The issue for consideration is whether Section 14 of the "
            "Limitation Act permits exclusion of time spent in prior "
            "proceedings. The provision applies where the earlier "
            "proceeding was pursued with due diligence and good faith. "
            "In ABC Ltd vs Union of India, the Supreme Court observed "
            "that Section 14 should be construed liberally to advance "
            "substantial justice. Therefore, if the factual requirements "
            "are satisfied, the delay may be condoned. In conclusion, "
            "the applicability of Section 14 depends on the facts of "
            "each case."
        ),
    }


@pytest.fixture
def poorly_structured_argument() -> Dict:
    return {
        "issue": (
            "Whether delay can be condoned under Section 14 of "
            "the Limitation Act."
        ),
        "text": (
            "Section 14 is important. Delay is an issue. Courts have said "
            "many things. It applies. It does not apply sometimes."
        ),
    }


@pytest.fixture
def misaligned_argument() -> Dict:
    return {
        "issue": "Applicability of Section 14 of the Limitation Act.",
        "text": (
            "Article 21 of the Constitution guarantees personal liberty. "
            "The right to life has been expanded in many judgments."
        ),
    }


# ---------------------------------------------------------------------
# Core CLSA Tests
# ---------------------------------------------------------------------

def test_well_structured_argument_scores_high(clsa_agent, well_structured_argument):
    report = clsa_agent.evaluate(
        issue=well_structured_argument["issue"],
        text=well_structured_argument["text"],
    )

    assert report["clarity_score"] >= 0.7
    assert report["logic_score"] >= 0.7
    assert report["structure_score"] >= 0.7
    assert report["alignment_score"] >= 0.7
    assert report["overall_rating"] in {"good", "excellent"}


def test_poor_structure_is_flagged(clsa_agent, poorly_structured_argument):
    report = clsa_agent.evaluate(
        issue=poorly_structured_argument["issue"],
        text=poorly_structured_argument["text"],
    )

    assert report["structure_score"] < 0.5
    assert report["overall_rating"] in {"poor", "needs_review"}


def test_misalignment_is_detected(clsa_agent, misaligned_argument):
    report = clsa_agent.evaluate(
        issue=misaligned_argument["issue"],
        text=misaligned_argument["text"],
    )

    assert report["alignment_score"] < 0.5
    assert report["overall_rating"] in {"poor", "needs_review"}


# ---------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------

def test_empty_text_fails_all_dimensions(clsa_agent):
    report = clsa_agent.evaluate(
        issue="Some legal issue",
        text="",
    )

    assert report["clarity_score"] == 0.0
    assert report["logic_score"] == 0.0
    assert report["structure_score"] == 0.0
    assert report["alignment_score"] == 0.0
    assert report["overall_rating"] == "poor"


def test_report_contains_required_fields(clsa_agent, well_structured_argument):
    report = clsa_agent.evaluate(
        issue=well_structured_argument["issue"],
        text=well_structured_argument["text"],
    )

    required_fields = {
        "clarity_score",
        "logic_score",
        "structure_score",
        "alignment_score",
        "overall_rating",
    }

    for field in required_fields:
        assert field in report
