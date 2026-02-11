"""
Agent Orchestrator

Coordinates the full legal reasoning pipeline:
LII → LRA → LAF → LAB → CLSA → CCA → DGA

This module focuses on flow control, safety gates, and graceful degradation.
"""

from __future__ import annotations

import time
from dataclasses import asdict
from typing import Any, Optional

from src.common.exceptions import (
    AgentExecutionError,
    PipelineError,
    ValidationError,
)
from src.common.schemas import (
    ComplianceCheckOutput,
    DocumentDraftOutput,
    LegalAnalysisOutput,
    LegalArgumentsOutput,
    LegalIssuesOutput,
    LegalResearchOutput,
    PipelineRequest,
    PipelineResponse,
)
from src.core.logging_config import get_logger
from src.validation.citation_validator import CitationValidator
from src.validation.hallucination_detector import HallucinationDetector

logger = get_logger(__name__)


class AgentOrchestrator:
    """
    Vidhi Pipeline Orchestrator

    Improvements included (based on latest review):
    - Supports agent interface fallback: run() / execute() / invoke() / callable
    - Strict schema validation: outputs must match expected schema
    - Fail-fast on mandatory stages
    - Per-agent execution timing capture
    - Validation is applied on meaningful text, not dict dumps
    - Citation + hallucination validation applied on FINAL DRAFT too
    - Compliance disclaimer enforcement at orchestrator level
    """

    def __init__(
        self,
        lii_agent: Any,
        lra_agent: Any,
        laf_agent: Any,
        lab_agent: Any,
        clsa_agent: Any,
        cca_agent: Any,
        dga_agent: Any,
        citation_validator: Optional[CitationValidator] = None,
        hallucination_detector: Optional[HallucinationDetector] = None,
        *,
        fail_fast: bool = True,
        mandatory_agents: Optional[list[str]] = None,
    ):
        self.lii_agent = lii_agent
        self.lra_agent = lra_agent
        self.laf_agent = laf_agent
        self.lab_agent = lab_agent
        self.clsa_agent = clsa_agent
        self.cca_agent = cca_agent
        self.dga_agent = dga_agent

        self.citation_validator = citation_validator or CitationValidator()
        self.hallucination_detector = hallucination_detector or HallucinationDetector()

        self.fail_fast = fail_fast
        self.mandatory_agents = mandatory_agents or ["LII", "LRA"]

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------
    def run(self, request: PipelineRequest) -> PipelineResponse:
        """
        Execute end-to-end pipeline.

        Returns:
            PipelineResponse
        """
        pipeline_start = time.time()

        response = PipelineResponse(
            request_id=request.request_id,
            status="IN_PROGRESS",
            issues=None,
            research=None,
            analysis=None,
            arguments=None,
            compliance=None,
            draft=None,
            validations={},
            errors=[],
            metadata={
                "execution_time_seconds": None,
                "agent_timings": {},
                "draft_generated": False,
            },
        )

        logger.info(
            "Pipeline started",
            extra={
                "request_id": request.request_id,
                "jurisdiction": request.jurisdiction,
                "document_type": request.document_type,
            },
        )

        # ---------------------------------------------------------------------
        # 1. Issue Identification (LII) - Mandatory
        # ---------------------------------------------------------------------
        response.issues = self._execute_agent(
            agent_code="LII",
            agent=self.lii_agent,
            request=request,
            payload={
                "case_description": request.case_description,
                "jurisdiction": request.jurisdiction,
                "document_type": request.document_type,
                "request_id": request.request_id,
            },
            output_schema=LegalIssuesOutput,
            response=response,
        )

        if self._should_stop(response, "LII"):
            return self._finalize(response, pipeline_start)

        # ---------------------------------------------------------------------
        # 2. Legal Research (LRA) - Mandatory
        # ---------------------------------------------------------------------
        response.research = self._execute_agent(
            agent_code="LRA",
            agent=self.lra_agent,
            request=request,
            payload={
                "case_description": request.case_description,
                "jurisdiction": request.jurisdiction,
                "document_type": request.document_type,
                "issues": self._safe_asdict(response.issues),
                "request_id": request.request_id,
            },
            output_schema=LegalResearchOutput,
            response=response,
        )

        if self._should_stop(response, "LRA"):
            return self._finalize(response, pipeline_start)

        # ---------------------------------------------------------------------
        # 3. Legal Analysis (LAF)
        # ---------------------------------------------------------------------
        response.analysis = self._execute_agent(
            agent_code="LAF",
            agent=self.laf_agent,
            request=request,
            payload={
                "case_description": request.case_description,
                "jurisdiction": request.jurisdiction,
                "document_type": request.document_type,
                "issues": self._safe_asdict(response.issues),
                "research": self._safe_asdict(response.research),
                "request_id": request.request_id,
            },
            output_schema=LegalAnalysisOutput,
            response=response,
        )

        # ---------------------------------------------------------------------
        # 4. Arguments Builder (LAB)
        # ---------------------------------------------------------------------
        response.arguments = self._execute_agent(
            agent_code="LAB",
            agent=self.lab_agent,
            request=request,
            payload={
                "case_description": request.case_description,
                "jurisdiction": request.jurisdiction,
                "document_type": request.document_type,
                "issues": self._safe_asdict(response.issues),
                "research": self._safe_asdict(response.research),
                "analysis": self._safe_asdict(response.analysis),
                "request_id": request.request_id,
            },
            output_schema=LegalArgumentsOutput,
            response=response,
        )

        # ---------------------------------------------------------------------
        # 5. Compliance Check (CLSA)
        # ---------------------------------------------------------------------
        response.compliance = self._execute_agent(
            agent_code="CLSA",
            agent=self.clsa_agent,
            request=request,
            payload={
                "case_description": request.case_description,
                "jurisdiction": request.jurisdiction,
                "document_type": request.document_type,
                "issues": self._safe_asdict(response.issues),
                "research": self._safe_asdict(response.research),
                "analysis": self._safe_asdict(response.analysis),
                "arguments": self._safe_asdict(response.arguments),
                "request_id": request.request_id,
            },
            output_schema=ComplianceCheckOutput,
            response=response,
        )

        # ---------------------------------------------------------------------
        # 6. Validate intermediate text (citation + hallucination)
        # ---------------------------------------------------------------------
        intermediate_text = self._build_validation_text(response)

        response.validations["intermediate_citation_validation"] = (
            self.citation_validator.validate(intermediate_text)
        )

        response.validations["intermediate_hallucination_detection"] = asdict(
            self.hallucination_detector.detect(
                intermediate_text,
                context={
                    "jurisdiction": request.jurisdiction,
                    "document_type": request.document_type,
                    "request_id": request.request_id,
                },
            )
        )

        # If hallucination HIGH at intermediate stage, block draft generation.
        if (
            response.validations["intermediate_hallucination_detection"].get("hallucination_risk")
            == "HIGH"
        ):
            response.status = "FAILED"
            response.errors.append(
                {
                    "stage": "HALLUCINATION_GATE",
                    "error": "High hallucination risk detected in intermediate output. Draft generation blocked.",
                    "details": response.validations["intermediate_hallucination_detection"],
                }
            )
            response.metadata["reason"] = "Hallucination gate blocked draft generation"
            return self._finalize(response, pipeline_start)

        # ---------------------------------------------------------------------
        # 7. Compliance Gate Enforcement
        # ---------------------------------------------------------------------
        if response.compliance and not response.compliance.can_generate_draft:
            response.status = "FAILED"
            response.metadata["reason"] = "Compliance agent blocked draft generation"
            response.errors.append(
                {
                    "stage": "COMPLIANCE_GATE",
                    "error": "Compliance agent blocked draft generation",
                    "details": self._safe_asdict(response.compliance),
                }
            )
            return self._finalize(response, pipeline_start)

        # ---------------------------------------------------------------------
        # 8. Draft Generation (DGA)
        # ---------------------------------------------------------------------
        response.draft = self._execute_agent(
            agent_code="DGA",
            agent=self.dga_agent,
            request=request,
            payload={
                "case_description": request.case_description,
                "jurisdiction": request.jurisdiction,
                "document_type": request.document_type,
                "issues": self._safe_asdict(response.issues),
                "research": self._safe_asdict(response.research),
                "analysis": self._safe_asdict(response.analysis),
                "arguments": self._safe_asdict(response.arguments),
                "compliance": self._safe_asdict(response.compliance),
                "request_id": request.request_id,
            },
            output_schema=DocumentDraftOutput,
            response=response,
        )

        if response.draft:
            response.metadata["draft_generated"] = True

        # ---------------------------------------------------------------------
        # 9. Enforce compliance disclaimer in orchestrator (hard enforcement)
        # ---------------------------------------------------------------------
        if response.draft and response.compliance:
            response.draft = self._enforce_compliance_disclaimer(response.draft, response.compliance)

        # ---------------------------------------------------------------------
        # 10. Validate FINAL DRAFT (most important validation)
        # ---------------------------------------------------------------------
        if response.draft and response.draft.draft_text.strip():
            draft_text = response.draft.draft_text.strip()

            response.validations["draft_citation_validation"] = (
                self.citation_validator.validate(draft_text)
            )

            response.validations["draft_hallucination_detection"] = asdict(
                self.hallucination_detector.detect(
                    draft_text,
                    context={
                        "jurisdiction": request.jurisdiction,
                        "document_type": request.document_type,
                        "request_id": request.request_id,
                    },
                )
            )

            if response.validations["draft_hallucination_detection"].get("hallucination_risk") == "HIGH":
                response.errors.append(
                    {
                        "stage": "FINAL_DRAFT_HALLUCINATION",
                        "error": "High hallucination risk detected in final draft.",
                        "details": response.validations["draft_hallucination_detection"],
                    }
                )

                # Block final success status if draft itself is high risk.
                response.status = "FAILED"
                response.metadata["reason"] = "Final draft hallucination risk is HIGH"
                return self._finalize(response, pipeline_start)

        # ---------------------------------------------------------------------
        # Final Status
        # ---------------------------------------------------------------------
        if response.errors:
            response.status = "PARTIAL_SUCCESS"
        else:
            response.status = "SUCCESS"

        return self._finalize(response, pipeline_start)

    # -------------------------------------------------------------------------
    # Agent Execution Wrapper
    # -------------------------------------------------------------------------
    def _execute_agent(
        self,
        *,
        agent_code: str,
        agent: Any,
        request: PipelineRequest,
        payload: dict[str, Any],
        output_schema: Any,
        response: PipelineResponse,
    ):
        """
        Execute agent with:
        - interface fallback (run/execute/invoke/callable)
        - schema enforcement
        - error capture
        - timing capture
        """
        agent_start = time.time()

        try:
            logger.info(
                f"Executing agent {agent_code}",
                extra={"request_id": request.request_id, "agent": agent_code},
            )

            raw_result = self._invoke_agent(agent, payload)

            if raw_result is None:
                raise AgentExecutionError(
                    agent_name=agent_code,
                    message=f"{agent_code} returned empty output",
                )

            parsed = self._parse_agent_output(
                agent_code=agent_code,
                raw_result=raw_result,
                output_schema=output_schema,
            )

            logger.info(
                f"Agent {agent_code} completed successfully",
                extra={"request_id": request.request_id, "agent": agent_code},
            )

            return parsed

        except Exception as e:
            err = AgentExecutionError(
                agent_name=agent_code,
                message=f"{agent_code} execution failed: {str(e)}",
                original_exception=e,
            )

            logger.error(
                f"Agent {agent_code} failed",
                extra={
                    "request_id": request.request_id,
                    "agent": agent_code,
                    "error": str(e),
                },
            )

            response.errors.append(
                {
                    "stage": agent_code,
                    "error": err.message,
                    "details": err.to_dict(),
                }
            )

            return None

        finally:
            elapsed = round(time.time() - agent_start, 4)
            response.metadata["agent_timings"][agent_code] = elapsed

    def _invoke_agent(self, agent: Any, payload: dict[str, Any]) -> Any:
        """
        Support different agent interfaces.

        Preferred:
            agent.run(payload)

        Fallback:
            agent.execute(payload)
            agent.invoke(payload)
            agent(payload)  (callable)
        """
        if hasattr(agent, "run") and callable(getattr(agent, "run")):
            return agent.run(payload)

        if hasattr(agent, "execute") and callable(getattr(agent, "execute")):
            return agent.execute(payload)

        if hasattr(agent, "invoke") and callable(getattr(agent, "invoke")):
            return agent.invoke(payload)

        if callable(agent):
            return agent(payload)

        raise PipelineError(f"Agent does not support known invocation interface: {agent}")

    def _parse_agent_output(self, *, agent_code: str, raw_result: Any, output_schema: Any):
        """
        Enforce strict schema compliance.

        Agent must return:
        - dict -> converted into schema
        - schema instance -> validated type
        """
        if isinstance(raw_result, dict):
            parsed = output_schema(**raw_result)
        else:
            parsed = raw_result

        if not isinstance(parsed, output_schema):
            raise ValidationError(
                message=f"{agent_code} returned invalid output type. Expected {output_schema.__name__}, got {type(parsed)}",
                error_code="INVALID_AGENT_OUTPUT",
                metadata={"agent": agent_code, "expected_schema": output_schema.__name__},
            )

        return parsed

    # -------------------------------------------------------------------------
    # Validation Helpers
    # -------------------------------------------------------------------------
    def _build_validation_text(self, response: PipelineResponse) -> str:
        """
        Build a clean natural language body for citation + hallucination checks.
        Avoid dumping full dicts or structured objects.
        """
        parts: list[str] = []

        def add_section(title: str, text: Optional[str]):
            if text and str(text).strip():
                parts.append(f"## {title}\n{text.strip()}\n")

        if response.issues:
            add_section("ISSUES", response.issues.summary)

        if response.research:
            add_section("RESEARCH", response.research.summary)

        if response.analysis:
            add_section("LEGAL_ANALYSIS", response.analysis.analysis_text)

        if response.arguments:
            add_section("ARGUMENTS", response.arguments.arguments_text)

        if response.compliance:
            add_section("COMPLIANCE_NOTES", response.compliance.notes)

        return "\n".join(parts).strip()

    def _enforce_compliance_disclaimer(
        self,
        draft: DocumentDraftOutput,
        compliance: ComplianceCheckOutput,
    ) -> DocumentDraftOutput:
        """
        Enforce compliance disclaimer insertion.

        This ensures the pipeline is safe even if DGA ignores compliance notes.
        """
        if not compliance.disclaimer_required:
            return draft

        disclaimer_text = (compliance.disclaimer_text or "").strip()
        if not disclaimer_text:
            disclaimer_text = (
                "Disclaimer: This draft is generated for informational purposes only and does not constitute legal advice."
            )

        draft_text = (draft.draft_text or "").strip()

        # Prevent duplicate disclaimer insertion
        if disclaimer_text.lower() in draft_text.lower():
            return draft

        updated_text = f"{disclaimer_text}\n\n{draft_text}".strip()

        return DocumentDraftOutput(
            draft_text=updated_text,
            format=draft.format,
            metadata=draft.metadata,
        )

    # -------------------------------------------------------------------------
    # Pipeline Stop + Finalization
    # -------------------------------------------------------------------------
    def _should_stop(self, response: PipelineResponse, stage: str) -> bool:
        """
        Stop pipeline if mandatory stage fails (fail-fast enabled).
        """
        if stage not in self.mandatory_agents:
            return False

        stage_failed = any(err.get("stage") == stage for err in response.errors)

        if stage_failed and self.fail_fast:
            response.status = "FAILED"
            response.metadata["reason"] = f"Mandatory stage {stage} failed"
            response.metadata["draft_generated"] = False
            return True

        return False

    def _finalize(self, response: PipelineResponse, pipeline_start: float) -> PipelineResponse:
        """
        Finalize pipeline response with total duration.
        """
        total_duration = round(time.time() - pipeline_start, 4)
        response.metadata["execution_time_seconds"] = total_duration

        logger.info(
            "Pipeline completed",
            extra={
                "request_id": response.request_id,
                "status": response.status,
                "execution_time_seconds": total_duration,
            },
        )

        return response

    def _safe_asdict(self, obj: Any) -> Optional[dict[str, Any]]:
        """
        Convert dataclass to dict safely.
        """
        if obj is None:
            return None
        try:
            return asdict(obj)
        except Exception:
            return None
