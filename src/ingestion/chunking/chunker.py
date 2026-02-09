"""
Text Chunker

Splits documents into overlapping chunks suitable for embedding
and retrieval, while preserving traceable metadata.

Aligned with:
- src/config/settings.py
- docs/design/ingestion_strategy.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

from src.config.settings import get_settings
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)
settings = get_settings()


# ---------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------

@dataclass
class Chunk:
    """
    Represents a single text chunk with metadata.
    """
    text: str
    index: int
    source_id: str
    metadata: Dict[str, object]


# ---------------------------------------------------------------------
# Chunker
# ---------------------------------------------------------------------

class TextChunker:
    """
    Splits text into overlapping chunks using character-based strategy.
    """

    def __init__(
        self,
        *,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ) -> None:
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

    def chunk_text(
        self,
        *,
        text: str,
        source_id: str,
        base_metadata: Dict[str, object] | None = None,
    ) -> List[Chunk]:
        """
        Split a single document into chunks.
        """
        base_metadata = base_metadata or {}
        cleaned_text = self._clean_text(text)

        chunks: List[Chunk] = []
        start = 0
        index = 0
        text_length = len(cleaned_text)

        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            chunk_text = cleaned_text[start:end]

            metadata = {
                **base_metadata,
                "source_id": source_id,
                "chunk_index": index,
                "start_char": start,
                "end_char": end,
            }

            chunks.append(
                Chunk(
                    text=chunk_text,
                    index=index,
                    source_id=source_id,
                    metadata=metadata,
                )
            )

            index += 1
            start = end - self.chunk_overlap

        logger.info(
            "Chunked document | source_id=%s | chunks=%s",
            source_id,
            len(chunks),
        )

        return chunks

    def chunk_documents(
        self,
        *,
        documents: Iterable[Dict[str, object]],
    ) -> List[Chunk]:
        """
        Chunk multiple documents.

        Expected document format:
        {
            "id": str,
            "text": str,
            "metadata": dict
        }
        """
        all_chunks: List[Chunk] = []

        for doc in documents:
            source_id = str(doc["id"])
            text = str(doc["text"])
            metadata = dict(doc.get("metadata", {}))

            chunks = self.chunk_text(
                text=text,
                source_id=source_id,
                base_metadata=metadata,
            )
            all_chunks.extend(chunks)

        logger.info(
            "Chunked %s documents into %s chunks",
            len(list(documents)),
            len(all_chunks),
        )

        return all_chunks


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def _normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


class TextCleaner:
    """
    Simple, deterministic text cleaning suitable for legal documents.
    """

    @staticmethod
    def clean(text: str) -> str:
        return _normalize_whitespace(text)


# Attach cleaner method to chunker (explicit, testable)
TextChunker._clean_text = staticmethod(TextCleaner.clean)
