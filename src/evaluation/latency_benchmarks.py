"""
Latency Benchmarks

Provides utilities to measure and evaluate latency of:
- Individual agents
- Agent stages
- End-to-end workflows

This module is deterministic and infra-agnostic.
It does NOT perform async orchestration itself.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, List, Optional

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------

@dataclass
class LatencyMetric:
    name: str
    duration_ms: float


@dataclass
class LatencyBenchmarkResult:
    total_duration_ms: float
    metrics: List[LatencyMetric]
    passed: bool
    threshold_ms: Optional[float] = None


# ---------------------------------------------------------------------
# Benchmark Context
# ---------------------------------------------------------------------

class LatencyBenchmark:
    """
    Context manager for measuring latency of named stages.

    Example:
        benchmark = LatencyBenchmark()
        with benchmark.track("issue_identification"):
            run_agent()

        result = benchmark.finalize(threshold_ms=3000)
    """

    def __init__(self) -> None:
        self._start_time: float = time.perf_counter()
        self._checkpoints: Dict[str, float] = {}
        self._durations: Dict[str, float] = {}

    def track(self, name: str):
        return _LatencyTracker(self, name)

    def _start(self, name: str) -> None:
        self._checkpoints[name] = time.perf_counter()

    def _end(self, name: str) -> None:
        start = self._checkpoints.get(name)
        if start is None:
            logger.warning("Latency end called without start: %s", name)
            return

        duration = (time.perf_counter() - start) * 1000
        self._durations[name] = duration

    def finalize(self, threshold_ms: Optional[float] = None) -> LatencyBenchmarkResult:
        total_duration = (time.perf_counter() - self._start_time) * 1000

        metrics = [
            LatencyMetric(name=k, duration_ms=v)
            for k, v in self._durations.items()
        ]

        passed = True
        if threshold_ms is not None:
            passed = total_duration <= threshold_ms

        logger.info(
            "Latency benchmark completed | total=%.2fms | stages=%s",
            total_duration,
            len(metrics),
        )

        return LatencyBenchmarkResult(
            total_duration_ms=total_duration,
            metrics=metrics,
            passed=passed,
            threshold_ms=threshold_ms,
        )


# ---------------------------------------------------------------------
# Internal Context Manager
# ---------------------------------------------------------------------

class _LatencyTracker:
    def __init__(self, benchmark: LatencyBenchmark, name: str) -> None:
        self.benchmark = benchmark
        self.name = name

    def __enter__(self):
        self.benchmark._start(self.name)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.benchmark._end(self.name)
        # Do not suppress exceptions
        return False
