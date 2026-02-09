"""
Evaluation Runner

Central orchestration layer for all evaluation tests.
This module coordinates evaluation of agent outputs including:
- Citation accuracy
- Hallucination detection
- Agent consistency checks

Aligned with:
- docs/design/evaluation_strategy.md
- tests/README.md
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from src.config.settings import get_settings
from src.utils.logging_utils import get_logger

from src.evaluation.citation_accuracy_tests import (
    evaluate_citations,
    CitationEvaluationReport,
)

logger = get_logger(__name__)
settings = get_settings()


# ---------------------------------------------------------------------
# Evaluation Report Models
# ---------------------------------------------------------------------

@dataclass
class EvaluationSummary:
    run_id: str
    timestamp: str
    citation_accuracy: Optional[float]
    passed: bool
    failure_reasons: List[str]


@dataclass
class EvaluationRunResult:
    summary: EvaluationSummary
    citation_report: Optional[CitationEvaluationReport]
    raw_inputs: Dict[str, object]


# ---------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------

class EvaluationRunner:
    """
    Orchestrates execution of all evaluation tests for agent outputs.
    """

    def __init__(self) -> None:
        self.settings = settings

    def run(
        self,
        *,
        citations: Optional[List[Dict[str, object]]] = None,
        raw_inputs: Optional[Dict[str, object]] = None,
    ) -> EvaluationRunResult:
        """
        Execute all enabled evaluations and return a unified report.
        """
        run_id = self._generate_run_id()
        timestamp = datetime.utcnow().isoformat()

        logger.info("Starting evaluation run | run_id=%s", run_id)

        failure_reasons: List[str] = []
        citation_report: Optional[CitationEvaluationReport] = None

        # -------------------------------------------------------------
        # Citation Accuracy Evaluation
        # -------------------------------------------------------------
        citation_accuracy: Optional[float] = None

        if self.settings.ENABLE_CITATION_VALIDATION and citations is not None:
            citation_report = evaluate_citations(citations)
            citation_accuracy = citation_report.accuracy

            if citation_accuracy < self.settings.CITATION_CONFIDENCE_THRESHOLD:
                failure_reasons.append(
                    f"Citation accuracy below threshold "
                    f"({citation_accuracy:.2f})"
                )

        # -------------------------------------------------------------
        # Overall Pass / Fail
        # -------------------------------------------------------------
        passed = len(failure_reasons) == 0

        summary = EvaluationSummary(
            run_id=run_id,
            timestamp=timestamp,
            citation_accuracy=citation_accuracy,
            passed=passed,
            failure_reasons=failure_reasons,
        )

        logger.info(
            "Evaluation completed | run_id=%s | passed=%s",
            run_id,
            passed,
        )

        return EvaluationRunResult(
            summary=summary,
            citation_report=citation_report,
            raw_inputs=raw_inputs or {},
        )

    # -----------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------

    @staticmethod
    def _generate_run_id() -> str:
        return f"eval-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
