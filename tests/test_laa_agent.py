"""
LAA Agent Tests (Legal Aid Agent)

These tests validate that the Legal Aid Agent:
- provides high-level legal information
- avoids direct legal advice
- tailors guidance to the area of law
- produces structured, user-friendly output
- handles edge cases safely and gracefully

The tests are deterministic, model-agnostic, and CI-safe.
"""

from __future__ import annotations

from typing import Dict

import pytest


# ---------------------------------------------------------------------
# Mock LAA Agent (replace with real import when wired)
# ---------------------------------------------------------------------

try:
    from src.agents.laa_agent import LAAAgent  # type: ignore
except ImportError:
    LAAAgent = None


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------

@pytest.fixture
def laa_agent():
    if LAAAgent is None:
        pytest.skip("LAAAgent not implemented yet")
    return LAAAgent()


@pytest.fixture
def consumer_law_query() -> Dict:
    return {
        "area_of_law": "Consumer Protection",
        "issue_description": (
            "Delay in resolving a consumer complaint by a service provider."
        ),
    }


@pytest.fixture
def constitutional_law_query() -> Dict:
    return {
        "area_of_law": "Constitutional Law",
        "issue_description": (
            "Challenge to administrative action affecting fundamental rights."
        ),
    }


# ---------------------------------------------------------------------
# Core LAA Tests
# ---------------------------------------------------------------------

def test_legal_aid_response_is_generated(laa_agent, consumer_law_query):
    response = laa_agent.provide_guidance(**consumer_law_query)

    assert isinstance(response, dict)
    assert len(response) > 0


def test_response_contains_required_sections(laa_agent, consumer_law_query):
    response = laa_agent.provide_guidance(**consumer_law_query)

    required_fields = {
        "overview",
        "possible_steps",
        "important_notes",
    }

    for field in required_fields:
        assert field in response


def test_possible_steps_are_listed(laa_agent, consumer_law_query):
    response = laa_agent.provide_guidance(**consumer_law_query)

    assert isinstance(response["possible_steps"], list)
    assert len(response["possible_steps"]) > 0


# ---------------------------------------------------------------------
# Scope & Safety
# ---------------------------------------------------------------------

def test_response_avoids_direct_legal_advice(laa_agent, consumer_law_query):
    response = laa_agent.provide_guidance(**consumer_law_query)

    combined_text = " ".join(
        [response.get("overview", "")] +
        response.get("possible_steps", []) +
        response.get("important_notes", [])
    ).lower()

    unsafe_phrases = [
        "you should file",
        "you must file",
        "immediately file",
        "it is mandatory to",
        "guarantees relief",
    ]

    for phrase in unsafe_phrases:
        assert phrase not in combined_text


def test_response_uses_cautious_language(laa_agent, consumer_law_query):
    response = laa_agent.provide_guidance(**consumer_law_query)

    text = response.get("overview", "").lower()
    assert any(
        phrase in text
        for phrase in ["may", "generally", "depending on", "typically"]
    )


# ---------------------------------------------------------------------
# Domain Awareness
# ---------------------------------------------------------------------

def test_guidance_varies_by_area_of_law(
    laa_agent,
    consumer_law_query,
    constitutional_law_query,
):
    consumer_response = laa_agent.provide_guidance(**consumer_law_query)
    constitutional_response = laa_agent.provide_guidance(**constitutional_law_query)

    assert consumer_response["overview"] != constitutional_response["overview"]


# ---------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------

def test_empty_issue_description_is_handled_gracefully(laa_agent):
    response = laa_agent.provide_guidance(
        area_of_law="General",
        issue_description="",
    )

    assert isinstance(response, dict)
    assert "overview" in response


def test_unknown_area_of_law_is_handled_safely(laa_agent):
    response = laa_agent.provide_guidance(
        area_of_law="Unknown Area",
        issue_description="Some generic legal concern.",
    )

    assert isinstance(response, dict)
    assert "overview" in response
    assert len(response.get("possible_steps", [])) > 0
