"""
Text Cleaner

Performs safe, deterministic normalization of raw text
from parsers / OCR before downstream processing.

This is a generic cleaner and should be applied before:
- citation_cleaner
- language detection
- chunking

Aligned with:
- src/ingestion/cleaners/*
- src/ingestion/chunking/chunker.py
"""

from __future__ import annotations

import re

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------
# Regex Patterns
# ---------------------------------------------------------------------

CONTROL_CHARS_PATTERN = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F]")
MULTI_SPACE_PATTERN = re.compile(r"[ \t]+")
MULTI_NEWLINE_PATTERN = re.compile(r"\n{3,}")
BROKEN_LINE_PATTERN = re.compile(r"(\w)-\n(\w)")  # OCR hyphen breaks


# ---------------------------------------------------------------------
# Cleaner
# ---------------------------------------------------------------------

class TextCleaner:
    """
    Generic text cleaner for legal and semi-structured documents.
    """

    @staticmethod
    def clean(text: str) -> str:
        """
        Clean raw text safely without altering meaning.
        """
        if not text:
            return text

        original_length = len(text)

        # Remove non-printable control characters
        text = CONTROL_CHARS_PATTERN.sub("", text)

        # Fix OCR line-break hyphenation (e.g., "informa-\ntion")
        text = BROKEN_LINE_PATTERN.sub(r"\1\2", text)

        # Normalize spaces and tabs
        text = MULTI_SPACE_PATTERN.sub(" ", text)

        # Normalize excessive newlines (preserve paragraphs)
        text = MULTI_NEWLINE_PATTERN.sub("\n\n", text)

        cleaned = text.strip()

        if len(cleaned) != original_length:
            logger.debug(
                "Text cleaned | original_len=%s | cleaned_len=%s",
                original_length,
                len(cleaned),
            )

        return cleaned

    @staticmethod
    def clean_lines(lines: list[str]) -> list[str]:
        """
        Clean text line-by-line (useful for OCR or CSV inputs).
        """
        return [TextCleaner.clean(line) for line in lines]

    @staticmethod
    def clean_document(text: str) -> str:
        """
        Alias for clean(), kept for semantic clarity in pipelines.
        """
        return TextCleaner.clean(text)
