"""
Agent Orchestrator

Coordinates the full legal reasoning pipeline:
LII → LRA → LAF → LAB → CLSA → CCA → DGA

This module focuses on flow control, safety gates, and graceful degradation.
"""

from __future__ import annotations

import time
import traceback
from dataclasses import dataclass
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


@dataclass
class AgentDefinition:
    """
    Internal structure for orchestrator agent registration.
    """
    name: str
    agent: Any
    enabled: bool = True


class AgentOrchestrator:
    """
    Agent Orchestrator is responsible for:
    - Validating incoming request payload
    - Executing agents sequentially (or pipeline style)
    - Collecting intermediate outputs
    - Running post-validation checks (citations, hallucination)
    - Returning standardized response
    """

    def __init__(
        self,
        agents: Optional[List[Any]] = None,
        citation_validator: Optional[CitationValidator] = None,
        hallucination_detector: Optional[HallucinationDetector] = None,
    ):
        self.settings = get_settings()

        self.citation_validator = citation_validator or CitationValidator()
        self.hallucination_detector = hallucination_detector or HallucinationDetector()

        self._agents: List[AgentDefinition] = []

        if agents:
            for agent in agents:
                self.register_agent(agent)

    # -------------------------------------------------------------------------
    # Agent Registration
    # -------------------------------------------------------------------------
    def register_agent(self, agent: Any) -> None:
        """
        Register an agent into orchestrator pipeline.

        Agent must implement:
        - .name (optional)
        - .run(payload: dict) -> dict
        """
        if agent is None:
            raise OrchestratorError("Cannot register None agent")

        agent_name = getattr(agent, "name", agent.__class__.__name__)

        if not hasattr(agent, "run"):
            raise OrchestratorError(f"Agent {agent_name} missing required method: run()")

        self._agents.append(AgentDefinition(name=agent_name, agent=agent))
        logger.info(f"Registered agent: {agent_name}")

    # -------------------------------------------------------------------------
    # Request Validation
    # -------------------------------------------------------------------------
    def _validate_request(self, request: Dict[str, Any]) -> OrchestratorRequest:
        """
        Convert request dict into OrchestratorRequest schema.
        Raises ValidationError if invalid.
        """
        try:
            return OrchestratorRequest.from_dict(request)
        except Exception as e:
            raise ValidationError(f"Invalid orchestrator request payload: {str(e)}") from e

    # -------------------------------------------------------------------------
    # Main Execution
    # -------------------------------------------------------------------------
    def run(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main orchestrator entrypoint.

        Args:
            request: dict payload

        Returns:
            dict response (OrchestratorResponse serialized)
        """
        start_time = time.time()

        try:
            validated_request = self._validate_request(request)
        except ValidationError as ve:
            logger.error(f"Request validation failed: {str(ve)}")
            return OrchestratorResponse.error(
                message="Invalid request payload.",
                error=str(ve),
                execution_time_sec=round(time.time() - start_time, 4),
            ).to_dict()

        logger.info(f"Orchestration started. request_id={validated_request.request_id}")

        agent_results: List[AgentExecutionResult] = []
        context: Dict[str, Any] = validated_request.to_context_dict()

        final_output: Dict[str, Any] = {}
        final_text: str = ""

        # ---------------------------------------------------------------------
        # Agent Pipeline Execution
        # ---------------------------------------------------------------------
        for agent_def in self._agents:
            if not agent_def.enabled:
                logger.warning(f"Skipping disabled agent: {agent_def.name}")
                continue

            logger.info(f"Executing agent: {agent_def.name}")

            agent_start = time.time()

            try:
                agent_response = self._safe_agent_execute(agent_def.agent, context)

                agent_duration = round(time.time() - agent_start, 4)

                agent_result = AgentExecutionResult(
                    agent_name=agent_def.name,
                    success=True,
                    output=agent_response,
                    error=None,
                    execution_time_sec=agent_duration,
                )
                agent_results.append(agent_result)

                # Update context for next agent
                context[f"{agent_def.name}_output"] = agent_response
                context["last_agent_output"] = agent_response

                # Keep most recent answer text if agent provides it
                if isinstance(agent_response, dict):
                    candidate_text = agent_response.get("answer") or agent_response.get("response_text")
                    if isinstance(candidate_text, str) and candidate_text.strip():
                        final_text = candidate_text.strip()

                final_output = agent_response

                logger.info(
                    f"Agent executed successfully: {agent_def.name} in {agent_duration}s"
                )

            except AgentExecutionError as ae:
                agent_duration = round(time.time() - agent_start, 4)

                agent_results.append(
                    AgentExecutionResult(
                        agent_name=agent_def.name,
                        success=False,
                        output={},
                        error=str(ae),
                        execution_time_sec=agent_duration,
                    )
                )

                logger.error(f"Agent failed: {agent_def.name}. Error={str(ae)}")

                # If strict mode enabled, stop pipeline
                if self.settings.ORCHESTRATOR_STRICT_MODE:
                    return OrchestratorResponse.error(
                        message=f"Pipeline stopped due to failure in agent: {agent_def.name}",
                        error=str(ae),
                        agent_results=agent_results,
                        execution_time_sec=round(time.time() - start_time, 4),
                    ).to_dict()

                # Non-strict mode: continue pipeline
                continue

            except Exception as e:
                agent_duration = round(time.time() - agent_start, 4)

                agent_results.append(
                    AgentExecutionResult(
                        agent_name=agent_def.name,
                        success=False,
                        output={},
                        error=f"Unexpected error: {str(e)}",
                        execution_time_sec=agent_duration,
                    )
                )

                logger.error(
                    f"Unexpected exception in agent {agent_def.name}: {str(e)}\n{traceback.format_exc()}"
                )

                if self.settings.ORCHESTRATOR_STRICT_MODE:
                    return OrchestratorResponse.error(
                        message=f"Pipeline stopped due to unexpected error in agent: {agent_def.name}",
                        error=str(e),
                        agent_results=agent_results,
                        execution_time_sec=round(time.time() - start_time, 4),
                    ).to_dict()

        # ---------------------------------------------------------------------
        # If no agent produced output
        # ---------------------------------------------------------------------
        if not final_output:
            logger.warning("Pipeline completed but produced no output.")
            return OrchestratorResponse.error(
                message="No output generated by agents.",
                error="Pipeline returned empty result.",
                agent_results=agent_results,
                execution_time_sec=round(time.time() - start_time, 4),
            ).to_dict()

        # ---------------------------------------------------------------------
        # Post Validation Checks (Citations + Hallucination)
        # ---------------------------------------------------------------------
        citation_result = None
        hallucination_result = None

        if self.settings.ENABLE_CITATION_VALIDATION:
            citation_result = self._run_citation_validation(final_output)

        if self.settings.ENABLE_HALLUCINATION_DETECTION:
            hallucination_result = self._run_hallucination_detection(final_text, context)

        # ---------------------------------------------------------------------
        # Build Final Response
        # ---------------------------------------------------------------------
        response = OrchestratorResponse.success(
            message="Orchestration completed successfully.",
            output=final_output,
            final_answer=final_text,
            agent_results=agent_results,
            citation_validation=citation_result,
            hallucination_validation=hallucination_result,
            execution_time_sec=round(time.time() - start_time, 4),
        )

        logger.info(
            f"Orchestration finished. request_id={validated_request.request_id}, "
            f"time={response.execution_time_sec}s"
        )

        return response.to_dict()

    # -------------------------------------------------------------------------
    # Safe Agent Execution Wrapper
    # -------------------------------------------------------------------------
    def _safe_agent_execute(self, agent: Any, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes agent safely and enforces agent contract.
        """
        if not hasattr(agent, "run"):
            raise AgentExecutionError(f"Agent {agent.__class__.__name__} has no run()")

        try:
            result = agent.run(payload)
        except Exception as e:
            raise AgentExecutionError(
                f"Agent {agent.__class__.__name__} execution failed: {str(e)}"
            ) from e

        if not isinstance(result, dict):
            raise AgentExecutionError(
                f"Agent {agent.__class__.__name__} returned invalid output type. "
                f"Expected dict, got {type(result)}"
            )

        # enforce required keys if expected
        if "status" not in result:
            result["status"] = "success"

        if "agent" not in result:
            result["agent"] = getattr(agent, "name", agent.__class__.__name__)

        return result

    # -------------------------------------------------------------------------
    # Citation Validation
    # -------------------------------------------------------------------------
    def _run_citation_validation(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs citation validation on final output.
        """
        try:
            return self.citation_validator.validate(output)
        except Exception as e:
            logger.error(f"Citation validation failed: {str(e)}")
            return {
                "passed": False,
                "error": f"Citation validator failure: {str(e)}",
            }

    # -------------------------------------------------------------------------
    # Hallucination Detection
    # -------------------------------------------------------------------------
    def _run_hallucination_detection(self, final_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs hallucination detection on final text output.
        """
        if not final_text.strip():
            return {
                "passed": True,
                "risk_score": 0.0,
                "notes": ["No final answer text provided for hallucination detection."],
            }

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
                "error": f"Hallucination detector failure: {str(e)}",
            }
