"""
OCR Parser

Parses OCR engine output into structured text suitable
for cleaning, metadata extraction, and chunking.

This parser assumes OCR has already been performed
(e.g., via Tesseract, cloud OCR, or document AI).

Aligned with:
- src/ingestion/parsers/html_parser.py
- src/ingestion/cleaners/text_cleaner.py
- src/ingestion/metadata/*
"""

from __future__ import annotations

from typing import Iterable, List, Optional, Union

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------

class OCRParser:
    """
    Parser for OCR-extracted text.
    """

    @classmethod
    def parse(
        cls,
        *,
        ocr_text: Union[str, List[str]],
        page_separator: str = "\n\n--- PAGE BREAK ---\n\n",
        preserve_line_breaks: bool = True,
    ) -> str:
        """
        Parse OCR output into structured plain text.

        Args:
            ocr_text:
                - Full OCR text as a string
                - OR list of page-level strings
            page_separator:
                Separator inserted between pages
            preserve_line_breaks:
                Whether to keep OCR line breaks

        Returns:
            Structured plain text
        """
        if not ocr_text:
            return ""

        if isinstance(ocr_text, list):
            pages = [
                cls._parse_page(
                    page_text=page,
                    preserve_line_breaks=preserve_line_breaks,
                )
                for page in ocr_text
                if page and page.strip()
            ]
            parsed_text = page_separator.join(pages)
        else:
            parsed_text = cls._parse_page(
                page_text=ocr_text,
                preserve_line_breaks=preserve_line_breaks,
            )

        logger.debug(
            "OCR parsed | length=%s",
            len(parsed_text),
        )

        return parsed_text.strip()

    # -----------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------

    @staticmethod
    def _parse_page(
        *,
        page_text: str,
        preserve_line_breaks: bool,
    ) -> str:
        """
        Normalize a single OCR page.
        """
        lines = page_text.splitlines()

        normalized_lines: List[str] = []
        for line in lines:
            clean_line = line.rstrip()
            if not clean_line:
                continue

            normalized_lines.append(clean_line)

        if preserve_line_breaks:
            return "\n".join(normalized_lines)

        # Collapse lines into paragraphs
        return " ".join(normalized_lines)
