"""
LAB Agent Tests (Legal Argument Builder Agent)

These tests validate that the Legal Argument Builder agent:
- constructs structured legal arguments
- aligns arguments with the stated issue
- incorporates provided research and citations
- avoids direct legal advice and absolute claims
- produces deterministic output

The tests are model-agnostic and CI-safe.
"""

from __future__ import annotations

from typing import Dict, List

import pytest


# ---------------------------------------------------------------------
# Mock LAB Agent (replace with real import when wired)
# ---------------------------------------------------------------------

try:
    from src.agents.lab_agent import LABAgent  # type: ignore
except ImportError:
    LABAgent = None


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------

@pytest.fixture
def lab_agent():
    if LABAgent is None:
        pytest.skip("LABAgent not implemented yet")
    return LABAgent()


@pytest.fixture
def valid_argument_request() -> Dict:
    return {
        "issue": "Whether delay can be condoned under Section 14 of the Limitation Act.",
        "research_points": [
            "Section 14 permits exclusion of time spent in bona fide proceedings.",
            "The provision requires due diligence and good faith.",
        ],
        "citations": [
            {
                "id": "SCC-2019-123",
                "reference": "ABC Ltd vs Union of India",
            }
        ],
    }


@pytest.fixture
def minimal_argument_request() -> Dict:
    return {
        "issue": "Applicability of Section 14 of the Limitation Act.",
        "research_points": [],
        "citations": [],
    }


# ---------------------------------------------------------------------
# Core Argument Builder Tests
# ---------------------------------------------------------------------

def test_argument_is_generated(lab_agent, valid_argument_request):
    argument = lab_agent.build_argument(**valid_argument_request)

    assert isinstance(argument, str)
    assert len(argument.strip()) > 0


def test_argument_contains_issue_statement(lab_agent, valid_argument_request):
    argument = lab_agent.build_argument(**valid_argument_request)

    assert valid_argument_request["issue"].lower() in argument.lower()


def test_argument_has_basic_structure(lab_agent, valid_argument_request):
    argument = lab_agent.build_argument(**valid_argument_request)

    expected_markers = [
        "issue",
        "analysis",
        "conclusion",
    ]

    arg_lower = argument.lower()
    for marker in expected_markers:
        assert marker in arg_lower


def test_argument_incorporates_research_points(lab_agent, valid_argument_request):
    argument = lab_agent.build_argument(**valid_argument_request)

    for point in valid_argument_request["research_points"]:
        assert any(
            keyword.lower() in argument.lower()
            for keyword in point.split()[:3]
        )


# ---------------------------------------------------------------------
# Safety & Language
# ---------------------------------------------------------------------

def test_argument_avoids_direct_legal_advice(lab_agent, valid_argument_request):
    argument = lab_agent.build_argument(**valid_argument_request)

    unsafe_phrases = [
        "you should file",
        "you must file",
        "immediately file",
        "it is mandatory to",
    ]

    arg_lower = argument.lower()
    for phrase in unsafe_phrases:
        assert phrase not in arg_lower


def test_argument_avoids_absolute_claims(lab_agent, valid_argument_request):
    argument = lab_agent.build_argument(**valid_argument_request)

    absolute_phrases = [
        "always applies",
        "never applies",
        "guarantees",
        "no exception",
    ]

    arg_lower = argument.lower()
    for phrase in absolute_phrases:
        assert phrase not in arg_lower


# ---------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------

def test_minimal_input_still_generates_argument(lab_agent, minimal_argument_request):
    argument = lab_agent.build_argument(**minimal_argument_request)

    assert isinstance(argument, str)
    assert len(argument.strip()) > 0


def test_empty_inputs_are_handled_gracefully(lab_agent):
    argument = lab_agent.build_argument(
        issue="",
        research_points=[],
        citations=[],
    )

    assert isinstance(argument, str)


# ---------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------

def test_argument_generation_is_deterministic(lab_agent, valid_argument_request):
    arg_1 = lab_agent.build_argument(**valid_argument_request)
    arg_2 = lab_agent.build_argument(**valid_argument_request)

    assert arg_1 == arg_2
