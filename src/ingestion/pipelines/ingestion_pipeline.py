"""
Ingestion Pipeline

Orchestrates the full ingestion flow:
fetch → parse → clean → extract metadata → chunk

This pipeline is the single entry-point for all document ingestion.

Aligned with:
- src/ingestion/fetchers/*
- src/ingestion/parsers/*
- src/ingestion/cleaners/*
- src/ingestion/metadata/*
- src/ingestion/chunking/*
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from src.utils.logging_utils import get_logger

# Fetchers produce raw records
# Parsers convert raw content to text
from src.ingestion.parsers.html_parser import HTMLParser
from src.ingestion.parsers.pdf_parser import PDFParser
from src.ingestion.parsers.ocr_parser import OCRParser

# Cleaners
from src.ingestion.cleaners.text_cleaner import TextCleaner
from src.ingestion.cleaners.citation_cleaner import CitationCleaner
from src.ingestion.cleaners.language_detector import detect_language_metadata

# Metadata
from src.ingestion.metadata.metadata_extractor import MetadataExtractor

# Chunking
from src.ingestion.chunking.chunker import Chunker

logger = get_logger(__name__)


# ---------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------

class IngestionPipelineError(Exception):
    """Raised for unrecoverable ingestion pipeline failures."""


# ---------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------

class IngestionPipeline:
    """
    End-to-end ingestion pipeline.
    """

    def __init__(
        self,
        *,
        chunker: Optional[Chunker] = None,
    ) -> None:
        self.chunker = chunker or Chunker()

    # -----------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------

    def ingest_records(
        self,
        *,
        records: Iterable[Dict[str, object]],
    ) -> List[Dict[str, object]]:
        """
        Ingest multiple raw records and return chunked documents.
        """
        all_chunks: List[Dict[str, object]] = []

        for record in records:
            try:
                chunks = self.ingest_record(record=record)
                all_chunks.extend(chunks)
            except IngestionPipelineError as exc:
                logger.error(str(exc))
                continue

        return all_chunks

    def ingest_record(
        self,
        *,
        record: Dict[str, object],
    ) -> List[Dict[str, object]]:
        """
        Ingest a single raw record.
        """
        logger.info(
            "Ingesting record | source=%s | id=%s",
            record.get("source"),
            record.get("id"),
        )

        # 1️⃣ Parse
        text = self._parse_record(record)

        if not text or not text.strip():
            raise IngestionPipelineError(
                f"No text extracted for record {record.get('id')}"
            )

        # 2️⃣ Clean (order matters)
        text = TextCleaner.clean_document(text)
        text = CitationCleaner.clean(text)

        # 3️⃣ Language detection (metadata only)
        language_meta = detect_language_metadata(text)

        # 4️⃣ Metadata extraction
        source_metadata = record.get("metadata", {})
        source_metadata.update(language_meta)

        metadata = MetadataExtractor.extract(
            text=text,
            source_metadata=source_metadata,
        )

        # 5️⃣ Chunk
        chunks = self.chunker.chunk(
            text=text,
            base_metadata=metadata,
        )

        logger.info(
            "Ingestion complete | record_id=%s | chunks=%s",
            record.get("id"),
            len(chunks),
        )

        return chunks

    # -----------------------------------------------------------------
    # Parser Routing
    # -----------------------------------------------------------------

    def _parse_record(self, record: Dict[str, object]) -> str:
        """
        Route record to the appropriate parser.
        """
        if "html" in record:
            return HTMLParser.parse(html=record["html"])

        if "bytes" in record:
            mime_type = record.get("metadata", {}).get("mime_type")

            if mime_type == "application/pdf":
                return PDFParser.parse(pdf_source=record["bytes"])

            # Unknown binary → OCR assumed already done upstream
            return OCRParser.parse(ocr_text=record["bytes"].decode(errors="ignore"))

        if "text" in record:
            return str(record["text"])

        raise IngestionPipelineError(
            f"Unsupported record format: {record.keys()}"
        )
