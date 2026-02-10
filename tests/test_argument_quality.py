"""
Argument Quality Tests

These tests evaluate the structural and qualitative aspects
of generated legal arguments without judging legal correctness.

Focus areas:
- clarity
- structure
- citation linkage
- risk indicators
- completeness
"""

from __future__ import annotations

import re
from typing import Dict, List

import pytest


# ---------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------

def has_minimum_length(text: str, min_words: int = 50) -> bool:
    return len(text.split()) >= min_words


def has_logical_structure(text: str) -> bool:
    """
    Checks for basic legal argument structure:
    issue → reasoning → conclusion
    """
    keywords = [
        "issue",
        "question",
        "analysis",
        "reason",
        "therefore",
        "thus",
        "conclusion",
    ]
    text_lower = text.lower()
    return any(k in text_lower for k in keywords)


def has_citations(text: str) -> bool:
    """
    Looks for common legal citation patterns.
    """
    patterns = [
        r"\bvs\b",
        r"\bsection\b",
        r"\bart\.?\b",
        r"\bAIR\b",
        r"\bSCC\b",
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def avoids_absolute_claims(text: str) -> bool:
    """
    Flags risky absolute language.
    """
    risky_phrases = [
        "always applies",
        "never applies",
        "no exception",
        "guarantees",
        "undoubtedly",
    ]
    text_lower = text.lower()
    return not any(p in text_lower for p in risky_phrases)


def avoids_direct_legal_advice(text: str) -> bool:
    """
    Ensures the argument does not instruct the user directly.
    """
    advisory_phrases = [
        "you should file",
        "you must file",
        "it is mandatory to file",
        "immediately file",
    ]
    text_lower = text.lower()
    return not any(p in text_lower for p in advisory_phrases)


# ---------------------------------------------------------------------
# Sample Argument Fixture
# ---------------------------------------------------------------------

@pytest.fixture
def sample_argument() -> Dict[str, str]:
    return {
        "issue": (
            "Whether the delay can be condoned under Section 14 "
            "of the Limitation Act."
        ),
        "argument_text": (
            "The issue for consideration is whether Section 14 of the "
            "Limitation Act applies in the present case. Section 14 "
            "permits exclusion of time spent in prosecuting a proceeding "
            "with due diligence and good faith before a court without "
            "jurisdiction. The Supreme Court in ABC Ltd vs Union of India "
            "has observed that the provision should be construed liberally "
            "to advance substantial justice. Therefore, where the prior "
            "proceeding was pursued bona fide, the benefit of Section 14 "
            "may be available. Thus, the delay may be condoned depending "
            "on the factual matrix."
        ),
    }


# ---------------------------------------------------------------------
# Argument Quality Tests
# ---------------------------------------------------------------------

def test_argument_has_minimum_length(sample_argument):
    text = sample_argument["argument_text"]
    assert has_minimum_length(text), "Argument is too short to be meaningful"


def test_argument_has_logical_structure(sample_argument):
    text = sample_argument["argument_text"]
    assert has_logical_structure(text), "Argument lacks logical structure"


def test_argument_contains_citations(sample_argument):
    text = sample_argument["argument_text"]
    assert has_citations(text), "Argument does not reference any legal sources"


def test_argument_avoids_absolute_claims(sample_argument):
    text = sample_argument["argument_text"]
    assert avoids_absolute_claims(text), "Argument uses risky absolute language"


def test_argument_avoids_direct_legal_advice(sample_argument):
    text = sample_argument["argument_text"]
    assert avoids_direct_legal_advice(text), (
        "Argument crosses into direct legal advice"
    )


# ---------------------------------------------------------------------
# Edge Case Tests
# ---------------------------------------------------------------------

def test_empty_argument_fails_quality_checks():
    text = ""
    assert not has_minimum_length(text)
    assert not has_logical_structure(text)
    assert not has_citations(text)


def test_overconfident_argument_is_flagged():
    text = (
        "Section 14 always applies and guarantees condonation of delay. "
        "There is no exception to this rule."
    )
    assert not avoids_absolute_claims(text)


def test_advisory_language_is_flagged():
    text = (
        "You should file an application immediately to get relief "
        "under Section 14."
    )
    assert not avoids_direct_legal_advice(text)
