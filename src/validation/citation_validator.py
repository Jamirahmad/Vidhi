"""
Citation Validator (Validation Layer)

This module is a thin adapter over the core citation validator.
It exists to provide a stable validation-layer import path
without duplicating citation validation logic.
"""
# src/validation/citation_validator.py

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from src.core.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class CitationIssue:
    """
    Represents a citation validation issue.
    """
    issue_type: str
    message: str
    evidence: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "issue_type": self.issue_type,
            "message": self.message,
            "evidence": self.evidence,
        }


class CitationValidator:
    """
    Citation Validator for Vidhi.

    Review-based improvements included:
    - deterministic output schema
    - tolerant parsing (works even if agents return different citation formats)
    - validates presence + format + inline citation matching
    - avoids hard failure (always returns dict)
    """

    INLINE_CITATION_PATTERN = r"\[(\d+)\]"  # example: [1], [2]

    def __init__(self, min_citations_required: int = 1):
        self.min_citations_required = min_citations_required
        self.inline_citation_regex = re.compile(self.INLINE_CITATION_PATTERN)

    # -------------------------------------------------------------------------
    # Main Entry
    # -------------------------------------------------------------------------
    def validate(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates citations in agent output.

        Expected output dict may contain:
        - answer / final_answer / response_text
        - citations: list[dict]
        - sources: list[dict]
        - references: list[dict]

        Returns standardized dict:
        {
            "passed": bool,
            "total_citations": int,
            "inline_citation_count": int,
            "issues": [...],
            "notes": [...]
        }
        """
        if not isinstance(output, dict):
            return {
                "passed": False,
                "total_citations": 0,
                "inline_citation_count": 0,
                "issues": [
                    {
                        "issue_type": "INVALID_OUTPUT_TYPE",
                        "message": f"Expected dict output but got {type(output)}",
                        "evidence": None,
                    }
                ],
                "notes": [],
            }

        answer_text = self._extract_text(output)
        citations = self._extract_citations(output)

        issues: List[CitationIssue] = []
        notes: List[str] = []

        # ---------------------------------------------------------------------
        # Validate citations list existence
        # ---------------------------------------------------------------------
        if not citations:
            issues.append(
                CitationIssue(
                    issue_type="NO_CITATIONS",
                    message="No citations were found in output.",
                    evidence=None,
                )
            )

        # ---------------------------------------------------------------------
        # Validate minimum citations
        # ---------------------------------------------------------------------
        if len(citations) < self.min_citations_required:
            issues.append(
                CitationIssue(
                    issue_type="INSUFFICIENT_CITATIONS",
                    message=f"Expected at least {self.min_citations_required} citations, found {len(citations)}.",
                    evidence=None,
                )
            )

        # ---------------------------------------------------------------------
        # Validate citation fields
        # ---------------------------------------------------------------------
        for idx, c in enumerate(citations, start=1):
            if not isinstance(c, dict):
                issues.append(
                    CitationIssue(
                        issue_type="INVALID_CITATION_FORMAT",
                        message=f"Citation at position {idx} is not a dict.",
                        evidence=str(c),
                    )
                )
                continue

            title = c.get("title") or c.get("name")
            url = c.get("url") or c.get("link")
            source = c.get("source")

            if not title:
                issues.append(
                    CitationIssue(
                        issue_type="MISSING_TITLE",
                        message=f"Citation #{idx} missing title/name.",
                        evidence=str(c),
                    )
                )

            if not url:
                issues.append(
                    CitationIssue(
                        issue_type="MISSING_URL",
                        message=f"Citation #{idx} missing url/link.",
                        evidence=str(c),
                    )
                )

            if url and not self._is_valid_url(url):
                issues.append(
                    CitationIssue(
                        issue_type="INVALID_URL",
                        message=f"Citation #{idx} contains invalid URL.",
                        evidence=str(url),
                    )
                )

            if not source:
                notes.append(f"Citation #{idx} has no explicit source field (optional).")

        # ---------------------------------------------------------------------
        # Inline citation check
        # ---------------------------------------------------------------------
        inline_refs = self._extract_inline_references(answer_text)
        inline_count = len(inline_refs)

        if answer_text.strip():
            if inline_count == 0 and citations:
                issues.append(
                    CitationIssue(
                        issue_type="MISSING_INLINE_REFERENCES",
                        message="Citations exist but no inline references like [1], [2] found in answer text.",
                        evidence=answer_text[:400],
                    )
                )

            # check that inline citations do not exceed citation list size
            max_inline = max(inline_refs) if inline_refs else 0
            if max_inline > len(citations):
                issues.append(
                    CitationIssue(
                        issue_type="INLINE_REFERENCE_OUT_OF_RANGE",
                        message=f"Inline reference [${max_inline}] exists but only {len(citations)} citations provided.",
                        evidence=answer_text[:400],
                    )
                )

        # ---------------------------------------------------------------------
        # Build result
        # ---------------------------------------------------------------------
        passed = len(issues) == 0

        return {
            "passed": passed,
            "total_citations": len(citations),
            "inline_citation_count": inline_count,
            "issues": [i.to_dict() for i in issues],
            "notes": notes,
        }

    # -------------------------------------------------------------------------
    # Extract Helpers
    # -------------------------------------------------------------------------
    def _extract_text(self, output: Dict[str, Any]) -> str:
        """
        Extract response text from output dict.
        """
        text = (
            output.get("final_answer")
            or output.get("answer")
            or output.get("response_text")
            or output.get("text")
            or ""
        )

        if not isinstance(text, str):
            return ""

        return text.strip()

    def _extract_citations(self, output: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract citations from output dict.
        Supports multiple keys to reduce coupling with agent outputs.
        """
        candidates = (
            output.get("citations")
            or output.get("sources")
            or output.get("references")
            or []
        )

        if not isinstance(candidates, list):
            return []

        normalized: List[Dict[str, Any]] = []
        for item in candidates:
            if isinstance(item, dict):
                normalized.append(item)
            else:
                # attempt best-effort conversion
                normalized.append({"raw": str(item)})

        return normalized

    def _extract_inline_references(self, text: str) -> List[int]:
        """
        Extracts inline citation markers like [1], [2].
        Returns list of ints.
        """
        if not text:
            return []

        matches = self.inline_citation_regex.findall(text)
        results: List[int] = []

        for m in matches:
            try:
                results.append(int(m))
            except Exception:
                continue

        return results

    # -------------------------------------------------------------------------
    # URL Validation
    # -------------------------------------------------------------------------
    def _is_valid_url(self, url: str) -> bool:
        """
        Minimal URL validation.
        """
        if not url or not isinstance(url, str):
            return False

        url = url.strip()

        if url.startswith("http://") or url.startswith("https://"):
            return True

        return False
