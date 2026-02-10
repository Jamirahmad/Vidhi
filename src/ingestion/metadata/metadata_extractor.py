"""
Metadata Extractor

Extracts structured, traceable metadata from raw legal documents
before cleaning and chunking.

This module is intentionally conservative:
- extracts only what can be reasonably inferred
- never hallucinates missing values

Aligned with:
- src/ingestion/fetchers/*
- src/ingestion/cleaners/*
- src/ingestion/chunking/*
- src/evaluation/*
"""

from __future__ import annotations

import re
from typing import Dict, Optional

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------
# Regex Patterns (Conservative, Explainable)
# ---------------------------------------------------------------------

CASE_NUMBER_PATTERN = re.compile(
    r"\b(?:Civil|Criminal|Writ|Appeal|SLP|OA|TA)\s*"
    r"(?:No\.?|Number)?\s*\d+\/\d{4}\b",
    re.IGNORECASE,
)

YEAR_PATTERN = re.compile(r"\b(19|20)\d{2}\b")

COURT_PATTERN = re.compile(
    r"(Supreme Court of India|High Court of [A-Za-z ]+)",
    re.IGNORECASE,
)

TRIBUNAL_PATTERN = re.compile(
    r"\b(NCLT|ITAT|CAT|NGT|SAT|APTEL)\b",
    re.IGNORECASE,
)

JUDGE_PATTERN = re.compile(
    r"(Justice|Hon'?ble)\s+[A-Z][A-Za-z .]+",
    re.IGNORECASE,
)

DATE_PATTERN = re.compile(
    r"\b\d{1,2}\s+(January|February|March|April|May|June|July|August|"
    r"September|October|November|December)\s+\d{4}\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------
# Extractor
# ---------------------------------------------------------------------

class MetadataExtractor:
    """
    Extracts metadata from raw text and fetcher metadata.
    """

    @classmethod
    def extract(
        cls,
        *,
        text: str,
        source_metadata: Dict[str, object],
    ) -> Dict[str, object]:
        """
        Extract metadata from document text and merge with source metadata.

        Returns a metadata dict suitable for chunk-level propagation.
        """
        extracted: Dict[str, Optional[object]] = {}

        extracted["case_number"] = cls._extract_case_number(text)
        extracted["decision_year"] = cls._extract_year(text)
        extracted["court"] = cls._extract_court(text, source_metadata)
        extracted["tribunal"] = cls._extract_tribunal(text, source_metadata)
        extracted["decision_date"] = cls._extract_decision_date(text)
        extracted["judges"] = cls._extract_judges(text)

        # Clean out None values
        cleaned_extracted = {
            k: v for k, v in extracted.items() if v is not None
        }

        merged_metadata = {
            **source_metadata,
            **cleaned_extracted,
        }

        logger.debug(
            "Metadata extracted | keys=%s",
            list(cleaned_extracted.keys()),
        )

        return merged_metadata

    # -----------------------------------------------------------------
    # Individual Extractors (Isolated & Testable)
    # -----------------------------------------------------------------

    @staticmethod
    def _extract_case_number(text: str) -> Optional[str]:
        match = CASE_NUMBER_PATTERN.search(text)
        return match.group(0) if match else None

    @staticmethod
    def _extract_year(text: str) -> Optional[int]:
        years = YEAR_PATTERN.findall(text)
        if not years:
            return None
        # Take earliest year mentioned (conservative)
        return int(min(years))

    @staticmethod
    def _extract_court(
        text: str, source_metadata: Dict[str, object]
    ) -> Optional[str]:
        # Prefer source metadata
        if "court" in source_metadata:
            return str(source_metadata["court"])

        match = COURT_PATTERN.search(text)
        return match.group(1) if match else None

    @staticmethod
    def _extract_tribunal(
        text: str, source_metadata: Dict[str, object]
    ) -> Optional[str]:
        if "tribunal" in source_metadata:
            return str(source_metadata["tribunal"])

        match = TRIBUNAL_PATTERN.search(text)
        return match.group(1) if match else None

    @staticmethod
    def _extract_decision_date(text: str) -> Optional[str]:
        match = DATE_PATTERN.search(text)
        return match.group(0) if match else None

    @staticmethod
    def _extract_judges(text: str) -> Optional[list[str]]:
        matches = JUDGE_PATTERN.findall(text)
        if not matches:
            return None

        # Deduplicate while preserving order
        seen = set()
        judges = []
        for judge in matches:
            normalized = judge.strip()
            if normalized not in seen:
                seen.add(normalized)
                judges.append(normalized)

        return judges if judges else None
