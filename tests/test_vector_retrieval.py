"""
Vector Retrieval Tests

These tests validate the vector-based retrieval layer:
- documents can be indexed
- similarity search returns relevant results
- scores are ordered correctly
- metadata is preserved
- the system behaves deterministically and safely

These are functional tests, not performance benchmarks.
"""

from __future__ import annotations

from typing import Dict, List

import pytest


# ---------------------------------------------------------------------
# Mock Vector Store Manager (replace with real import when wired)
# ---------------------------------------------------------------------

try:
    from src.retrieval.vector_store_manager import VectorStoreManager  # type: ignore
except ImportError:
    VectorStoreManager = None


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------

@pytest.fixture
def vector_store():
    if VectorStoreManager is None:
        pytest.skip("VectorStoreManager not implemented yet")
    return VectorStoreManager()


@pytest.fixture
def sample_documents() -> List[Dict]:
    return [
        {
            "id": "doc_1",
            "text": (
                "Section 14 of the Limitation Act permits exclusion of "
                "time spent in bona fide proceedings."
            ),
            "metadata": {"source": "statute"},
        },
        {
            "id": "doc_2",
            "text": (
                "In ABC Ltd vs Union of India, the Supreme Court interpreted "
                "Section 14 of the Limitation Act liberally."
            ),
            "metadata": {"source": "case_law"},
        },
        {
            "id": "doc_3",
            "text": (
                "Article 21 of the Constitution guarantees the right "
                "to life and personal liberty."
            ),
            "metadata": {"source": "constitution"},
        },
    ]


@pytest.fixture
def relevant_query() -> str:
    return "Applicability of Section 14 of the Limitation Act"


@pytest.fixture
def irrelevant_query() -> str:
    return "Right to life under the Constitution"


# ---------------------------------------------------------------------
# Indexing Tests
# ---------------------------------------------------------------------

def test_documents_can_be_indexed(vector_store, sample_documents):
    vector_store.add_documents(sample_documents)

    stats = vector_store.stats()

    assert isinstance(stats, dict)
    assert stats.get("document_count", 0) >= len(sample_documents)


def test_reindexing_does_not_duplicate_documents(vector_store, sample_documents):
    vector_store.add_documents(sample_documents)
    vector_store.add_documents(sample_documents)

    stats = vector_store.stats()

    assert stats.get("document_count") == len(sample_documents)


# ---------------------------------------------------------------------
# Similarity Search
# ---------------------------------------------------------------------

def test_similarity_search_returns_results(
    vector_store,
    sample_documents,
    relevant_query,
):
    vector_store.add_documents(sample_documents)

    results = vector_store.search(query=relevant_query, top_k=5)

    assert isinstance(results, list)
    assert len(results) > 0


def test_similarity_search_returns_relevant_content(
    vector_store,
    sample_documents,
    relevant_query,
):
    vector_store.add_documents(sample_documents)

    results = vector_store.search(query=relevant_query, top_k=5)

    combined_text = " ".join(r["text"].lower() for r in results)

    assert any(
        keyword in combined_text
        for keyword in ["section 14", "limitation"]
    )


# ---------------------------------------------------------------------
# Ranking & Scores
# ---------------------------------------------------------------------

def test_similarity_scores_are_ordered(
    vector_store,
    sample_documents,
    relevant_query,
):
    vector_store.add_documents(sample_documents)

    results = vector_store.search(query=relevant_query, top_k=5)
    scores = [r["score"] for r in results]

    assert scores == sorted(scores, reverse=True)


def test_irrelevant_documents_rank_lower(
    vector_store,
    sample_documents,
    relevant_query,
    irrelevant_query,
):
    vector_store.add_documents(sample_documents)

    relevant_results = vector_store.search(query=relevant_query, top_k=1)
    irrelevant_results = vector_store.search(query=irrelevant_query, top_k=1)

    assert relevant_results[0]["score"] >= irrelevant_results[0]["score"]


# ---------------------------------------------------------------------
# Metadata Integrity
# ---------------------------------------------------------------------

def test_metadata_is_preserved_in_results(
    vector_store,
    sample_documents,
    relevant_query,
):
    vector_store.add_documents(sample_documents)

    results = vector_store.search(query=relevant_query, top_k=5)

    for result in results:
        assert "metadata" in result
        assert isinstance(result["metadata"], dict)


# ---------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------

def test_empty_query_is_handled_gracefully(vector_store, sample_documents):
    vector_store.add_documents(sample_documents)

    results = vector_store.search(query="", top_k=5)

    assert isinstance(results, list)


def test_search_without_indexed_documents_is_safe(vector_store):
    results = vector_store.search(query="Some query", top_k=5)

    assert isinstance(results, list)
    assert len(results) == 0


# ---------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------

def test_vector_search_is_deterministic(
    vector_store,
    sample_documents,
    relevant_query,
):
    vector_store.add_documents(sample_documents)

    results_1 = vector_store.search(query=relevant_query, top_k=5)
    results_2 = vector_store.search(query=relevant_query, top_k=5)

    assert results_1 == results_2
