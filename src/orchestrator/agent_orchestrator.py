"""
Agent Orchestrator

Coordinates the full legal reasoning pipeline:
LII → LRA → LAF → LAB → CLSA → CCA → DGA

This module focuses on flow control, safety gates, and graceful degradation.
"""

from __future__ import annotations

import time
import traceback
from typing import Any, Dict, List, Optional

from src.core.logging_config import get_logger
from src.core.config import get_settings

from src.common.exceptions import (
    OrchestratorError,
    AgentExecutionError,
    ValidationError,
)

from src.common.schemas import (
    OrchestratorRequest,
    OrchestratorResponse,
    AgentExecutionResult,
)

from src.validation.citation_validator import CitationValidator
from src.validation.hallucination_detector import HallucinationDetector

logger = get_logger(__name__)


class AgentOrchestrator:
    """
    Central orchestration engine.

    Responsibilities:
    - Validate request payload into OrchestratorRequest
    - Execute agents sequentially with shared context
    - Enforce agent contract: agent.run(payload)->dict
    - Collect agent execution traces
    - Run citation validation and hallucination detection (optional via config)
    - Return stable OrchestratorResponse schema
    """

    def __init__(
        self,
        agents: Optional[List[Any]] = None,
        citation_validator: Optional[CitationValidator] = None,
        hallucination_detector: Optional[HallucinationDetector] = None,
    ):
        self.settings = get_settings()

        self.agents: List[Any] = agents or []

        self.citation_validator = citation_validator or CitationValidator()
        self.hallucination_detector = hallucination_detector or HallucinationDetector()

    # -------------------------------------------------------------------------
    # Validation
    # -------------------------------------------------------------------------
    def _validate_request(self, request: Dict[str, Any]) -> OrchestratorRequest:
        """
        Converts raw request dict into OrchestratorRequest.
        """
        try:
            return OrchestratorRequest.from_dict(request)
        except Exception as e:
            raise ValidationError(str(e)) from e

    # -------------------------------------------------------------------------
    # Agent Execution
    # -------------------------------------------------------------------------
    def _execute_agent(self, agent: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes agent safely and enforces the contract:
        - must implement .run()
        - must return dict
        """
        agent_name = getattr(agent, "name", agent.__class__.__name__)

        if not hasattr(agent, "run"):
            raise AgentExecutionError(f"Agent '{agent_name}' does not implement run()")

        try:
            result = agent.run(context)
        except Exception as e:
            raise AgentExecutionError(
                f"Agent '{agent_name}' failed during execution: {str(e)}"
            ) from e

        if not isinstance(result, dict):
            raise AgentExecutionError(
                f"Agent '{agent_name}' returned invalid type: {type(result)}. Expected dict."
            )

        # enforce standard keys for consistency
        if "agent" not in result:
            result["agent"] = agent_name

        if "status" not in result:
            result["status"] = "success"

        return result

    # -------------------------------------------------------------------------
    # Post Validation
    # -------------------------------------------------------------------------
    def _run_citation_validation(self, output: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return self.citation_validator.validate(output)
        except Exception as e:
            logger.error(f"Citation validation failed: {str(e)}")
            return {
                "passed": False,
                "error": str(e),
            }

    def _run_hallucination_detection(self, final_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return self.hallucination_detector.detect(
                response_text=final_text,
                context=context,
            )
        except Exception as e:
            logger.error(f"Hallucination detection failed: {str(e)}")
            return {
                "passed": False,
                "risk_score": 1.0,
                "error": str(e),
            }

    # -------------------------------------------------------------------------
    # Main Orchestration Entry
    # -------------------------------------------------------------------------
    def run(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs full pipeline and returns OrchestratorResponse dict.

        Args:
            request: raw request dict

        Returns:
            dict (serialized OrchestratorResponse)
        """
        start_time = time.time()

        try:
            validated_request = self._validate_request(request)
        except ValidationError as e:
            logger.error(f"Request validation failed: {str(e)}")
            return OrchestratorResponse.error(
                message="Invalid request payload.",
                error=str(e),
                execution_time_sec=round(time.time() - start_time, 4),
            ).to_dict()

        logger.info(f"Orchestration started. request_id={validated_request.request_id}")

        context: Dict[str, Any] = validated_request.to_context_dict()
        agent_results: List[AgentExecutionResult] = []

        final_output: Dict[str, Any] = {}
        final_answer_text: str = ""

        # ---------------------------------------------------------------------
        # Execute pipeline agents sequentially
        # ---------------------------------------------------------------------
        for agent in self.agents:
            agent_name = getattr(agent, "name", agent.__class__.__name__)
            agent_start = time.time()

            logger.info(f"Executing agent: {agent_name}")

            try:
                result = self._execute_agent(agent, context)

                exec_time = round(time.time() - agent_start, 4)

                agent_results.append(
                    AgentExecutionResult(
                        agent_name=agent_name,
                        success=True,
                        output=result,
                        error=None,
                        execution_time_sec=exec_time,
                    )
                )

                # store into context for downstream agents
                context[f"{agent_name}_output"] = result
                context["last_agent_output"] = result

                # maintain final output
                final_output = result

                # attempt to extract final textual response
                candidate_text = (
                    result.get("final_answer")
                    or result.get("answer")
                    or result.get("response_text")
                    or result.get("text")
                )

                if isinstance(candidate_text, str) and candidate_text.strip():
                    final_answer_text = candidate_text.strip()

                logger.info(f"Agent {agent_name} executed successfully in {exec_time}s")

            except AgentExecutionError as e:
                exec_time = round(time.time() - agent_start, 4)

                agent_results.append(
                    AgentExecutionResult(
                        agent_name=agent_name,
                        success=False,
                        output={},
                        error=str(e),
                        execution_time_sec=exec_time,
                    )
                )

                logger.error(f"Agent execution failed: {agent_name} error={str(e)}")

                # strict mode: stop immediately
                if getattr(self.settings, "ORCHESTRATOR_STRICT_MODE", False):
                    return OrchestratorResponse.error(
                        message=f"Pipeline failed at agent: {agent_name}",
                        error=str(e),
                        agent_results=agent_results,
                        execution_time_sec=round(time.time() - start_time, 4),
                    ).to_dict()

                # non-strict mode: continue
                continue

            except Exception as e:
                exec_time = round(time.time() - agent_start, 4)

                agent_results.append(
                    AgentExecutionResult(
                        agent_name=agent_name,
                        success=False,
                        output={},
                        error=f"Unexpected error: {str(e)}",
                        execution_time_sec=exec_time,
                    )
                )

                logger.error(
                    f"Unexpected exception in agent {agent_name}: {str(e)}\n{traceback.format_exc()}"
                )

                if getattr(self.settings, "ORCHESTRATOR_STRICT_MODE", False):
                    return OrchestratorResponse.error(
                        message=f"Unexpected pipeline failure at agent: {agent_name}",
                        error=str(e),
                        agent_results=agent_results,
                        execution_time_sec=round(time.time() - start_time, 4),
                    ).to_dict()

        # ---------------------------------------------------------------------
        # Pipeline output check
        # ---------------------------------------------------------------------
        if not final_output:
            logger.warning("Pipeline completed but produced no output.")
            return OrchestratorResponse.error(
                message="No output generated by agents.",
                error="Pipeline returned empty output.",
                agent_results=agent_results,
                execution_time_sec=round(time.time() - start_time, 4),
            ).to_dict()

        # ---------------------------------------------------------------------
        # Post Validations
        # ---------------------------------------------------------------------
        citation_validation = None
        hallucination_validation = None

        if getattr(self.settings, "ENABLE_CITATION_VALIDATION", True):
            citation_validation = self._run_citation_validation(final_output)

        if getattr(self.settings, "ENABLE_HALLUCINATION_DETECTION", True):
            hallucination_validation = self._run_hallucination_detection(final_answer_text, context)

        # ---------------------------------------------------------------------
        # Build final response
        # ---------------------------------------------------------------------
        response = OrchestratorResponse.success(
            message="Orchestration completed successfully.",
            output=final_output,
            final_answer=final_answer_text,
            agent_results=agent_results,
            citation_validation=citation_validation,
            hallucination_validation=hallucination_validation,
            execution_time_sec=round(time.time() - start_time, 4),
        )

        logger.info(
            f"Orchestration finished. request_id={validated_request.request_id}, "
            f"time={response.execution_time_sec}s"
        )

        return response.to_dict()
