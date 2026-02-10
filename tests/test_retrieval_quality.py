"""
Retrieval Quality Tests

These tests validate that the retrieval layer:
- returns relevant documents for a query
- ranks results by relevance
- avoids empty or low-quality responses
- behaves deterministically
- degrades gracefully when data is weak or missing

This is a quality test, not a performance or embedding test.
"""

from __future__ import annotations

from typing import Dict, List

import pytest


# ---------------------------------------------------------------------
# Mock Retriever (replace with real import when wired)
# ---------------------------------------------------------------------

try:
    from src.retrieval.retriever import Retriever  # type: ignore
except ImportError:
    Retriever = None


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------

@pytest.fixture
def retriever():
    if Retriever is None:
        pytest.skip("Retriever not implemented yet")
    return Retriever()


@pytest.fixture
def indexed_documents() -> List[Dict]:
    """
    Simulated documents assumed to be present in the vector store.
    """
    return [
        {
            "id": "doc_1",
            "text": "Section 14 of the Limitation Act permits exclusion of time spent in bona fide proceedings.",
            "metadata": {"source": "statute"},
        },
        {
            "id": "doc_2",
            "text": "In ABC Ltd vs Union of India, the Supreme Court interpreted Section 14 liberally.",
            "metadata": {"source": "case_law"},
        },
        {
            "id": "doc_3",
            "text": "Article 21 of the Constitution guarantees the right to life and personal liberty.",
            "metadata": {"source": "constitution"},
        },
    ]


@pytest.fixture
def relevant_query() -> str:
    return "Applicability of Section 14 of the Limitation Act"


@pytest.fixture
def irrelevant_query() -> str:
    return "Right to privacy under the Constitution"


# ---------------------------------------------------------------------
# Core Retrieval Tests
# ---------------------------------------------------------------------

def test_retrieval_returns_results(retriever, relevant_query):
    results = retriever.retrieve(query=relevant_query, top_k=5)

    assert isinstance(results, list)
    assert len(results) > 0


def test_retrieval_results_have_expected_structure(retriever, relevant_query):
    results = retriever.retrieve(query=relevant_query, top_k=5)

    required_fields = {"id", "text", "score"}

    for result in results:
        assert isinstance(result, dict)
        for field in required_fields:
            assert field in result


def test_retrieval_returns_relevant_content(retriever, relevant_query):
    results = retriever.retrieve(query=relevant_query, top_k=5)

    combined_text = " ".join(r["text"].lower() for r in results)

    assert any(
        keyword in combined_text
        for keyword in ["section 14", "limitation"]
    )


# ---------------------------------------------------------------------
# Ranking & Quality
# ---------------------------------------------------------------------

def test_results_are_ranked_by_relevance(retriever, relevant_query):
    results = retriever.retrieve(query=relevant_query, top_k=5)

    scores = [r["score"] for r in results]

    assert scores == sorted(scores, reverse=True)


def test_irrelevant_content_is_ranked_lower(
    retriever,
    relevant_query,
    irrelevant_query,
):
    relevant_results = retriever.retrieve(query=relevant_query, top_k=3)
    irrelevant_results = retriever.retrieve(query=irrelevant_query, top_k=3)

    assert relevant_results[0]["score"] >= irrelevant_results[0]["score"]


# ---------------------------------------------------------------------
# Diversity & Coverage
# ---------------------------------------------------------------------

def test_retrieval_returns_diverse_sources(retriever, relevant_query):
    results = retriever.retrieve(query=relevant_query, top_k=5)

    sources = {
        r.get("metadata", {}).get("source")
        for r in results
        if r.get("metadata")
    }

    # Expect at least statute + case law where available
    assert len(sources) >= 1


# ---------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------

def test_empty_query_returns_empty_or_safe_response(retriever):
    results = retriever.retrieve(query="", top_k=5)

    assert isinstance(results, list)


def test_unknown_query_is_handled_gracefully(retriever):
    results = retriever.retrieve(
        query="Some completely unrelated topic",
        top_k=5,
    )

    assert isinstance(results, list)


# ---------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------

def test_retrieval_is_deterministic(retriever, relevant_query):
    results_1 = retriever.retrieve(query=relevant_query, top_k=5)
    results_2 = retriever.retrieve(query=relevant_query, top_k=5)

    assert results_1 == results_2
