"""
Base Agent Definition for Vidhi

All agents must inherit from BaseAgent and implement:
- validate_input()
- run()
- validate_output()

This ensures consistency, traceability, and safety across the system.
"""

# src/agents/base_agent.py

from __future__ import annotations

import time
import traceback
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class AgentResult:
    """
    Standard agent result structure.

    Every agent MUST return output in this structure (converted to dict).

    status:
        SUCCESS | FAILED
    """

    status: str
    data: dict[str, Any] = field(default_factory=dict)
    errors: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "data": self.data,
            "errors": self.errors,
            "metadata": self.metadata,
        }


class BaseAgent(ABC):
    """
    Base Agent contract.

    All agents must:
    - implement `_execute(payload: dict) -> dict`
    - use `.run(payload) -> dict` (do not override run unless necessary)
    - return consistent dict output

    The orchestrator expects:
    {
        "status": "SUCCESS" | "FAILED",
        "data": {...},
        "errors": [...],
        "metadata": {...}
    }
    """

    agent_name: str = "BaseAgent"
    agent_version: str = "1.0"

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}

    @abstractmethod
    def _execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Implement agent logic here.
        Must return dict (data payload).
        """
        raise NotImplementedError

    def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Standard execution wrapper with:
        - timing
        - exception handling
        - consistent output format
        """
        start_time = time.time()

        if payload is None:
            payload = {}

        try:
            data = self._execute(payload)

            duration_ms = int((time.time() - start_time) * 1000)

            result = AgentResult(
                status="SUCCESS",
                data=data if isinstance(data, dict) else {"result": data},
                errors=[],
                metadata={
                    "agent": self.agent_name,
                    "version": self.agent_version,
                    "duration_ms": duration_ms,
                },
            )
            return result.to_dict()

        except Exception as ex:
            duration_ms = int((time.time() - start_time) * 1000)

            error_obj = {
                "agent": self.agent_name,
                "error_type": type(ex).__name__,
                "message": str(ex),
                "traceback": traceback.format_exc(),
            }

            result = AgentResult(
                status="FAILED",
                data={},
                errors=[error_obj],
                metadata={
                    "agent": self.agent_name,
                    "version": self.agent_version,
                    "duration_ms": duration_ms,
                },
            )
            return result.to_dict()
