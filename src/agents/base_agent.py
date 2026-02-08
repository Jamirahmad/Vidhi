"""
Base Agent Definition for Vidhi

All agents must inherit from BaseAgent and implement:
- validate_input()
- run()
- validate_output()

This ensures consistency, traceability, and safety across the system.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional
import logging


logger = logging.getLogger(__name__)


class AgentResultStatus:
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"
    UNCERTAIN = "UNCERTAIN"


class BaseAgent(ABC):
    """
    Abstract base class for all Vidhi agents.
    """

    def __init__(self, name: str, requires_human_review: bool = False):
        self.name = name
        self.requires_human_review = requires_human_review

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def execute(self, input_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main execution wrapper for the agent.
        Handles validation, tracing, and error capture.
        """

        context = context or {}
        start_time = datetime.utcnow()

        try:
            self.validate_input(input_data)

            output = self.run(input_data, context)

            self.validate_output(output)

            status = AgentResultStatus.SUCCESS

        except Exception as exc:
            output = {
                "error": str(exc)
            }
            status = AgentResultStatus.FAIL

        end_time = datetime.utcnow()

        trace = self._build_trace(
            status=status,
            input_data=input_data,
            output_data=output,
            start_time=start_time,
            end_time=end_time,
        )

        self._log_trace(trace)

        return {
            "agent": self.name,
            "status": status,
            "output": output,
            "trace": trace,
            "requires_human_review": self.requires_human_review or status != AgentResultStatus.SUCCESS
        }

    # ------------------------------------------------------------------
    # Methods to be implemented by child agents
    # ------------------------------------------------------------------

    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> None:
        """
        Validate required fields and structure of input_data.
        Raise Exception on failure.
        """
        pass

    @abstractmethod
    def run(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Core business logic of the agent.
        """
        pass

    @abstractmethod
    def validate_output(self, output_data: Dict[str, Any]) -> None:
        """
        Validate agent output before passing to next step.
        Raise Exception on failure.
        """
        pass

    # ------------------------------------------------------------------
    # Tracing & Logging
    # ------------------------------------------------------------------

    def _build_trace(
        self,
        status: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        start_time: datetime,
        end_time: datetime,
    ) -> Dict[str, Any]:
        """
        Build a structured trace entry for logging and audit.
        """

        return {
            "timestamp": end_time.isoformat(),
            "agent": self.name,
            "status": status,
            "duration_ms": int((end_time - start_time).total_seconds() * 1000),
            "input_summary": self._safe_summary(input_data),
            "output_summary": self._safe_summary(output_data),
            "requires_human_review": self.requires_human_review,
        }

    def _log_trace(self, trace: Dict[str, Any]) -> None:
        """
        Log agent trace in a consistent format.
        """
        logger.info(trace)

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def _safe_summary(self, data: Dict[str, Any], max_length: int = 500) -> Any:
        """
        Prevents logging large or sensitive payloads.
        """
        try:
            summary = str(data)
            return summary[:max_length]
        except Exception:
            return "<unserializable>"
