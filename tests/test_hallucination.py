"""
Hallucination Detection Tests

These tests validate that the hallucination detection logic:
- flags unsupported factual and legal claims
- penalizes absolute or overconfident language
- correlates hallucination risk with citation coverage
- remains deterministic and model-agnostic

This module focuses on *risk detection*, not truth verification.
"""

from __future__ import annotations

from typing import Dict, List

import pytest


# ---------------------------------------------------------------------
# Mock Hallucination Detector (replace with real import when wired)
# ---------------------------------------------------------------------

try:
    from src.validation.hallucination_detector import HallucinationDetector  # type: ignore
except ImportError:
    HallucinationDetector = None


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------

@pytest.fixture
def detector():
    if HallucinationDetector is None:
        pytest.skip("HallucinationDetector not implemented yet")
    return HallucinationDetector()


@pytest.fixture
def low_risk_content() -> Dict:
    return {
        "text": (
            "Section 14 of the Limitation Act permits exclusion of time "
            "spent in bona fide proceedings. In ABC Ltd vs Union of India, "
            "the Supreme Court observed that the provision should be "
            "construed liberally."
        ),
        "citations": [
            {
                "id": "SCC-2019-123",
                "reference": "ABC Ltd vs Union of India",
            }
        ],
    }


@pytest.fixture
def high_risk_content() -> Dict:
    return {
        "text": (
            "Section 14 always applies and guarantees condonation of delay "
            "in every case without exception."
        ),
        "citations": [],
    }


@pytest.fixture
def mixed_risk_content() -> Dict:
    return {
        "text": (
            "Section 14 may apply in certain cases. However, courts have "
            "clearly settled that delay must always be condoned."
        ),
        "citations": [],
    }


# ---------------------------------------------------------------------
# Core Hallucination Risk Tests
# ---------------------------------------------------------------------

def test_low_risk_content_is_flagged_low(detector, low_risk_content):
    report = detector.evaluate(
        text=low_risk_content["text"],
        citations=low_risk_content["citations"],
    )

    assert report["risk_level"] == "low"
    assert report["risk_score"] < 0.3


def test_high_risk_content_is_flagged_high(detector, high_risk_content):
    report = detector.evaluate(
        text=high_risk_content["text"],
        citations=high_risk_content["citations"],
    )

    assert report["risk_level"] == "high"
    assert report["risk_score"] >= 0.7


def test_mixed_risk_content_is_flagged_medium(detector, mixed_risk_content):
    report = detector.evaluate(
        text=mixed_risk_content["text"],
        citations=mixed_risk_content["citations"],
    )

    assert report["risk_level"] in {"medium", "high"}
    assert report["risk_score"] >= 0.4


# ---------------------------------------------------------------------
# Citation Dependency
# ---------------------------------------------------------------------

def test_missing_citations_increase_hallucination_risk(detector):
    text = (
        "The Supreme Court has conclusively ruled on this issue "
        "leaving no scope for doubt."
    )

    report = detector.evaluate(text=text, citations=[])

    assert report["risk_level"] in {"medium", "high"}


def test_presence_of_citations_reduces_risk(detector, low_risk_content):
    report = detector.evaluate(
        text=low_risk_content["text"],
        citations=low_risk_content["citations"],
    )

    assert report["risk_level"] == "low"


# ---------------------------------------------------------------------
# Language Pattern Detection
# ---------------------------------------------------------------------

def test_absolute_language_increases_risk(detector):
    text = "This rule always applies and has no exceptions."

    report = detector.evaluate(text=text, citations=[])

    assert report["risk_level"] == "high"


def test_speculative_language_is_not_penalized(detector):
    text = (
        "This provision may apply depending on the facts "
        "and judicial interpretation."
    )

    report = detector.evaluate(text=text, citations=[])

    assert report["risk_level"] in {"low", "medium"}


# ---------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------

def test_empty_text_returns_low_risk(detector):
    report = detector.evaluate(text="", citations=[])

    assert report["risk_level"] == "low"
    assert report["risk_score"] == 0.0


def test_non_legal_text_is_handled_gracefully(detector):
    text = "This document provides general background information."

    report = detector.evaluate(text=text, citations=[])

    assert report["risk_level"] in {"low", "medium"}


# ---------------------------------------------------------------------
# Report Structure
# ---------------------------------------------------------------------

def test_report_contains_required_fields(detector, low_risk_content):
    report = detector.evaluate(
        text=low_risk_content["text"],
        citations=low_risk_content["citations"],
    )

    required_fields = {
        "risk_level",
        "risk_score",
        "signals",
    }

    for field in required_fields:
        assert field in report
