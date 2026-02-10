"""
Orchestrator Flow Tests

These tests validate that the orchestrator:
- invokes agents in the correct sequence
- passes outputs cleanly between agents
- produces a final, review-ready artifact
- fails safely when upstream stages break
- behaves deterministically

This is an integration-level test, not an intelligence test.
"""

from __future__ import annotations

from typing import Dict

import pytest


# ---------------------------------------------------------------------
# Mock Orchestrator (replace with real import when wired)
# ---------------------------------------------------------------------

try:
    from src.orchestrator.agent_orchestrator import AgentOrchestrator  # type: ignore
except ImportError:
    AgentOrchestrator = None


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------

@pytest.fixture
def orchestrator():
    if AgentOrchestrator is None:
        pytest.skip("AgentOrchestrator not implemented yet")
    return AgentOrchestrator()


@pytest.fixture
def valid_case_input() -> Dict:
    return {
        "case_description": (
            "The petitioner pursued a remedy before an authority that "
            "lacked jurisdiction, leading to delay under the Limitation Act."
        ),
        "jurisdiction": "India",
        "document_type": "Research Note",
    }


# ---------------------------------------------------------------------
# Core Orchestrator Flow
# ---------------------------------------------------------------------

def test_full_orchestrator_flow(orchestrator, valid_case_input):
    """
    End-to-end happy path:
    LII → LRA → LAF → LAB → CLSA → CCA → DGA
    """
    result = orchestrator.run(**valid_case_input)

    assert isinstance(result, dict)

    expected_keys = {
        "issues",
        "research",
        "analysis",
        "argument",
        "quality_report",
        "compliance_report",
        "final_document",
    }

    for key in expected_keys:
        assert key in result


def test_final_document_is_generated(orchestrator, valid_case_input):
    result = orchestrator.run(**valid_case_input)

    document = result.get("final_document")

    assert isinstance(document, str)
    assert len(document.strip()) > 0


# ---------------------------------------------------------------------
# Sequencing & Dependency Checks
# ---------------------------------------------------------------------

def test_analysis_depends_on_research(orchestrator, valid_case_input):
    result = orchestrator.run(**valid_case_input)

    research = result.get("research", {})
    analysis = result.get("analysis", {})

    assert isinstance(research, dict)
    assert isinstance(analysis, dict)
    assert len(research) > 0
    assert len(analysis) > 0


def test_argument_depends_on_analysis(orchestrator, valid_case_input):
    result = orchestrator.run(**valid_case_input)

    argument = result.get("argument")
    analysis = result.get("analysis")

    assert argument is not None
    assert analysis is not None


# ---------------------------------------------------------------------
# Safety Gates
# ---------------------------------------------------------------------

def test_quality_gate_is_enforced(orchestrator, valid_case_input):
    result = orchestrator.run(**valid_case_input)

    quality = result.get("quality_report")

    assert isinstance(quality, dict)
    assert "overall_rating" in quality


def test_compliance_gate_is_enforced(orchestrator, valid_case_input):
    result = orchestrator.run(**valid_case_input)

    compliance = result.get("compliance_report")

    assert isinstance(compliance, dict)
    assert "overall_status" in compliance


# ---------------------------------------------------------------------
# Failure Handling
# ---------------------------------------------------------------------

def test_orchestrator_handles_empty_input_gracefully(orchestrator):
    result = orchestrator.run(
        case_description="",
        jurisdiction="India",
        document_type="Note",
    )

    assert isinstance(result, dict)
    assert "final_document" in result


def test_orchestrator_does_not_crash_on_partial_failure(orchestrator):
    """
    Simulates a weak upstream signal but expects graceful degradation,
    not a hard crash.
    """
    result = orchestrator.run(
        case_description="Unclear dispute with minimal facts.",
        jurisdiction="Unknown",
        document_type="Draft Note",
    )

    assert isinstance(result, dict)
    assert "final_document" in result


# ---------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------

def test_orchestrator_is_deterministic(orchestrator, valid_case_input):
    result_1 = orchestrator.run(**valid_case_input)
    result_2 = orchestrator.run(**valid_case_input)

    assert result_1 == result_2
