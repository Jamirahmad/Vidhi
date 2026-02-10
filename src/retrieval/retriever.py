"""
Retriever

Central orchestration layer for query expansion, embedding,
vector retrieval, and reranking.

Designed for legal / tribunal / enterprise-grade RAG systems.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from src.utils.logging_utils import get_logger
from src.retrieval.embedding_provider import EmbeddingProvider
from src.retrieval.query_expander import QueryExpander
from src.retrieval.reranker import Reranker

logger = get_logger(__name__)


# ---------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------

class RetrieverError(RuntimeError):
    pass


# ---------------------------------------------------------------------
# Retriever
# ---------------------------------------------------------------------

class Retriever:
    """
    High-level retrieval engine.
    """

    def __init__(
        self,
        *,
        embedding_provider: EmbeddingProvider,
        faiss_store=None,
        chroma_store=None,
        query_expander: Optional[QueryExpander] = None,
        reranker: Optional[Reranker] = None,
        top_k: int = 10,
    ) -> None:
        if not faiss_store and not chroma_store:
            raise RetrieverError("At least one vector store must be provided")

        self.embedding_provider = embedding_provider
        self.faiss_store = faiss_store
        self.chroma_store = chroma_store
        self.query_expander = query_expander or QueryExpander()
        self.reranker = reranker or Reranker()
        self.top_k = top_k

        logger.info(
            "Retriever initialized | faiss=%s | chroma=%s | top_k=%s",
            bool(faiss_store),
            bool(chroma_store),
            top_k,
        )

    # -----------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------

    def retrieve(
        self,
        *,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, object]] = None,
    ) -> List[Dict[str, object]]:
        """
        Retrieve documents for a user query.

        Args:
            query: user query
            top_k: optional override
            filters: metadata filters (if supported by backend)

        Returns:
            List of reranked documents.
        """
        top_k = top_k or self.top_k

        logger.debug("Retrieval started | query='%s'", query)

        expanded_queries = self.query_expander.expand(query)

        all_results: List[Dict[str, object]] = []

        for expanded_query in expanded_queries:
            embedding = self.embedding_provider.embed_query(expanded_query)

            if self.faiss_store:
                all_results.extend(
                    self._search_faiss(embedding, top_k, filters)
                )

            if self.chroma_store:
                all_results.extend(
                    self._search_chroma(expanded_query, embedding, top_k, filters)
                )

        deduped = self._deduplicate(all_results)

        reranked = self.reranker.rerank(
            query=query,
            results=deduped,
            top_k=top_k,
        )

        logger.info(
            "Retrieval completed | expanded_queries=%s | results=%s",
            len(expanded_queries),
            len(reranked),
        )

        return reranked

    # -----------------------------------------------------------------
    # Backend Searches
    # -----------------------------------------------------------------

    def _search_faiss(
        self,
        embedding: List[float],
        top_k: int,
        filters: Optional[Dict[str, object]],
    ) -> List[Dict[str, object]]:
        """
        FAISS search.
        """
        try:
            return self.faiss_store.search(
                embedding=embedding,
                top_k=top_k,
                filters=filters,
            )
        except Exception as e:
            logger.exception("FAISS search failed")
            raise RetrieverError(str(e)) from e

    def _search_chroma(
        self,
        query: str,
        embedding: List[float],
        top_k: int,
        filters: Optional[Dict[str, object]],
    ) -> List[Dict[str, object]]:
        """
        Chroma search (supports text + embedding).
        """
        try:
            return self.chroma_store.search(
                query=query,
                embedding=embedding,
                top_k=top_k,
                filters=filters,
            )
        except Exception as e:
            logger.exception("Chroma search failed")
            raise RetrieverError(str(e)) from e

    # -----------------------------------------------------------------
    # Utilities
    # -----------------------------------------------------------------

    def _deduplicate(
        self,
        results: List[Dict[str, object]],
    ) -> List[Dict[str, object]]:
        """
        Deduplicate results by document ID.
        Keeps the highest similarity score.
        """
        seen = {}

        for result in results:
            doc_id = result.get("id")
            score = float(result.get("score", 0.0))

            if doc_id not in seen or score > seen[doc_id]["score"]:
                seen[doc_id] = result

        deduped = list(seen.values())

        logger.debug(
            "Deduplicated results | before=%s | after=%s",
            len(results),
            len(deduped),
        )

        return deduped
