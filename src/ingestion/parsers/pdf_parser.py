"""
PDF Parser

Parses text-based PDF documents into structured plain text
for downstream cleaning, metadata extraction, and chunking.

NOTE:
- This parser does NOT perform OCR.
- Scanned PDFs should be routed to OCRParser.

Aligned with:
- src/ingestion/parsers/html_parser.py
- src/ingestion/parsers/ocr_parser.py
- src/ingestion/cleaners/text_cleaner.py
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import List, Optional, Union

from pypdf import PdfReader

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------

class PDFParseError(Exception):
    """Raised when PDF parsing fails."""


# ---------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------

class PDFParser:
    """
    Parser for text-based PDF documents.
    """

    @classmethod
    def parse(
        cls,
        *,
        pdf_source: Union[bytes, str, Path],
        page_separator: str = "\n\n--- PAGE BREAK ---\n\n",
    ) -> str:
        """
        Parse a PDF into structured plain text.

        Args:
            pdf_source:
                - bytes (preferred for uploads)
                - file path (str or Path)
            page_separator:
                Separator inserted between pages

        Returns:
            Extracted plain text
        """
        reader = cls._load_reader(pdf_source)

        pages_text: List[str] = []

        for idx, page in enumerate(reader.pages):
            try:
                text = page.extract_text() or ""
            except Exception as exc:
                logger.warning(
                    "Failed to extract text from PDF page %s: %s",
                    idx,
                    exc,
                )
                text = ""

            if text.strip():
                pages_text.append(text.strip())

        parsed_text = page_separator.join(pages_text)

        logger.debug(
            "PDF parsed | pages=%s | length=%s",
            len(pages_text),
            len(parsed_text),
        )

        return parsed_text

    # -----------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------

    @staticmethod
    def _load_reader(
        pdf_source: Union[bytes, str, Path]
    ) -> PdfReader:
        """
        Load a PdfReader from bytes or file path.
        """
        try:
            if isinstance(pdf_source, bytes):
                return PdfReader(io.BytesIO(pdf_source))

            path = Path(pdf_source)
            if not path.exists():
                raise PDFParseError(f"PDF file not found: {path}")

            return PdfReader(str(path))

        except Exception as exc:
            raise PDFParseError("Failed to load PDF") from exc
