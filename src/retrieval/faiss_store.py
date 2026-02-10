"""
FAISS Vector Store Abstraction

Provides a controlled interface over FAISS for fast
in-memory or disk-backed vector similarity search.

Designed to coexist with ChromaStore and share
the same embedding providers.
"""

from __future__ import annotations

import os
import pickle
from pathlib import Path
from typing import Dict, List, Optional

import faiss
import numpy as np

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------

class FaissStoreError(RuntimeError):
    pass


# ---------------------------------------------------------------------
# FAISS Store
# ---------------------------------------------------------------------

class FaissStore:
    """
    Abstraction layer over FAISS index.
    """

    def __init__(
        self,
        *,
        dim: int,
        index_type: str = "cosine",
        index_path: Optional[str] = None,
    ) -> None:
        """
        Args:
            dim: embedding dimension
            index_type: cosine | l2
            index_path: directory for persistence
        """
        self.dim = dim
        self.index_type = index_type
        self.index_path = Path(index_path) if index_path else None

        self.index = self._create_index(dim, index_type)
        self.metadata: List[Dict[str, object]] = []
        self.ids: List[str] = []

        if self.index_path:
            self._load_if_exists()

        logger.info(
            "FaissStore initialized | dim=%s | type=%s",
            dim,
            index_type,
        )

    # -----------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------

    def add(
        self,
        *,
        embeddings: List[List[float]],
        metadatas: List[Dict[str, object]],
        ids: List[str],
    ) -> None:
        """
        Add vectors to the index.
        """
        if not (len(embeddings) == len(metadatas) == len(ids)):
            raise ValueError("embeddings, metadatas and ids must be same length")

        vectors = self._to_numpy(embeddings)

        try:
            self.index.add(vectors)
        except Exception as exc:
            logger.exception("FAISS add failed")
            raise FaissStoreError("Failed to add vectors") from exc

        self.metadata.extend(metadatas)
        self.ids.extend(ids)

        logger.debug("Added %s vectors to FAISS", len(vectors))

    def search(
        self,
        *,
        query_embedding: List[float],
        top_k: int = 5,
    ) -> List[Dict[str, object]]:
        """
        Perform similarity search.
        """
        query_vec = self._to_numpy([query_embedding])

        try:
            distances, indices = self.index.search(query_vec, top_k)
        except Exception as exc:
            logger.exception("FAISS search failed")
            raise FaissStoreError("Search failed") from exc

        results = []
        for score, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue

            results.append(
                {
                    "id": self.ids[idx],
                    "metadata": self.metadata[idx],
                    "score": float(score),
                }
            )

        return results

    def count(self) -> int:
        return self.index.ntotal

    def persist(self) -> None:
        """
        Persist FAISS index and metadata to disk.
        """
        if not self.index_path:
            return

        self.index_path.mkdir(parents=True, exist_ok=True)

        try:
            faiss.write_index(self.index, str(self.index_path / "index.faiss"))
            with open(self.index_path / "meta.pkl", "wb") as f:
                pickle.dump(
                    {
                        "ids": self.ids,
                        "metadata": self.metadata,
                        "dim": self.dim,
                        "index_type": self.index_type,
                    },
                    f,
                )
        except Exception as exc:
            logger.exception("FAISS persistence failed")
            raise FaissStoreError("Failed to persist FAISS index") from exc

        logger.debug("FAISS index persisted")

    # -----------------------------------------------------------------
    # Internals
    # -----------------------------------------------------------------

    def _create_index(self, dim: int, index_type: str):
        if index_type == "cosine":
            index = faiss.IndexFlatIP(dim)
        elif index_type == "l2":
            index = faiss.IndexFlatL2(dim)
        else:
            raise ValueError("index_type must be 'cosine' or 'l2'")

        return index

    def _load_if_exists(self) -> None:
        index_file = self.index_path / "index.faiss"
        meta_file = self.index_path / "meta.pkl"

        if not index_file.exists() or not meta_file.exists():
            return

        try:
            self.index = faiss.read_index(str(index_file))
            with open(meta_file, "rb") as f:
                payload = pickle.load(f)

            self.ids = payload["ids"]
            self.metadata = payload["metadata"]

            logger.info(
                "Loaded FAISS index | vectors=%s",
                len(self.ids),
            )
        except Exception as exc:
            logger.exception("Failed to load FAISS index")
            raise FaissStoreError("FAISS index load failed") from exc

    def _to_numpy(self, vectors: List[List[float]]) -> np.ndarray:
        arr = np.array(vectors, dtype="float32")

        if self.index_type == "cosine":
            faiss.normalize_L2(arr)

        return arr
