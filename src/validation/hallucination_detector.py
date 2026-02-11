"""
Hallucination Detector (Validation Layer)

This module aggregates low-level hallucination checks into a single
risk assessment interface expected by agents and tests.

It intentionally contains NO model logic.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from src.core.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class HallucinationSignal:
    """
    Represents one hallucination risk signal detected in the response.
    """
    signal_type: str
    message: str
    evidence: Optional[str] = None
    severity: float = 0.5  # 0.0 to 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "signal_type": self.signal_type,
            "message": self.message,
            "evidence": self.evidence,
            "severity": float(self.severity),
        }


class HallucinationDetector:
    """
    Hallucination Detector (rule-based).

    Review-based improvements:
    - deterministic output schema
    - risk scoring
    - checks for suspicious certainty claims without citations
    - checks for fabricated case-law patterns
    - checks for made-up sections / statute references patterns
    - avoids hard failure (always returns dict)
    """

    CASE_LAW_PATTERN = r"\b[A-Z][a-zA-Z]+ v\. [A-Z][a-zA-Z]+\b"
    YEAR_PATTERN = r"\b(18|19|20)\d{2}\b"

    STATUTE_SECTION_PATTERN = r"\bSection\s+\d+[A-Za-z]?\b"
    ARTICLE_PATTERN = r"\bArticle\s+\d+\b"

    STRONG_ASSERTION_PHRASES = [
        "it is guaranteed",
        "always",
        "never",
        "without any doubt",
        "clearly proves",
        "undeniably",
        "the court will",
        "must be granted",
        "certainly",
        "definitely",
    ]

    UNCERTAIN_PHRASES = [
        "may",
        "might",
        "could",
        "it depends",
        "possible",
        "likely",
        "generally",
    ]

    def __init__(self, risk_threshold: float = 0.65):
        self.risk_threshold = risk_threshold

        self.case_law_regex = re.compile(self.CASE_LAW_PATTERN)
        self.year_regex = re.compile(self.YEAR_PATTERN)
        self.section_regex = re.compile(self.STATUTE_SECTION_PATTERN, re.IGNORECASE)
        self.article_regex = re.compile(self.ARTICLE_PATTERN, re.IGNORECASE)

    # -------------------------------------------------------------------------
    # Main Entry
    # -------------------------------------------------------------------------
    def detect(self, response_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Detect hallucination risk.

        Args:
            response_text: final answer text produced by pipeline
            context: orchestrator context, may contain citations or agent outputs

        Returns standardized dict:
        {
            "passed": bool,
            "risk_score": float,
            "signals": [...],
            "notes": [...]
        }
        """
        if not isinstance(response_text, str):
            return {
                "passed": False,
                "risk_score": 1.0,
                "signals": [
                    {
                        "signal_type": "INVALID_TEXT_TYPE",
                        "message": f"Expected response_text to be str but got {type(response_text)}",
                        "evidence": None,
                        "severity": 1.0,
                    }
                ],
                "notes": [],
            }

        text = response_text.strip()
        if not text:
            return {
                "passed": True,
                "risk_score": 0.0,
                "signals": [],
                "notes": ["Empty response text. No hallucination risk detected."],
            }

        context = context or {}

        citations_present = self._citations_present(context)

        signals: List[HallucinationSignal] = []
        notes: List[str] = []

        # ---------------------------------------------------------------------
        # Signal 1: Strong assertions without citations
        # ---------------------------------------------------------------------
        if not citations_present:
            for phrase in self.STRONG_ASSERTION_PHRASES:
                if phrase.lower() in text.lower():
                    signals.append(
                        HallucinationSignal(
                            signal_type="STRONG_ASSERTION_NO_CITATION",
                            message="Strong assertion language detected without citations.",
                            evidence=phrase,
                            severity=0.8,
                        )
                    )
                    break

        # ---------------------------------------------------------------------
        # Signal 2: Case law mention without citation support
        # ---------------------------------------------------------------------
        case_law_hits = self.case_law_regex.findall(text)
        if case_law_hits and not citations_present:
            signals.append(
                HallucinationSignal(
                    signal_type="CASE_LAW_WITHOUT_CITATIONS",
                    message="Case law style references detected but no citations found.",
                    evidence=", ".join(case_law_hits[:3]),
                    severity=0.85,
                )
            )

        # ---------------------------------------------------------------------
        # Signal 3: Year mentions without citations
        # ---------------------------------------------------------------------
        year_hits = self.year_regex.findall(text)
        if year_hits and not citations_present:
            signals.append(
                HallucinationSignal(
                    signal_type="YEAR_REFERENCE_WITHOUT_CITATIONS",
                    message="Year references detected without citations (possible fabricated events).",
                    evidence="Year reference found",
                    severity=0.6,
                )
            )

        # ---------------------------------------------------------------------
        # Signal 4: Legal sections/articles referenced without citations
        # ---------------------------------------------------------------------
        section_hits = self.section_regex.findall(text)
        article_hits = self.article_regex.findall(text)

        if (section_hits or article_hits) and not citations_present:
            signals.append(
                HallucinationSignal(
                    signal_type="LEGAL_REFERENCE_NO_CITATIONS",
                    message="Legal sections/articles referenced without citations.",
                    evidence=", ".join((section_hits + article_hits)[:5]),
                    severity=0.75,
                )
            )

        # ---------------------------------------------------------------------
        # Signal 5: Very confident "court will" type predictions
        # ---------------------------------------------------------------------
        if "court will" in text.lower() and not citations_present:
            signals.append(
                HallucinationSignal(
                    signal_type="COURT_OUTCOME_ASSERTION",
                    message="Response predicts court outcome with certainty without citations.",
                    evidence="court will",
                    severity=0.85,
                )
            )

        # ---------------------------------------------------------------------
        # Signal 6: Too short response may be incomplete
        # ---------------------------------------------------------------------
        if len(text.split()) < 30:
            notes.append("Response is very short; may be incomplete or lacking reasoning.")
            signals.append(
                HallucinationSignal(
                    signal_type="SHORT_RESPONSE",
                    message="Response may be incomplete due to low word count.",
                    evidence=f"Word count={len(text.split())}",
                    severity=0.3,
                )
            )

        # ---------------------------------------------------------------------
        # Signal 7: Lack of uncertainty markers (overconfidence)
        # ---------------------------------------------------------------------
        uncertainty_found = any(p in text.lower() for p in self.UNCERTAIN_PHRASES)
        if not uncertainty_found and not citations_present:
            signals.append(
                HallucinationSignal(
                    signal_type="NO_UNCERTAINTY_MARKERS",
                    message="No uncertainty language detected in response without citations (overconfident tone).",
                    evidence=None,
                    severity=0.55,
                )
            )

        # ---------------------------------------------------------------------
        # Risk scoring
        # ---------------------------------------------------------------------
        risk_score = self._calculate_risk_score(signals)

        passed = risk_score < self.risk_threshold

        if citations_present:
            notes.append("Citations detected in context; hallucination risk reduced.")

        notes.append(f"Risk threshold={self.risk_threshold}")

        return {
            "passed": passed,
            "risk_score": round(risk_score, 4),
            "signals": [s.to_dict() for s in signals],
            "notes": notes,
        }

    # -------------------------------------------------------------------------
    # Internal Helpers
    # -------------------------------------------------------------------------
    def _calculate_risk_score(self, signals: List[HallucinationSignal]) -> float:
        """
        Risk score is computed as weighted max severity + small additive factor.
        Keeps score bounded between 0 and 1.
        """
        if not signals:
            return 0.0

        max_sev = max(s.severity for s in signals)
        additive = min(0.25, 0.05 * len(signals))  # cap additive impact
        score = min(1.0, max_sev + additive)

        return score

    def _citations_present(self, context: Dict[str, Any]) -> bool:
        """
        Attempts to detect whether citations exist anywhere in the orchestrator context.
        Supports multiple possible keys.
        """
        if not isinstance(context, dict):
            return False

        # Most likely location: last_agent_output
        last = context.get("last_agent_output")
        if isinstance(last, dict):
            for k in ("citations", "sources", "references"):
                if isinstance(last.get(k), list) and len(last.get(k)) > 0:
                    return True

        # Check all agent outputs in context
        for key, value in context.items():
            if isinstance(value, dict):
                for k in ("citations", "sources", "references"):
                    if isinstance(value.get(k), list) and len(value.get(k)) > 0:
                        return True

        return False
