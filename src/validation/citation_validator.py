"""
Citation Validator (Validation Layer)

This module is a thin adapter over the core citation validator.
It exists to provide a stable validation-layer import path
without duplicating citation validation logic.
"""

from __future__ import annotations

from typing import Dict, List

try:
    # Preferred: reuse the core implementation
    from src.core.citation_validator import CitationValidator as CoreCitationValidator
except ImportError:
    CoreCitationValidator = None


class CitationValidator:
    """
    Validation-layer citation validator.

    Delegates actual validation logic to src.core.citation_validator
    while enforcing a consistent return schema for tests and agents.
    """

    def __init__(self):
        if CoreCitationValidator is None:
            self._core = None
        else:
            self._core = CoreCitationValidator()

    def validate(self, text: str, citations: List[Dict]) -> Dict:
        """
        Validate citation coverage for the given text.

        Returns a normalized validation report.
        """

        # --------------------------------------------------
        # Fallback: extremely safe default (should never fail)
        # --------------------------------------------------
        if self._core is None:
            return {
                "is_valid": bool(citations),
                "missing_citations": [] if citations else ["No citations provided"],
                "issues": [] if citations else ["Citation list is empty"],
            }

        # --------------------------------------------------
        # Delegate to core implementation
        # --------------------------------------------------
        core_result = self._core.validate(text=text, citations=citations)

        # --------------------------------------------------
        # Normalize output for validation layer
        # --------------------------------------------------
        return {
            "is_valid": core_result.get("is_valid", True),
            "missing_citations": core_result.get("missing_citations", []),
            "issues": core_result.get("issues", []),
        }


__all__ = ["CitationValidator"]
