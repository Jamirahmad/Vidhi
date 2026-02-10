"""
Vector Store Manager

Centralized lifecycle manager for vector stores (FAISS, Chroma).
Responsible for initialization, loading, persistence, and safety checks.

Designed for enterprise / legal / tribunal-grade RAG systems.
"""

from __future__ import annotations

import os
from typing import Dict, Optional

from src.utils.logging_utils import get_logger
from src.retrieval.faiss_store import FAISSStore
from src.retrieval.chroma_store import ChromaStore

logger = get_logger(__name__)


# ---------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------

class VectorStoreManagerError(RuntimeError):
    pass


# ---------------------------------------------------------------------
# VectorStoreManager
# ---------------------------------------------------------------------

class VectorStoreManager:
    """
    Manages vector store instances and their lifecycle.
    """

    def __init__(
        self,
        *,
        embedding_dim: int,
        base_path: str = "data/vectorstores",
        enable_faiss: bool = True,
        enable_chroma: bool = False,
        chroma_collection: str = "default",
    ) -> None:
        self.embedding_dim = embedding_dim
        self.base_path = base_path

        self.enable_faiss = enable_faiss
        self.enable_chroma = enable_chroma
        self.chroma_collection = chroma_collection

        self._faiss_store: Optional[FAISSStore] = None
        self._chroma_store: Optional[ChromaStore] = None

        self._validate()
        self._ensure_directories()

        logger.info(
            "VectorStoreManager initialized | faiss=%s | chroma=%s",
            enable_faiss,
            enable_chroma,
        )

    # -----------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------

    def get_faiss_store(self) -> Optional[FAISSStore]:
        if not self.enable_faiss:
            return None

        if not self._faiss_store:
            self._faiss_store = self._load_faiss()

        return self._faiss_store

    def get_chroma_store(self) -> Optional[ChromaStore]:
        if not self.enable_chroma:
            return None

        if not self._chroma_store:
            self._chroma_store = self._load_chroma()

        return self._chroma_store

    def get_active_stores(self) -> Dict[str, object]:
        """
        Returns all enabled vector stores.
        """
        stores = {}

        if self.enable_faiss:
            stores["faiss"] = self.get_faiss_store()

        if self.enable_chroma:
            stores["chroma"] = self.get_chroma_store()

        return stores

    def persist_all(self) -> None:
        """
        Persist all managed vector stores.
        """
        if self._faiss_store:
            self._faiss_store.persist()

        if self._chroma_store:
            self._chroma_store.persist()

        logger.info("All vector stores persisted")

    # -----------------------------------------------------------------
    # Internal Loaders
    # -----------------------------------------------------------------

    def _load_faiss(self) -> FAISSStore:
        path = os.path.join(self.base_path, "faiss")

        try:
            store = FAISSStore(
                embedding_dim=self.embedding_dim,
                index_path=path,
            )
            store.load_or_create()
            logger.info("FAISS store ready | path=%s", path)
            return store
        except Exception as e:
            logger.exception("Failed to initialize FAISS store")
            raise VectorStoreManagerError(str(e)) from e

    def _load_chroma(self) -> ChromaStore:
        path = os.path.join(self.base_path, "chroma")

        try:
            store = ChromaStore(
                persist_directory=path,
                collection_name=self.chroma_collection,
                embedding_dim=self.embedding_dim,
            )
            store.load_or_create()
            logger.info(
                "Chroma store ready | collection=%s",
                self.chroma_collection,
            )
            return store
        except Exception as e:
            logger.exception("Failed to initialize Chroma store")
            raise VectorStoreManagerError(str(e)) from e

    # -----------------------------------------------------------------
    # Validation & Setup
    # -----------------------------------------------------------------

    def _validate(self) -> None:
        if not self.enable_faiss and not self.enable_chroma:
            raise VectorStoreManagerError(
                "At least one vector store must be enabled"
            )

        if self.embedding_dim <= 0:
            raise VectorStoreManagerError("Invalid embedding dimension")

    def _ensure_directories(self) -> None:
        os.makedirs(self.base_path, exist_ok=True)

        if self.enable_faiss:
            os.makedirs(os.path.join(self.base_path, "faiss"), exist_ok=True)

        if self.enable_chroma:
            os.makedirs(os.path.join(self.base_path, "chroma"), exist_ok=True)
