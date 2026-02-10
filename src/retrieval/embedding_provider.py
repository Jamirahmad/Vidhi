"""
Embedding Provider

Defines a unified interface for generating vector embeddings
used by retrieval systems (e.g., Chroma).

This abstraction allows swapping embedding backends without
changing ingestion or retrieval logic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, List

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------

class EmbeddingError(RuntimeError):
    """Raised when embedding generation fails."""


# ---------------------------------------------------------------------
# Base Provider
# ---------------------------------------------------------------------

class EmbeddingProvider(ABC):
    """
    Abstract base class for embedding providers.
    """

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of documents.
        """
        raise NotImplementedError

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a single query.
        """
        raise NotImplementedError


# ---------------------------------------------------------------------
# Local Sentence-Transformer Provider
# ---------------------------------------------------------------------

class SentenceTransformerProvider(EmbeddingProvider):
    """
    Local embedding provider using sentence-transformers.
    """

    def __init__(
        self,
        *,
        model_name: str = "all-MiniLM-L6-v2",
        normalize: bool = True,
    ) -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise EmbeddingError(
                "sentence-transformers not installed"
            ) from exc

        self.model = SentenceTransformer(model_name)
        self.normalize = normalize

        logger.info(
            "SentenceTransformerProvider initialized | model=%s",
            model_name,
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        try:
            embeddings = self.model.encode(
                texts,
                normalize_embeddings=self.normalize,
                show_progress_bar=False,
            )
            return embeddings.tolist()
        except Exception as exc:
            logger.exception("Document embedding failed")
            raise EmbeddingError("Failed to embed documents") from exc

    def embed_query(self, text: str) -> List[float]:
        if not text:
            raise EmbeddingError("Query text cannot be empty")

        try:
            embedding = self.model.encode(
                text,
                normalize_embeddings=self.normalize,
            )
            return embedding.tolist()
        except Exception as exc:
            logger.exception("Query embedding failed")
            raise EmbeddingError("Failed to embed query") from exc


# ---------------------------------------------------------------------
# OpenAI-Compatible Provider (Optional / Future)
# ---------------------------------------------------------------------

class OpenAIEmbeddingProvider(EmbeddingProvider):
    """
    OpenAI-compatible embedding provider.

    This class is intentionally isolated so it can be removed
    or replaced without affecting the rest of the system.
    """

    def __init__(
        self,
        *,
        client,
        model: str,
    ) -> None:
        self.client = client
        self.model = model

        logger.info(
            "OpenAIEmbeddingProvider initialized | model=%s",
            model,
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts,
            )
            return [item.embedding for item in response.data]
        except Exception as exc:
            logger.exception("OpenAI document embedding failed")
            raise EmbeddingError("Failed to embed documents") from exc

    def embed_query(self, text: str) -> List[float]:
        if not text:
            raise EmbeddingError("Query text cannot be empty")

        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=[text],
            )
            return response.data[0].embedding
        except Exception as exc:
            logger.exception("OpenAI query embedding failed")
            raise EmbeddingError("Failed to embed query") from exc
