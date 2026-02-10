"""
Reranker

Reranks retrieved documents using deterministic scoring strategies.
Designed for legal, tribunal, and enterprise document retrieval.

LLM-free by default, but extensible.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------

class RerankerError(RuntimeError):
    pass


# ---------------------------------------------------------------------
# Reranker
# ---------------------------------------------------------------------

class Reranker:
    """
    Reranks retrieved documents based on multiple weighted signals.
    """

    def __init__(
        self,
        *,
        weight_similarity: float = 0.7,
        weight_metadata: float = 0.3,
        boost_recent: bool = True,
        boost_exact_match: bool = True,
    ) -> None:
        """
        Args:
            weight_similarity: weight for vector similarity score
            weight_metadata: weight for metadata-based signals
            boost_recent: boost newer documents if date metadata exists
            boost_exact_match: boost exact query term matches
        """
        self.weight_similarity = weight_similarity
        self.weight_metadata = weight_metadata
        self.boost_recent = boost_recent
        self.boost_exact_match = boost_exact_match

        logger.info(
            "Reranker initialized | similarity=%.2f | metadata=%.2f",
            weight_similarity,
            weight_metadata,
        )

    # -----------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------

    def rerank(
        self,
        *,
        query: str,
        results: List[Dict[str, object]],
        top_k: Optional[int] = None,
    ) -> List[Dict[str, object]]:
        """
        Rerank retrieved results.

        Args:
            query: original user query
            results: list of retrieved documents
            top_k: optional limit on returned results

        Each result is expected to contain:
        {
            "id": str,
            "score": float,        # similarity score
            "metadata": dict
        }
        """
        if not results:
            return []

        reranked = []

        for result in results:
            final_score, signals = self._score(query, result)

            enriched = dict(result)
            enriched["final_score"] = final_score
            enriched["signals"] = signals

            reranked.append(enriched)

        reranked.sort(key=lambda x: x["final_score"], reverse=True)

        if top_k:
            reranked = reranked[:top_k]

        logger.debug(
            "Reranked %s documents | returning=%s",
            len(results),
            len(reranked),
        )

        return reranked

    # ---------------------------------------------------------------------
    # Scoring Logic
    # ---------------------------------------------------------------------

    def _score(
        self,
        query: str,
        result: Dict[str, object],
    ) -> tuple[float, Dict[str, float]]:
        """
        Compute final score and explanation signals.
        """
        similarity_score = float(result.get("score", 0.0))
        metadata = result.get("metadata", {}) or {}

        metadata_score = 0.0

        if self.boost_exact_match:
            metadata_score += self._exact_match_boost(query, metadata)

        if self.boost_recent:
            metadata_score += self._recency_boost(metadata)

        final_score = (
            self.weight_similarity * similarity_score
            + self.weight_metadata * metadata_score
        )

        signals = {
            "similarity": similarity_score,
            "metadata": metadata_score,
        }

        return final_score, signals

    # ---------------------------------------------------------------------
    # Metadata Boosts
    # ---------------------------------------------------------------------

    def _exact_match_boost(self, query: str, metadata: Dict[str, object]) -> float:
        """
        Boost if query terms appear in title or heading metadata.
        """
        text_fields = [
            str(metadata.get("title", "")).lower(),
            str(metadata.get("heading", "")).lower(),
            str(metadata.get("section", "")).lower(),
        ]

        query_terms = query.lower().split()
        hits = 0

        for term in query_terms:
            if any(term in field for field in text_fields):
                hits += 1

        if hits == 0:
            return 0.0

        # capped boost
        return min(0.3, 0.05 * hits)

    def _recency_boost(self, metadata: Dict[str, object]) -> float:
        """
        Boost newer documents if year/date metadata is present.
        """
        year = metadata.get("year") or metadata.get("assessment_year")

        try:
            year = int(str(year)[:4])
        except Exception:
            return 0.0

        if year >= 2020:
            return 0.2
        if year >= 2015:
            return 0.1

        return 0.0
