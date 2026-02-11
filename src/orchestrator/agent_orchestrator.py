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
    HallucinationDetectedError,
    PipelineError,
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
    Full pipeline orchestrator for Vidhi.

    Design goals:
    - Enforce mandatory dependencies (Issue Identification + Research).
    - Keep agent execution isolated with structured error capture.
    - Run validation on meaningful natural language content (not dict dumps).
    - Allow config-driven fail-fast behavior.
    - Ensure compliance output is enforced before drafting.
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
    # Public Orchestration API
    # -------------------------------------------------------------------------
    def run(self, request: PipelineRequest) -> PipelineResponse:
        """
        Execute full legal pipeline.

        Returns:
            PipelineResponse containing all intermediate outputs, validations,
            draft (if generated), errors, and pipeline metadata.
        """
        start_ts = time.time()

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
            metadata={},
        )

        logger.info(
            "Pipeline started",
            extra={"request_id": request.request_id, "jurisdiction": request.jurisdiction},
        )

        # ---------------------------
        # Step 1: Legal Issue Identification (LII)
        # ---------------------------
        issues = self._execute_agent(
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

        if issues:
            response.issues = issues

        if self._should_stop(response, "LII"):
            return self._finalize_failure(response, start_ts)

        # ---------------------------
        # Step 2: Legal Research Agent (LRA)
        # ---------------------------
        research = self._execute_agent(
            agent_code="LRA",
            agent=self.lra_agent,
            request=request,
            payload={
                "case_description": request.case_description,
                "jurisdiction": request.jurisdiction,
                "document_type": request.document_type,
                "issues": asdict(issues) if issues else None,
                "request_id": request.request_id,
            },
            output_schema=LegalResearchOutput,
            response=response,
        )

        if research:
            response.research = research

        if self._should_stop(response, "LRA"):
            return self._finalize_failure(response, start_ts)

        # ---------------------------
        # Step 3: Legal Analysis Agent (LAF)
        # ---------------------------
        analysis = self._execute_agent(
            agent_code="LAF",
            agent=self.laf_agent,
            request=request,
            payload={
                "case_description": request.case_description,
                "jurisdiction": request.jurisdiction,
                "document_type": request.document_type,
                "issues": asdict(response.issues) if response.issues else None,
                "research": asdict(response.research) if response.research else None,
                "request_id": request.request_id,
            },
            output_schema=LegalAnalysisOutput,
            response=response,
        )

        if analysis:
            response.analysis = analysis

        # ---------------------------
        # Step 4: Legal Arguments Builder (LAB)
        # ---------------------------
        arguments = self._execute_agent(
            agent_code="LAB",
            agent=self.lab_agent,
            request=request,
            payload={
                "case_description": request.case_description,
                "jurisdiction": request.jurisdiction,
                "document_type": request.document_type,
                "issues": asdict(response.issues) if response.issues else None,
                "research": asdict(response.research) if response.research else None,
                "analysis": asdict(response.analysis) if response.analysis else None,
                "request_id": request.request_id,
            },
            output_schema=LegalArgumentsOutput,
            response=response,
        )

        if arguments:
            response.arguments = arguments

        # ---------------------------
        # Step 5: Compliance & Safety Agent (CLSA)
        # ---------------------------
        compliance = self._execute_agent(
            agent_code="CLSA",
            agent=self.clsa_agent,
            request=request,
            payload={
                "case_description": request.case_description,
                "jurisdiction": request.jurisdiction,
                "document_type": request.document_type,
                "issues": asdict(response.issues) if response.issues else None,
                "research": asdict(response.research) if response.research else None,
                "analysis": asdict(response.analysis) if response.analysis else None,
                "arguments": asdict(response.arguments) if response.arguments else None,
                "request_id": request.request_id,
            },
            output_schema=ComplianceCheckOutput,
            response=response,
        )

        if compliance:
            response.compliance = compliance

        # ---------------------------
        # Step 6: Citation Check Agent (CCA)
        # ---------------------------
        citation_validation_text = self._build_validation_text(response)
        citation_result = self.citation_validator.validate(citation_validation_text)

        response.validations["citation_validation"] = citation_result

        if not citation_result.get("passed", True):
            response.errors.append(
                {
                    "stage": "CITATION_VALIDATION",
                    "error": "Citation validation failed",
                    "details": citation_result,
                }
            )

        # ---------------------------
        # Step 7: Hallucination Detection
        # ---------------------------
        hallucination_result = self.hallucination_detector.detect(
            citation_validation_text,
            context={
                "jurisdiction": request.jurisdiction,
                "document_type": request.document_type,
                "request_id": request.request_id,
            },
        )

        response.validations["hallucination_detection"] = asdict(hallucination_result)

        if hallucination_result.hallucination_risk == "HIGH":
            response.errors.append(
                {
                    "stage": "HALLUCINATION_DETECTION",
                    "error": "High hallucination risk detected",
                    "details": asdict(hallucination_result),
                }
            )

            # This is a hard safety gate: if hallucination is HIGH, do not draft.
            response.status = "FAILED"
            response.metadata["draft_generated"] = False
            response.metadata["reason"] = "High hallucination risk - draft generation blocked"
            return self._finalize(response, start_ts)

        # ---------------------------
        # Step 8: Enforce Compliance Gate Before Drafting
        # ---------------------------
        if compliance and not compliance.can_generate_draft:
            response.status = "FAILED"
            response.metadata["draft_generated"] = False
            response.metadata["reason"] = "Compliance agent blocked draft generation"
            response.errors.append(
                {
                    "stage": "COMPLIANCE_GATE",
                    "error": "Compliance agent blocked drafting",
                    "details": asdict(compliance),
                }
            )
            return self._finalize(response, start_ts)

        # ---------------------------
        # Step 9: Document Generation Agent (DGA)
        # ---------------------------
        draft = self._execute_agent(
            agent_code="DGA",
            agent=self.dga_agent,
            request=request,
            payload={
                "case_description": request.case_description,
                "jurisdiction": request.jurisdiction,
                "document_type": request.document_type,
                "issues": asdict(response.issues) if response.issues else None,
                "research": asdict(response.research) if response.research else None,
                "analysis": asdict(response.analysis) if response.analysis else None,
                "arguments": asdict(response.arguments) if response.arguments else None,
                "compliance": asdict(response.compliance) if response.compliance else None,
                "request_id": request.request_id,
            },
            output_schema=DocumentDraftOutput,
            response=response,
        )

        if draft:
            response.draft = draft
            response.metadata["draft_generated"] = True

        response.status = "SUCCESS" if not response.errors else "PARTIAL_SUCCESS"
        return self._finalize(response, start_ts)

    # -------------------------------------------------------------------------
    # Internal Helpers
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
        Execute agent with strong error handling + schema validation.
        """
        try:
            logger.info(
                f"Executing agent {agent_code}",
                extra={"request_id": request.request_id, "agent": agent_code},
            )

            raw_result = agent.run(payload)

            if raw_result is None:
                raise AgentExecutionError(
                    agent_name=agent_code,
                    message=f"{agent_code} returned empty output",
                )

            if isinstance(raw_result, dict):
                parsed = output_schema(**raw_result)
            else:
                # Allow agent to return already-parsed schema object
                parsed = raw_result

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

    def _should_stop(self, response: PipelineResponse, stage: str) -> bool:
        """
        Determine if pipeline must stop based on mandatory stage failures.
        """
        if stage not in self.mandatory_agents:
            return False

        stage_failed = any(err.get("stage") == stage for err in response.errors)
        if stage_failed and self.fail_fast:
            response.status = "FAILED"
            response.metadata["reason"] = f"Mandatory stage {stage} failed (fail_fast enabled)"
            return True

        return False

    def _build_validation_text(self, response: PipelineResponse) -> str:
        """
        Build clean natural language text for validation checks.

        Avoid dumping dicts. Prefer text fields from schemas.
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

    def _finalize_failure(self, response: PipelineResponse, start_ts: float) -> PipelineResponse:
        """
        Finalize pipeline in failure mode.
        """
        response.status = "FAILED"
        response.metadata["draft_generated"] = False
        return self._finalize(response, start_ts)

    def _finalize(self, response: PipelineResponse, start_ts: float) -> PipelineResponse:
        """
        Add duration + finalize response.
        """
        duration = round(time.time() - start_ts, 3)
        response.metadata["execution_time_seconds"] = duration

        logger.info(
            "Pipeline completed",
            extra={
                "request_id": response.request_id,
                "status": response.status,
                "duration_seconds": duration,
            },
        )

        return response
