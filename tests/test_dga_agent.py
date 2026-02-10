"""
DGA Agent Tests (Document Generation Agent)

These tests validate that the DGA agent:
- generates structurally complete documents
- respects the requested document type
- preserves factual inputs
- avoids unsafe legal advice
- produces deterministic, review-ready output

The tests are model-agnostic and CI-safe.
"""

from __future__ import annotations

from typing import Dict

import pytest


# ---------------------------------------------------------------------
# Mock DGA Agent (replace with real import when wired)
# ---------------------------------------------------------------------

try:
    from src.agents.dga_agent import DGAAgent  # type: ignore
except ImportError:
    DGAAgent = None


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------

@pytest.fixture
def dga_agent():
    if DGAAgent is None:
        pytest.skip("DGAAgent not implemented yet")
    return DGAAgent()


@pytest.fixture
def valid_generation_request() -> Dict:
    return {
        "document_type": "Research Note",
        "case_context": {
            "case_title": "ABC Ltd vs Union of India",
            "court": "Supreme Court of India",
            "year": 2019,
        },
        "content": {
            "issue": "Applicability of Section 14 of the Limitation Act",
            "analysis": (
                "Section 14 permits exclusion of time spent in bona fide "
                "proceedings before a court without jurisdiction."
            ),
            "citations": [
                {
                    "id": "SCC-2019-123",
                    "reference": "ABC Ltd vs Union of India",
                }
            ],
        },
    }


@pytest.fixture
def minimal_generation_request() -> Dict:
    return {
        "document_type": "Draft Note",
        "case_context": {},
        "content": {
            "issue": "Limitation Act Section 14",
            "analysis": "",
            "citations": [],
        },
    }


# ---------------------------------------------------------------------
# Core DGA Tests
# ---------------------------------------------------------------------

def test_document_is_generated(dga_agent, valid_generation_request):
    document = dga_agent.generate(**valid_generation_request)

    assert isinstance(document, str)
    assert len(document.strip()) > 0


def test_document_contains_core_sections(dga_agent, valid_generation_request):
    document = dga_agent.generate(**valid_generation_request)

    expected_sections = [
        "Issue",
        "Analysis",
        "Conclusion",
    ]

    for section in expected_sections:
        assert section.lower() in document.lower()


def test_document_respects_document_type(dga_agent, valid_generation_request):
    document = dga_agent.generate(**valid_generation_request)

    assert "research note" in document.lower()


def test_document_preserves_issue_statement(dga_agent, valid_generation_request):
    document = dga_agent.generate(**valid_generation_request)

    issue = valid_generation_request["content"]["issue"]
    assert issue.lower() in document.lower()


# ---------------------------------------------------------------------
# Safety & Quality
# ---------------------------------------------------------------------

def test_document_avoids_direct_legal_advice(dga_agent, valid_generation_request):
    document = dga_agent.generate(**valid_generation_request)

    unsafe_phrases = [
        "you should file",
        "you must file",
        "immediately file",
        "it is mandatory to file",
    ]

    doc_lower = document.lower()
    for phrase in unsafe_phrases:
        assert phrase not in doc_lower


def test_document_avoids_absolute_claims(dga_agent, valid_generation_request):
    document = dga_agent.generate(**valid_generation_request)

    absolute_phrases = [
        "always applies",
        "never applies",
        "guarantees",
        "no exception",
    ]

    doc_lower = document.lower()
    for phrase in absolute_phrases:
        assert phrase not in doc_lower


# ---------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------

def test_minimal_input_still_generates_document(dga_agent, minimal_generation_request):
    document = dga_agent.generate(**minimal_generation_request)

    assert isinstance(document, str)
    assert len(document.strip()) > 0


def test_empty_inputs_are_handled_gracefully(dga_agent):
    document = dga_agent.generate(
        document_type="Note",
        case_context={},
        content={},
    )

    assert isinstance(document, str)


# ---------------------------------------------------------------------
# Consistency
# ---------------------------------------------------------------------

def test_generation_is_deterministic(dga_agent, valid_generation_request):
    doc_1 = dga_agent.generate(**valid_generation_request)
    doc_2 = dga_agent.generate(**valid_generation_request)

    assert doc_1 == doc_2
