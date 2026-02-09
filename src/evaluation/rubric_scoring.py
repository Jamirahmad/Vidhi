"""
Rubric Scoring

Maps evaluation metrics to rubric-based scores and qualitative grades.

This module translates normalized metrics into:
- Rubric bands
- Pass / Needs Review / Fail decisions
- Human-readable explanations

Aligned with:
- docs/design/evaluation_strategy.md
- academic grading + legal QA expectations
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from src.evaluation.metrics import Metric, MetricGroup


# ---------------------------------------------------------------------
# Rubric Models
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class RubricBand:
    name: str
    min_score: float
    description: str


@dataclass
class RubricResult:
    overall_band: RubricBand
    per_category: Dict[str, RubricBand]
    explanations: List[str]


# ---------------------------------------------------------------------
# Default Rubric Definition
# ---------------------------------------------------------------------

DEFAULT_RUBRIC = {
    "Excellent": RubricBand(
        name="Excellent",
        min_score=0.85,
        description="High-quality, reliable output with minimal risk",
    ),
    "Good": RubricBand(
        name="Good",
        min_score=0.70,
        description="Generally correct with minor issues",
    ),
    "Needs Review": RubricBand(
        name="Needs Review",
        min_score=0.50,
        description="Significant issues; human review required",
    ),
    "Fail": RubricBand(
        name="Fail",
        min_score=0.0,
        description="Unsafe or unreliable output",
    ),
}


# ---------------------------------------------------------------------
# Scoring Logic
# ---------------------------------------------------------------------

def score_with_rubric(
    *,
    accuracy_group: MetricGroup,
    safety_group: MetricGroup,
    performance_group: MetricGroup,
    rubric: Dict[str, RubricBand] = DEFAULT_RUBRIC,
) -> RubricResult:
    """
    Assign rubric bands based on metric group scores.
    """

    explanations: List[str] = []

    category_scores = {
        "accuracy": accuracy_group.score,
        "safety": safety_group.score,
        "performance": performance_group.score,
    }

    per_category: Dict[str, RubricBand] = {}

    for category, score in category_scores.items():
        band = _select_band(score, rubric)
        per_category[category] = band

        explanations.append(
            f"{category.title()} score {score:.2f} → {band.name}"
        )

    # Overall band = worst-case category (conservative, legal-safe)
    overall_band = min(
        per_category.values(),
        key=lambda band: band.min_score,
    )

    explanations.append(
        f"Overall evaluation classified as '{overall_band.name}' "
        f"({overall_band.description})"
    )

    return RubricResult(
        overall_band=overall_band,
        per_category=per_category,
        explanations=explanations,
    )


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def _select_band(score: float, rubric: Dict[str, RubricBand]) -> RubricBand:
    """
    Select the highest rubric band whose min_score is satisfied.
    """
    for band in sorted(
        rubric.values(),
        key=lambda b: b.min_score,
        reverse=True,
    ):
        if score >= band.min_score:
            return band

    # Fallback (should never happen)
    return rubric["Fail"]
