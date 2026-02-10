"""
Citation Cleaner

Cleans and normalizes legal citations extracted from documents
(PDF / OCR / HTML) before chunking and retrieval.

Aligned with:
- src/ingestion/chunking/*
- src/evaluation/citation_accuracy_tests.py
- docs/design/ingestion_strategy.md
"""

from __future__ import annotations

import re
from typing import List

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------
# Regex Patterns (Conservative)
# ---------------------------------------------------------------------

MULTI_SPACE_PATTERN = re.compile(r"\s+")
BROKEN_YEAR_PATTERN = re.compile(r"\(\s*(\d{4})\s*\)")
MISPLACED_DOTS_PATTERN = re.compile(r"\.\s*\.")
BROKEN_REPORTER_PATTERN = re.compile(r"(S\s*C\s*C|A\s*I\s*R)")
BROKEN_V_PATTERN = re.compile(r"\bV\s*\.?\s*\b", re.IGNORECASE)


# ---------------------------------------------------------------------
# Cleaner
# ---------------------------------------------------------------------

class CitationCleaner:
    """
    Normalizes citation formatting without altering meaning.
    """

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Apply citation-safe cleaning rules to a block of text.
        """
        original = text

        text = MULTI_SPACE_PATTERN.sub(" ", text)
        text = MISPLACED_DOTS_PATTERN.sub(".", text)

        # Normalize common reporters
        text = BROKEN_REPORTER_PATTERN.sub(
            lambda m: m.group(1).replace(" ", ""), text
        )

        # Normalize Vs / v.
        text = BROKEN_V_PATTERN.sub(" v. ", text)

        # Normalize year formatting
        text = BROKEN_YEAR_PATTERN.sub(r"(\1)", text)

        cleaned = text.strip()

        if cleaned != original:
            logger.debug("Citation text normalized")

        return cleaned

    @staticmethod
    def clean_lines(lines: List[str]) -> List[str]:
        """
        Clean citations line-by-line (useful for OCR output).
        """
        return [CitationCleaner.clean_text(line) for line in lines]

    @staticmethod
    def clean_document(text: str) -> str:
        """
        Clean an entire document while preserving paragraph structure.
        """
        paragraphs = text.split("\n")
        cleaned_paragraphs = [
            CitationCleaner.clean_text(p) for p in paragraphs
        ]
        return "\n".join(cleaned_paragraphs)
