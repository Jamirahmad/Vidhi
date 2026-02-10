"""
Query Expander

Expands user queries to improve retrieval recall.
Designed for legal, tribunal, and policy document search.

This implementation is deterministic, explainable,
and LLM-optional.
"""

from __future__ import annotations

import re
from typing import Dict, List, Set

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------
# Query Expander
# ---------------------------------------------------------------------

class QueryExpander:
    """
    Expands a query into multiple semantically related queries.
    """

    def __init__(
        self,
        *,
        enable_synonyms: bool = True,
        enable_legal_expansion: bool = True,
        max_expansions: int = 5,
    ) -> None:
        self.enable_synonyms = enable_synonyms
        self.enable_legal_expansion = enable_legal_expansion
        self.max_expansions = max_expansions

        logger.info(
            "QueryExpander initialized | synonyms=%s | legal=%s",
            enable_synonyms,
            enable_legal_expansion,
        )

    # -----------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------

    def expand(self, query: str) -> List[str]:
        """
        Expand a query into multiple variants.

        Returns:
            List of expanded queries including original.
        """
        normalized = self._normalize(query)

        expansions: Set[str] = {normalized}

        if self.enable_synonyms:
            expansions |= self._expand_synonyms(normalized)

        if self.enable_legal_expansion:
            expansions |= self._expand_legal_terms(normalized)

        results = list(expansions)[: self.max_expansions]

        logger.debug(
            "Query expanded | original='%s' | expansions=%s",
            query,
            results,
        )

        return results

    # -----------------------------------------------------------------
    # Expansion Strategies
    # -----------------------------------------------------------------

    def _expand_synonyms(self, query: str) -> Set[str]:
        """
        Expand general English synonyms (lightweight).
        """
        synonym_map: Dict[str, List[str]] = {
            "appeal": ["appeal", "review petition"],
            "order": ["order", "judgment", "decision"],
            "delay": ["delay", "late", "belated"],
            "dismissed": ["dismissed", "rejected"],
            "allowed": ["allowed", "granted"],
            "penalty": ["penalty", "fine", "punishment"],
        }

        tokens = query.split()
        expansions = set()

        for i, token in enumerate(tokens):
            if token in synonym_map:
                for synonym in synonym_map[token]:
                    new_tokens = tokens.copy()
                    new_tokens[i] = synonym
                    expansions.add(" ".join(new_tokens))

        return expansions

    def _expand_legal_terms(self, query: str) -> Set[str]:
        """
        Legal / tribunal-specific expansions.
        """
        legal_map: Dict[str, List[str]] = {
            "tribunal": ["tribunal", "appellate tribunal"],
            "section": ["section", "sec"],
            "act": ["act", "statute"],
            "rule": ["rule", "regulation"],
            "order dated": ["order dated", "order passed on"],
            "assessment year": ["assessment year", "AY"],
        }

        expansions = set()

        for key, variants in legal_map.items():
            if key in query:
                for variant in variants:
                    expansions.add(query.replace(key, variant))

        return expansions

    # -----------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------

    def _normalize(self, query: str) -> str:
        """
        Normalize query for expansion.
        """
        query = query.lower().strip()
        query = re.sub(r"\s+", " ", query)
        return query
