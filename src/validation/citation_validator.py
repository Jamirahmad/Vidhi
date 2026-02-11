"""
Citation Validator (Validation Layer)

This module is a thin adapter over the core citation validator.
It exists to provide a stable validation-layer import path
without duplicating citation validation logic.
"""

from __future__ import annotations

import re
from dataclasses import asdict
from typing import Any, Optional

from src.common.schemas import CitationValidationResult


class CitationValidator:
    """
    Citation Validator for legal responses.

    Purpose:
    - Identify if legal output contains citations.
    - Validate citation formatting (basic heuristic checks).
    - Flag suspicious or fake-looking citations.
    - Return a consistent structured response contract.

    Notes:
    - This is NOT a real citation authenticity validator.
    - This only ensures citation presence + pattern sanity.
    """

    # Common Indian legal citation patterns
    CITATION_PATTERNS = [
        # SCC format: (2020) 3 SCC 123 OR 2020 (3) SCC 123
        r"\(?\b\d{4}\)?\s*\(?\d+\)?\s*SCC\s*\d+\b",

        # AIR format: AIR 2020 SC 1234
        r"\bAIR\s+\d{4}\s+[A-Z]{2,}\s+\d+\b",

        # MANU format: MANU/SC/1234/2020
        r"\bMANU/[A-Z]{2,}/\d{3,4}/\d{4}\b",

        # Criminal Appeal No. 123 of 2020
        r"\b(?:Criminal|Civil)\s+Appeal\s+No\.?\s*\d+\s+of\s+\d{4}\b",

        # Writ Petition (C) No. 1234/2021
        r"\bWrit\s+Petition\s*\(.*?\)\s*No\.?\s*\d+\/\d{4}\b",
    ]

    # Suspicious citation patterns (heuristic)
    SUSPICIOUS_PATTERNS = [
        r"\bMANU/[A-Z]{2,}/0000/\d{4}\b",      # MANU/SC/0000/2023 suspicious
        r"\b\d{4}\s*\(\d+\)\s*SCC\s*0\b",      # SCC 0 invalid
        r"\bAIR\s+\d{4}\s+[A-Z]{2,}\s+0\b",    # AIR 2020 SC 0 invalid
    ]

    def __init__(self):
        self._citation_regex = re.compile("|".join(self.CITATION_PATTERNS), re.IGNORECASE)
        self._suspicious_regex = re.compile("|".join(self.SUSPICIOUS_PATTERNS), re.IGNORECASE)

    def validate(self, text: str) -> dict[str, Any]:
        """
        Validate citations in a given text.

        Returns consistent contract:
        {
            "passed": bool,
            "citation_count": int,
            "citations_found": list[str],
            "suspicious_citations": list[str],
            "message": str
        }
        """
        if not text or not text.strip():
            result = CitationValidationResult(
                passed=False,
                citation_count=0,
                citations_found=[],
                suspicious_citations=[],
                message="Empty text provided for citation validation.",
            )
            return asdict(result)

        citations_found = list(set(self._citation_regex.findall(text)))
        suspicious_found = list(set(self._suspicious_regex.findall(text)))

        # Normalize output because regex findall can return tuples sometimes
        citations_found = self._normalize_matches(citations_found)
        suspicious_found = self._normalize_matches(suspicious_found)

        citation_count = len(citations_found)

        # Decision Logic
        if citation_count == 0:
            passed = False
            message = "No legal citations detected in the text."
        elif suspicious_found:
            passed = False
            message = "Suspicious citations detected. Validation failed."
        else:
            passed = True
            message = "Citations detected and appear structurally valid."

        result = CitationValidationResult(
            passed=passed,
            citation_count=citation_count,
            citations_found=sorted(citations_found),
            suspicious_citations=sorted(suspicious_found),
            message=message,
        )

        return asdict(result)

    def _normalize_matches(self, matches: list[Any]) -> list[str]:
        """
        Regex findall may return:
        - list[str]
        - list[tuple[str, ...]]

        Normalize into clean list[str].
        """
        normalized: list[str] = []

        for m in matches:
            if isinstance(m, tuple):
                # pick the first non-empty entry
                chosen = next((x for x in m if x), "")
                if chosen:
                    normalized.append(chosen.strip())
            elif isinstance(m, str):
                if m.strip():
                    normalized.append(m.strip())

        return list(set(normalized))
