"""
Chroma Vector Store Abstraction

Provides a thin, controlled interface over ChromaDB
for legal document retrieval.
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional

import chromadb
from chromadb.api.models.Collection import Collection

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------

class VectorStoreError(RuntimeError):
    pass


# ---------------------------------------------------------------------
# Chroma Store
# ---------------------------------------------------------------------

class ChromaStore:
    """
    Abstraction layer over ChromaDB collections.
    """

    def __init__(
        self,
        *,
        persist_directory: str,
        collection_name: str,
        embedding_function,
        distance_metric: str = "cosine",
    ) -> None:
        """
        Args:
            persist_directory: disk location for Chroma persistence
            collection_name: logical collection name
            embedding_function: callable used by Chroma for embeddings
            distance_metric: cosine | l2 | ip
        """
        self._client = chromadb.Client(
            chromadb.Settings(
                persist_directory=persist_directory,
                anonymized_telemetry=False,
            )
        )

        self._collection = self._get_or_create_collection(
            name=collection_name,
            embedding_function=embedding_function,
            distance_metric=distance_metric,
        )

        logger.info(
            "ChromaStore initialized | collection=%s",
            collection_name,
        )

    # -----------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------

    def upsert(
        self,
        *,
        documents: List[str],
        metadatas: List[Dict[str, object]],
        ids: List[str],
    ) -> None:
        """
        Insert or update documents.

        Args:
            documents: chunk texts
            metadatas: metadata per chunk
            ids: stable unique IDs
        """
        if not (len(documents) == len(metadatas) == len(ids)):
            raise ValueError("documents, metadatas and ids must be same length")

        try:
            self._collection.upsert(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
            )
        except Exception as exc:
            logger.exception("Chroma upsert failed")
            raise VectorStoreError("Failed to upsert into Chroma") from exc

        logger.debug("Upserted %s documents", len(documents))

    def query(
        self,
        *,
        query_text: str,
        top_k: int = 5,
        filters: Optional[Dict[str, object]] = None,
    ) -> List[Dict[str, object]]:
        """
        Perform semantic similarity search.

        Args:
            query_text: natural language query
            top_k: number of results
            filters: optional metadata filters

        Returns:
            List of result dictionaries
        """
        try:
            results = self._collection.query(
                query_texts=[query_text],
                n_results=top_k,
                where=filters,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as exc:
            logger.exception("Chroma query failed")
            raise VectorStoreError("Query execution failed") from exc

        return self._format_results(results)

    def count(self) -> int:
        """Return number of stored vectors."""
        return self._collection.count()

    def persist(self) -> None:
        """Force persistence to disk."""
        self._client.persist()
        logger.debug("Chroma persistence flushed")

    # -----------------------------------------------------------------
    # Internals
    # -----------------------------------------------------------------

    def _get_or_create_collection(
        self,
        *,
        name: str,
        embedding_function,
        distance_metric: str,
    ) -> Collection:
        try:
            return self._client.get_or_create_collection(
                name=name,
                embedding_function=embedding_function,
                metadata={"hnsw:space": distance_metric},
            )
        except Exception as exc:
            logger.exception("Collection initialization failed")
            raise VectorStoreError("Failed to initialize Chroma collection") from exc

    @staticmethod
    def _format_results(raw: Dict[str, object]) -> List[Dict[str, object]]:
        """
        Normalize Chroma query output into flat records.
        """
        documents = raw.get("documents", [[]])[0]
        metadatas = raw.get("metadatas", [[]])[0]
        distances = raw.get("distances", [[]])[0]

        results = []
        for doc, meta, score in zip(documents, metadatas, distances):
            results.append(
                {
                    "text": doc,
                    "metadata": meta,
                    "score": score,
                }
            )

        return results
