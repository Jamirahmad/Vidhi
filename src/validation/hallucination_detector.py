"""
Hallucination Detector (Validation Layer)

This module aggregates low-level hallucination checks into a single
risk assessment interface expected by agents and tests.

It intentionally contains NO model logic.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class HallucinationDetectionResult:
    """
    Structured output for hallucination detection.
    """
    hallucination_risk: str  # LOW / MEDIUM / HIGH
    score: float
    reasons: list[str] = field(default_factory=list)
    flagged_segments: list[str] = field(default_factory=list)


class HallucinationDetector:
    """
    Heuristic hallucination detector for legal content.

    This detector does NOT confirm truth.
    It flags content patterns that typically indicate hallucination risk:
    - strong absolute claims without citations
    - fake-looking citations
    - inconsistent legal phrasing
    - suspicious case numbers
    - overconfident wording

    Intended use:
    - pipeline guardrails
    - warning system before final draft is returned
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

    FAKE_CITATION_PATTERNS = [
        r"\bAIR\s+\d{4}\s+[A-Z]{2,}\s+\d{1,2}\b",          # AIR 2020 SC 1 (too small page number suspicious)
        r"\bMANU/[A-Z]{2,}/0000/\d{4}\b",                  # MANU/SC/0000/2023 suspicious
        r"\b\d{4}\s*\(\d+\)\s*SCC\s*0\b",                  # SCC 0 suspicious
        r"\b\d{4}\s*INSC\s*0\b",                           # INSC 0 suspicious
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
    ]

    GENERIC_HALLUCINATION_PATTERNS = [
        r"\bas per the above case\b",
        r"\bas discussed earlier\b",
        r"\bthe case mentioned above\b",
        r"\bthe statute mentioned above\b",
        r"\bthe law clearly states\b",
        r"\bthe judgement states\b",
    ]

    def __init__(self):
        self._absolute_regex = re.compile("|".join(self.ABSOLUTE_CLAIM_PATTERNS), re.IGNORECASE)
        self._fake_citation_regex = re.compile("|".join(self.FAKE_CITATION_PATTERNS), re.IGNORECASE)
        self._strong_assertion_regex = re.compile("|".join(self.STRONG_LEGAL_ASSERTION_PATTERNS), re.IGNORECASE)
        self._generic_hallu_regex = re.compile("|".join(self.GENERIC_HALLUCINATION_PATTERNS), re.IGNORECASE)

        # Citation regex used to detect if any citations exist at all
        self._citation_regex = re.compile(
            r"(AIR\s+\d{4}\s+[A-Z]{2,}\s+\d+)|(\d{4}\s*\(\d+\)\s*SCC\s*\d+)|(MANU/[A-Z]{2,}/\d{3,4}/\d{4})",
            re.IGNORECASE,
        )

    def detect(
        self,
        text: str,
        context: Optional[dict[str, Any]] = None,
    ) -> HallucinationDetectionResult:
        """
        Detect hallucination risk in legal draft.

        Returns:
            HallucinationDetectionResult
        """
        if not text or not text.strip():
            return HallucinationDetectionResult(
                hallucination_risk="HIGH",
                score=1.0,
                reasons=["Empty response received. High hallucination risk due to missing content."],
                flagged_segments=[],
            )

        reasons = []
        flagged_segments = []

        score = 0.0

        # 1. Absolute claims increase risk
        absolute_matches = self._absolute_regex.findall(text)
        if absolute_matches:
            score += 0.20
            reasons.append("Overconfident/absolute language detected.")
            flagged_segments.extend(list(set(absolute_matches)))

        # 2. Strong legal assertions without citations
        strong_assertions = self._strong_assertion_regex.findall(text)
        citations_present = bool(self._citation_regex.search(text))

        if strong_assertions and not citations_present:
            score += 0.35
            reasons.append("Strong legal assertions present without citations.")
            flagged_segments.extend(list(set(strong_assertions)))

        # 3. Fake-looking citations
        fake_citations = self._fake_citation_regex.findall(text)
        if fake_citations:
            score += 0.40
            reasons.append("Suspicious or malformed citations detected.")
            flagged_segments.extend(list(set(fake_citations)))

        # 4. Generic hallucination phrases
        generic_phrases = self._generic_hallu_regex.findall(text)
        if generic_phrases:
            score += 0.15
            reasons.append("Generic referencing language detected (possible fabricated context).")
            flagged_segments.extend(list(set(generic_phrases)))

        # 5. Context-based heuristics
        if context:
            jurisdiction = str(context.get("jurisdiction", "")).strip().lower()
            if jurisdiction and jurisdiction not in {"india", "indian"}:
                score += 0.05
                reasons.append("Jurisdiction is non-Indian but output patterns appear India-specific.")

        # Clamp score to [0, 1]
        score = max(0.0, min(score, 1.0))

        # Risk bands
        if score >= 0.70:
            risk = "HIGH"
        elif score >= 0.35:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        if not reasons:
            reasons.append("No strong hallucination indicators detected.")

        return HallucinationDetectionResult(
            hallucination_risk=risk,
            score=score,
            reasons=reasons,
            flagged_segments=sorted(set(flagged_segments)),
        )
