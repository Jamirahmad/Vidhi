"""
Safety Utilities

Shared safety-related helper functions used across validation,
compliance, and quality layers.

All utilities are deterministic and side-effect free.
"""

from __future__ import annotations

from typing import Dict, List


# ---------------------------------------------------------------------
# Risk Scoring Utilities
# ---------------------------------------------------------------------

def compute_risk_score(
    signals: List[str],
    weight_per_signal: float = 0.3,
    max_score: float = 1.0,
) -> float:
    """
    Computes a bounded risk score based on detected signals.

    Each signal contributes a fixed weight.
    """
    score = len(signals) * weight_per_signal
    return round(min(max_score, score), 2)


def map_score_to_risk_level(score: float) -> str:
    """
    Maps a numeric risk score to a qualitative risk level.
    """
    if score >= 0.7:
        return "high"
    if score >= 0.4:
        return "medium"
    return "low"


# ---------------------------------------------------------------------
# Compliance Decision Utilities
# ---------------------------------------------------------------------

def compliance_passes(
    violations: List[str] | None = None,
    risk_level: str | None = None,
) -> bool:
    """
    Determines whether compliance passes based on violations
    and hallucination risk level.
    """
    violations = violations or []

    if violations:
        return False

    if risk_level == "high":
        return False

    return True


def compliance_status(
    violations: List[str] | None = None,
    risk_level: str | None = None,
) -> str:
    """
    Returns a normalized compliance status string.
    """
    return "pass" if compliance_passes(violations, risk_level) else "fail"


# ---------------------------------------------------------------------
# Safety Gate Utilities
# ---------------------------------------------------------------------

def should_block_output(
    compliance_status: str,
    risk_level: str,
) -> bool:
    """
    Determines whether final output should be blocked
    due to safety or compliance concerns.
    """
    if compliance_status == "fail":
        return True
    if risk_level == "high":
        return True
    return False


def safety_notes(
    violations: List[str] | None = None,
    signals: List[str] | None = None,
) -> List[str]:
    """
    Aggregates human-readable safety notes from violations
    and hallucination signals.
    """
    notes: List[str] = []

    for v in violations or []:
        notes.append(f"Compliance violation: {v}")

    for s in signals or []:
        notes.append(f"Hallucination signal detected: {s}")

    return notes


# ---------------------------------------------------------------------
# Public exports
# ---------------------------------------------------------------------

__all__ = [
    "compute_risk_score",
    "map_score_to_risk_level",
    "compliance_passes",
    "compliance_status",
    "should_block_output",
    "safety_notes",
  ]
