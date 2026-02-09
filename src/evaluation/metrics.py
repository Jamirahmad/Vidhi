"""
Evaluation Metrics

Defines standard metrics and aggregation helpers for
evaluating agent and workflow quality.

This module contains:
- Metric definitions
- Aggregation logic
- Scoring utilities

No orchestration logic belongs here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


# ---------------------------------------------------------------------
# Metric Models
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class Metric:
    """
    Represents a single evaluation metric.
    """
    name: str
    value: float
    max_value: float = 1.0
    description: Optional[str] = None

    @property
    def normalized(self) -> float:
        if self.max_value == 0:
            return 0.0
        return min(self.value / self.max_value, 1.0)


@dataclass
class MetricGroup:
    """
    A group of related metrics (e.g. accuracy, safety, performance).
    """
    name: str
    metrics: List[Metric]

    @property
    def score(self) -> float:
        if not self.metrics:
            return 0.0
        return sum(m.normalized for m in self.metrics) / len(self.metrics)

    def as_dict(self) -> Dict[str, float]:
        return {m.name: m.normalized for m in self.metrics}


# ---------------------------------------------------------------------
# Standard Metric Builders
# ---------------------------------------------------------------------

def citation_accuracy_metric(
    *,
    accuracy: float,
) -> Metric:
    return Metric(
        name="citation_accuracy",
        value=accuracy,
        description="Proportion of valid, retrievable citations",
    )


def hallucination_rate_metric(
    *,
    total_claims: int,
    hallucinated_claims: int,
) -> Metric:
    rate = 0.0
    if total_claims > 0:
        rate = hallucinated_claims / total_claims

    return Metric(
        name="hallucination_rate",
        value=rate,
        description="Fraction of claims flagged as hallucinated",
    )


def latency_metric(
    *,
    total_latency_ms: float,
    max_allowed_ms: Optional[float] = None,
) -> Metric:
    max_value = max_allowed_ms if max_allowed_ms else total_latency_ms

    return Metric(
        name="latency",
        value=total_latency_ms,
        max_value=max_value,
        description="End-to-end workflow latency in milliseconds",
    )


# ---------------------------------------------------------------------
# Composite Scoring
# ---------------------------------------------------------------------

def build_overall_score(
    *,
    accuracy_group: Optional[MetricGroup] = None,
    safety_group: Optional[MetricGroup] = None,
    performance_group: Optional[MetricGroup] = None,
    weights: Optional[Dict[str, float]] = None,
) -> float:
    """
    Build a weighted overall score from metric groups.

    Default weights are conservative and safety-biased.
    """

    weights = weights or {
        "accuracy": 0.4,
        "safety": 0.4,
        "performance": 0.2,
    }

    score = 0.0
    total_weight = 0.0

    if accuracy_group:
        score += accuracy_group.score * weights.get("accuracy", 0)
        total_weight += weights.get("accuracy", 0)

    if safety_group:
        score += safety_group.score * weights.get("safety", 0)
        total_weight += weights.get("safety", 0)

    if performance_group:
        score += performance_group.score * weights.get("performance", 0)
        total_weight += weights.get("performance", 0)

    if total_weight == 0:
        return 0.0

    return score / total_weight
