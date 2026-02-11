"""
Citation Validator (Validation Layer)

This module is a thin adapter over the core citation validator.
It exists to provide a stable validation-layer import path
without duplicating citation validation logic.
"""

# src/validation/citation_validator.py

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class CitationValidationResult:
    """
    Structured result for citation validation.
    """
    is_valid: bool
    citations_found: list[str] = field(default_factory=list)
    missing_citations: list[str] = field(default_factory=list)
    invalid_citations: list[str] = field(default_factory=list)
    notes: str = ""


class CitationValidator:
    """
    Validates citations in legal outputs.

    This validator checks:
    - Whether citations are present at all
    - Whether the citations follow expected legal patterns
    - Whether the content contains claims without citations

    NOTE:
    This does not confirm the citation exists in the real world.
    It only validates formatting + presence.
    """

    # Basic Indian legal citation patterns
    CASE_CITATION_PATTERNS = [
        r"\bAIR\s+\d{4}\s+[A-Z]{2,}\s+\d+\b",                      # AIR 1995 SC 123
        r"\b\d{4}\s*\(\d+\)\s*SCC\s*\d+\b",                        # 2012 (3) SCC 456
        r"\b\d{4}\s*\(\d+\)\s*CriLJ\s*\d+\b",                      # 2005 (2) CriLJ 1200
        r"\b\d{4}\s*\(\d+\)\s*ALLMR\s*\d+\b",                      # 2010 (4) ALLMR 22
        r"\bMANU/[A-Z]{2,}/\d{3,4}/\d{4}\b",                       # MANU/SC/0123/2011
        r"\b\d{4}\s*INSC\s*\d+\b",                                 # 2024 INSC 123
    ]

    STATUTE_PATTERNS = [
        r"\bSection\s+\d+[A-Z]?\b",                                # Section 420
        r"\bArticle\s+\d+\b",                                      # Article 21
        r"\bIPC\b|\bCrPC\b|\bCPC\b",                               # IPC / CrPC / CPC
        r"\bConstitution of India\b",                              # Constitution of India
        r"\bIndian Penal Code\b",                                  # Indian Penal Code
        r"\bCode of Criminal Procedure\b",                         # Code of Criminal Procedure
        r"\bCode of Civil Procedure\b",                            # Code of Civil Procedure
    ]

    # Claims that generally require citations (heuristic)
    STRONG_CLAIM_PATTERNS = [
        r"\bheld that\b",
        r"\bestablished that\b",
        r"\bsettled law\b",
        r"\bthe Supreme Court\b",
        r"\bthe High Court\b",
        r"\bit is well[- ]settled\b",
        r"\bprecedent\b",
        r"\bdoctrine\b",
        r"\bconstitutional\b",
    ]

    def __init__(self, min_citations_required: int = 1):
        self.min_citations_required = min_citations_required

        self._case_regex = re.compile("|".join(self.CASE_CITATION_PATTERNS), re.IGNORECASE)
        self._statute_regex = re.compile("|".join(self.STATUTE_PATTERNS), re.IGNORECASE)
        self._strong_claim_regex = re.compile("|".join(self.STRONG_CLAIM_PATTERNS), re.IGNORECASE)

    def extract_citations(self, text: str) -> list[str]:
        """
        Extract citations using regex patterns.
        """
        if not text or not text.strip():
            return []

        found = set()

        for match in self._case_regex.findall(text):
            found.add(match.strip())

        for match in self._statute_regex.findall(text):
            found.add(match.strip())

        return sorted(found)

    def validate(self, text: str, context: Optional[dict[str, Any]] = None) -> CitationValidationResult:
        """
        Validate citations inside text.

        Returns:
            CitationValidationResult
        """
        if not text or not text.strip():
            return CitationValidationResult(
                is_valid=False,
                citations_found=[],
                missing_citations=["No text provided for citation validation."],
                notes="Empty output cannot be validated.",
            )

        citations_found = self.extract_citations(text)

        # Determine if strong legal claims exist
        strong_claims_present = bool(self._strong_claim_regex.search(text))

        missing_citations = []
        invalid_citations = []

        # If strong claims exist but no citations exist, flag missing
        if strong_claims_present and len(citations_found) < self.min_citations_required:
            missing_citations.append(
                "Strong legal claims detected but insufficient citations were found."
            )

        # Validate citation formatting heuristically
        # (Here we only detect citations that look malformed)
        # Example malformed: "AIR SC" without year/page
        malformed_patterns = [
            r"\bAIR\s+SC\b",
            r"\bSCC\b",
            r"\bMANU/[A-Z]{2,}\b",
        ]
        malformed_regex = re.compile("|".join(malformed_patterns), re.IGNORECASE)

        for m in malformed_regex.findall(text):
            invalid_citations.append(m.strip())

        # Additional checks based on context (if passed)
        notes = ""
        if context:
            jurisdiction = str(context.get("jurisdiction", "")).strip()
            if jurisdiction and jurisdiction.lower() not in {"india", "indian"}:
                notes = f"Validator currently optimized for Indian legal citations. Jurisdiction: {jurisdiction}"

        is_valid = True

        if missing_citations:
            is_valid = False

        if invalid_citations:
            is_valid = False

        return CitationValidationResult(
            is_valid=is_valid,
            citations_found=citations_found,
            missing_citations=missing_citations,
            invalid_citations=sorted(set(invalid_citations)),
            notes=notes,
        )
