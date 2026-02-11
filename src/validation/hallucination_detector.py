"""
Hallucination Detector (Validation Layer)

This module aggregates low-level hallucination checks into a single
risk assessment interface expected by agents and tests.

It intentionally contains NO model logic.
"""

from __future__ import annotations

import re
from dataclasses import asdict
from typing import Any, Optional

from src.common.schemas import HallucinationDetectionResult


class HallucinationDetector:
    """
    Hallucination Detector (Heuristic)

    Purpose:
    - Identify hallucination-like patterns in legal content.
    - Provide risk classification: LOW / MEDIUM / HIGH.
    - Produce consistent schema-based output.

    Important:
    - This detector does NOT verify legal correctness.
    - It flags patterns that are commonly associated with hallucinations:
        * overly confident language
        * missing citations for strong legal claims
        * suspicious citation formatting
        * generic reference to "above case" without details

    Designed for:
    - intermediate pipeline validation
    - final draft validation gate
    """

    ABSOLUTE_CLAIM_PATTERNS = [
        r"\bclearly\b",
        r"\bundoubtedly\b",
        r"\bwithout any doubt\b",
        r"\b100%\b",
        r"\bguaranteed\b",
        r"\bdefinitely\b",
        r"\balways\b",
        r"\bnever\b",
        r"\bno question\b",
        r"\bconclusively\b",
    ]

    STRONG_LEGAL_ASSERTION_PATTERNS = [
        r"\bthe Supreme Court held\b",
        r"\bthe High Court held\b",
        r"\bsettled law\b",
        r"\bestablished principle\b",
        r"\bprecedent\b",
        r"\bdoctrine\b",
        r"\bit is mandatory\b",
        r"\bit is illegal\b",
        r"\bvoid ab initio\b",
        r"\bconstitutional right\b",
        r"\bthere is no exception\b",
    ]

    GENERIC_REFERENCE_PATTERNS = [
        r"\bas per the above case\b",
        r"\bas discussed earlier\b",
        r"\bthe case mentioned above\b",
        r"\bthe judgement mentioned above\b",
        r"\bthe statute mentioned above\b",
        r"\bthe law clearly states\b",
        r"\bthe judgement states\b",
    ]

    # Detect citations at all
    CITATION_PATTERNS = [
        r"\(?\b\d{4}\)?\s*\(?\d+\)?\s*SCC\s*\d+\b",     # SCC citation
        r"\bAIR\s+\d{4}\s+[A-Z]{2,}\s+\d+\b",           # AIR citation
        r"\bMANU/[A-Z]{2,}/\d{3,4}/\d{4}\b",            # MANU citation
    ]

    # Suspicious citations
    SUSPICIOUS_CITATION_PATTERNS = [
        r"\bMANU/[A-Z]{2,}/0000/\d{4}\b",
        r"\b\d{4}\s*\(\d+\)\s*SCC\s*0\b",
        r"\bAIR\s+\d{4}\s+[A-Z]{2,}\s+0\b",
    ]

    def __init__(self):
        self._absolute_regex = re.compile("|".join(self.ABSOLUTE_CLAIM_PATTERNS), re.IGNORECASE)
        self._strong_assertion_regex = re.compile(
            "|".join(self.STRONG_LEGAL_ASSERTION_PATTERNS), re.IGNORECASE
        )
        self._generic_ref_regex = re.compile("|".join(self.GENERIC_REFERENCE_PATTERNS), re.IGNORECASE)

        self._citation_regex = re.compile("|".join(self.CITATION_PATTERNS), re.IGNORECASE)
        self._suspicious_citation_regex = re.compile(
            "|".join(self.SUSPICIOUS_CITATION_PATTERNS), re.IGNORECASE
        )

    def detect(self, text: str, context: Optional[dict[str, Any]] = None) -> HallucinationDetectionResult:
        """
        Detect hallucination risk.

        Args:
            text: input legal text (analysis/arguments/draft)
            context: optional metadata (jurisdiction, request_id, etc.)

        Returns:
            HallucinationDetectionResult
        """
        if not text or not text.strip():
            return HallucinationDetectionResult(
                hallucination_risk="HIGH",
                score=1.0,
                reasons=["Empty response text. High hallucination risk."],
                flagged_segments=[],
            )

        text = text.strip()
        reasons: list[str] = []
        flagged_segments: list[str] = []

        score = 0.0

        # -------------------------------------------------------------
        # 1. Overconfident / absolute language
        # -------------------------------------------------------------
        abs_matches = self._absolute_regex.findall(text)
        if abs_matches:
            score += 0.20
            reasons.append("Overconfident or absolute language detected.")
            flagged_segments.extend(abs_matches)

        # -------------------------------------------------------------
        # 2. Strong legal assertions without citations
        # -------------------------------------------------------------
        strong_matches = self._strong_assertion_regex.findall(text)
        citations_present = bool(self._citation_regex.search(text))

        if strong_matches and not citations_present:
            score += 0.35
            reasons.append("Strong legal assertions found without citations.")
            flagged_segments.extend(strong_matches)

        # -------------------------------------------------------------
        # 3. Generic references ("above case") without context
        # -------------------------------------------------------------
        generic_matches = self._generic_ref_regex.findall(text)
        if generic_matches:
            score += 0.15
            reasons.append("Generic references found without clear legal grounding.")
            flagged_segments.extend(generic_matches)

        # -------------------------------------------------------------
        # 4. Suspicious citations
        # -------------------------------------------------------------
        suspicious_matches = self._suspicious_citation_regex.findall(text)
        if suspicious_matches:
            score += 0.40
            reasons.append("Suspicious citation patterns detected.")
            flagged_segments.extend(suspicious_matches)

        # -------------------------------------------------------------
        # 5. Context-based jurisdiction mismatch heuristic
        # -------------------------------------------------------------
        if context:
            jurisdiction = str(context.get("jurisdiction", "")).strip().lower()
            if jurisdiction and jurisdiction not in {"india", "indian"}:
                # If output contains India-specific citations but jurisdiction isn't India
                if re.search(r"\bSCC\b|\bAIR\b|\bMANU/SC\b", text, re.IGNORECASE):
                    score += 0.10
                    reasons.append(
                        "Possible jurisdiction mismatch: India-specific citation style used for non-Indian jurisdiction."
                    )

        # Clamp score
        score = max(0.0, min(score, 1.0))

        # Risk classification
        if score >= 0.70:
            risk = "HIGH"
        elif score >= 0.35:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        if not reasons:
            reasons.append("No major hallucination indicators detected.")

        # Clean duplicates
        flagged_segments = sorted(set([seg.strip() for seg in flagged_segments if seg.strip()]))

        return HallucinationDetectionResult(
            hallucination_risk=risk,
            score=round(score, 3),
            reasons=reasons,
            flagged_segments=flagged_segments,
        )

    def detect_as_dict(self, text: str, context: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """
        Convenience wrapper for components that want dict output.
        """
        return asdict(self.detect(text, context=context))
