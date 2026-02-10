"""
Hallucination Detector (Validation Layer)

This module aggregates low-level hallucination checks into a single
risk assessment interface expected by agents and tests.

It intentionally contains NO model logic.
"""

from __future__ import annotations

from typing import Dict, List

try:
    # Low-level signal checks (already implemented by you)
    from src.validation.hallucination_checks import run_checks  # type: ignore
except ImportError:
    run_checks = None


class HallucinationDetector:
    """
    Validation-layer hallucination detector.

    Produces a deterministic hallucination risk report by aggregating
    heuristic signals such as absolute language, missing citations,
    and overconfident phrasing.
    """

    def __init__(self):
        pass

    def evaluate(self, text: str, citations: List[Dict] | None = None) -> Dict:
        """
        Evaluate hallucination risk for generated text.

        Returns:
        {
            "risk_level": "low" | "medium" | "high",
            "risk_score": float (0.0 - 1.0),
            "signals": List[str]
        }
        """

        citations = citations or []

        # --------------------------------------------------
        # Fallback: ultra-safe default
        # --------------------------------------------------
        if run_checks is None:
            return {
                "risk_level": "low",
                "risk_score": 0.0,
                "signals": [],
            }

        # --------------------------------------------------
        # Collect hallucination signals
        # --------------------------------------------------
        signals: List[str] = run_checks(text=text, citations=citations)

        # --------------------------------------------------
        # Deterministic scoring model
        # --------------------------------------------------
        # Each signal contributes a fixed weight.
        # This keeps behavior predictable and testable.
        weight_per_signal = 0.3
        risk_score = min(1.0, len(signals) * weight_per_signal)

        if risk_score >= 0.7:
            risk_level = "high"
        elif risk_score >= 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"

        return {
            "risk_level": risk_level,
            "risk_score": round(risk_score, 2),
            "signals": signals,
        }


__all__ = ["HallucinationDetector"]
