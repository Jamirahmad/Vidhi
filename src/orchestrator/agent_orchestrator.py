"""
Agent Orchestrator

Coordinates the full legal reasoning pipeline:
LII → LRA → LAF → LAB → CLSA → CCA → DGA

This module focuses on flow control, safety gates, and graceful degradation.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, Optional

from src.common.schemas import (
    PipelineResponse,
    IssuesOutput,
    ResearchOutput,
    AnalysisOutput,
    ArgumentBuilderOutput,
    CitationCheckOutput,
    ComplianceOutput,
    DocumentDraftOutput,
)

from src.core.config import get_config
from src.validation.citation_validator import CitationValidator
from src.validation.hallucination_detector import HallucinationDetector

# Agents
from src.agents.lii_agent import LIIAgent
from src.agents.lra_agent import LRAAgent
from src.agents.laf_agent import LAFAgent
from src.agents.lab_agent import LABAgent
from src.agents.clsa_agent import CLSAAgent
from src.agents.cca_agent import CCAAgent
from src.agents.dga_agent import DGAAgent


logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Orchestrates Vidhi legal pipeline:

    1. LII  -> Legal Issue Identification
    2. LRA  -> Legal Research
    3. LAF  -> Legal Analysis Framework
    4. LAB  -> Legal Argument Builder
    5. CLSA -> Citation & Legal Source Analyzer
    6. CCA  -> Compliance & Caution Agent
    7. DGA  -> Document Draft Generator

    Improvements applied (based on review):
    - No silent exception swallowing
    - Structured errors captured in response
    - Standardized schema normalization
    - Citation + hallucination validation integrated
    - Fail-fast input validation
    - Config-driven behavior toggles
    """

    def __init__(self):
        self.config = get_config()

        # Agents
        self._lii = LIIAgent()
        self._lra = LRAAgent()
        self._laf = LAFAgent()
        self._lab = LABAgent()
        self._clsa = CLSAAgent()
        self._cca = CCAAgent()
        self._dga = DGAAgent()

        # Validators
        self._citation_validator = CitationValidator()
        self._hallucination_detector = HallucinationDetector()

    def _validate_inputs(
        self,
        case_description: str,
        jurisdiction: str,
        document_type: str,
    ) -> None:
        if not case_description or not case_description.strip():
            raise ValueError("case_description cannot be empty.")

        if not jurisdiction or not jurisdiction.strip():
            raise ValueError("jurisdiction cannot be empty.")

        if not document_type or not document_type.strip():
            raise ValueError("document_type cannot be empty.")

    def run_pipeline(
        self,
        case_description: str,
        jurisdiction: str,
        document_type: str,
        request_id: Optional[str] = None,
        extra_context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Runs the full Vidhi pipeline and returns structured output.

        Returns:
            dict (PipelineResponse serialized)
        """

        self._validate_inputs(case_description, jurisdiction, document_type)

        request_id = request_id or str(uuid.uuid4())
        extra_context = extra_context or {}

        response = PipelineResponse(
            request_id=request_id,
            jurisdiction=jurisdiction,
            document_type=document_type,
            case_description=case_description,
        )

        logger.info(
            f"Starting pipeline | request_id={request_id} | jurisdiction={jurisdiction} | document_type={document_type}"
        )

        # ----------------------------
        # Step 1: LII Agent
        # ----------------------------
        try:
            lii_raw = self._lii.identify_issues(
                case_description=case_description,
                jurisdiction=jurisdiction,
            )
            lii_obj = IssuesOutput(**(lii_raw or {})).normalize()
            response.issues = lii_obj.to_dict()

            logger.info(f"LII completed | primary_issues={len(lii_obj.primary_issues)}")

        except Exception as e:
            logger.exception("LII Agent failed")
            response.add_error(agent="LII", error=str(e), stage="identify_issues")
            response.issues = IssuesOutput().to_dict()

        # ----------------------------
        # Step 2: LRA Agent
        # ----------------------------
        try:
            lra_raw = self._lra.perform_research(
                case_description=case_description,
                jurisdiction=jurisdiction,
                issues=response.issues,
            )
            lra_obj = ResearchOutput(**(lra_raw or {})).normalize()
            response.research = lra_obj.to_dict()

            logger.info(
                f"LRA completed | statutes={len(lra_obj.statutes)} | case_laws={len(lra_obj.case_laws)}"
            )

        except Exception as e:
            logger.exception("LRA Agent failed")
            response.add_error(agent="LRA", error=str(e), stage="perform_research")
            response.research = ResearchOutput().to_dict()

        # ----------------------------
        # Step 3: LAF Agent
        # ----------------------------
        try:
            laf_raw = self._laf.build_analysis_framework(
                case_description=case_description,
                jurisdiction=jurisdiction,
                issues=response.issues,
                research=response.research,
            )
            laf_obj = AnalysisOutput(**(laf_raw or {})).normalize()
            response.analysis = laf_obj.to_dict()

            logger.info(
                f"LAF completed | for={len(laf_obj.arguments_for)} | against={len(laf_obj.arguments_against)}"
            )

        except Exception as e:
            logger.exception("LAF Agent failed")
            response.add_error(agent="LAF", error=str(e), stage="build_analysis_framework")
            response.analysis = AnalysisOutput().to_dict()

        # ----------------------------
        # Step 4: LAB Agent
        # ----------------------------
        try:
            lab_raw = self._lab.build_arguments(
                case_description=case_description,
                jurisdiction=jurisdiction,
                issues=response.issues,
                research=response.research,
                analysis=response.analysis,
            )
            lab_obj = ArgumentBuilderOutput(**(lab_raw or {})).normalize()
            response.arguments = lab_obj.to_dict()

            logger.info(
                f"LAB completed | arguments={len(lab_obj.final_arguments)}"
            )

        except Exception as e:
            logger.exception("LAB Agent failed")
            response.add_error(agent="LAB", error=str(e), stage="build_arguments")
            response.arguments = ArgumentBuilderOutput().to_dict()

        # ----------------------------
        # Step 5: CLSA Agent
        # ----------------------------
        try:
            clsa_raw = self._clsa.analyze_sources(
                jurisdiction=jurisdiction,
                issues=response.issues,
                research=response.research,
                analysis=response.analysis,
                arguments=response.arguments,
            )
            clsa_obj = CitationCheckOutput(**(clsa_raw or {})).normalize()
            response.citations = clsa_obj.to_dict()

            logger.info(
                f"CLSA completed | citations_found={len(clsa_obj.citations_found)}"
            )

        except Exception as e:
            logger.exception("CLSA Agent failed")
            response.add_error(agent="CLSA", error=str(e), stage="analyze_sources")
            response.citations = CitationCheckOutput().to_dict()

        # ----------------------------
        # Step 6: Citation Validation (Heuristic)
        # ----------------------------
        if self.config.enable_citations:
            try:
                full_text = self._merge_for_validation(response)
                citation_result = self._citation_validator.validate(
                    full_text,
                    context={"jurisdiction": jurisdiction},
                )

                if not citation_result.is_valid:
                    response.add_error(
                        agent="CITATION_VALIDATOR",
                        error="Citation validation failed",
                        stage="validate",
                    )

                response.citations["citation_validation"] = {
                    "is_valid": citation_result.is_valid,
                    "citations_found": citation_result.citations_found,
                    "missing_citations": citation_result.missing_citations,
                    "invalid_citations": citation_result.invalid_citations,
                    "notes": citation_result.notes,
                }

                logger.info(
                    f"Citation validation completed | is_valid={citation_result.is_valid}"
                )

            except Exception as e:
                logger.exception("Citation validation failed unexpectedly")
                response.add_error(agent="CITATION_VALIDATOR", error=str(e), stage="validate")

        # ----------------------------
        # Step 7: CCA Agent (Compliance)
        # ----------------------------
        try:
            cca_raw = self._cca.check_compliance(
                case_description=case_description,
                jurisdiction=jurisdiction,
                document_type=document_type,
                issues=response.issues,
                research=response.research,
                analysis=response.analysis,
                arguments=response.arguments,
            )
            cca_obj = ComplianceOutput(**(cca_raw or {})).normalize()
            response.compliance = cca_obj.to_dict()

            logger.info(
                f"CCA completed | warnings={len(cca_obj.compliance_warnings)}"
            )

        except Exception as e:
            logger.exception("CCA Agent failed")
            response.add_error(agent="CCA", error=str(e), stage="check_compliance")
            response.compliance = ComplianceOutput().to_dict()

        # ----------------------------
        # Step 8: DGA Agent (Document Draft)
        # ----------------------------
        try:
            dga_raw = self._dga.generate_document(
                case_description=case_description,
                jurisdiction=jurisdiction,
                document_type=document_type,
                issues=response.issues,
                research=response.research,
                analysis=response.analysis,
                arguments=response.arguments,
                compliance=response.compliance,
                citations=response.citations,
            )
            dga_obj = DocumentDraftOutput(**(dga_raw or {})).normalize()
            response.draft = dga_obj.to_dict()

            logger.info("DGA completed | draft generated successfully")

        except Exception as e:
            logger.exception("DGA Agent failed")
            response.add_error(agent="DGA", error=str(e), stage="generate_document")
            response.draft = DocumentDraftOutput().to_dict()

        # ----------------------------
        # Step 9: Hallucination Detection (Heuristic)
        # ----------------------------
        if self.config.enable_hallucination_detection:
            try:
                draft_text = response.draft.get("document_body", "") or ""
                hallu_result = self._hallucination_detector.detect(
                    draft_text,
                    context={
                        "jurisdiction": jurisdiction,
                        "document_type": document_type,
                    },
                )

                response.draft["hallucination_check"] = {
                    "risk": hallu_result.hallucination_risk,
                    "score": hallu_result.score,
                    "reasons": hallu_result.reasons,
                    "flagged_segments": hallu_result.flagged_segments,
                }

                if hallu_result.hallucination_risk in {"HIGH"}:
                    response.add_error(
                        agent="HALLUCINATION_DETECTOR",
                        error=f"High hallucination risk detected (score={hallu_result.score})",
                        stage="detect",
                    )

                logger.info(
                    f"Hallucination detection completed | risk={hallu_result.hallucination_risk} | score={hallu_result.score}"
                )

            except Exception as e:
                logger.exception("Hallucination detection failed unexpectedly")
                response.add_error(agent="HALLUCINATION_DETECTOR", error=str(e), stage="detect")

        logger.info(f"Pipeline completed | request_id={request_id} | errors={len(response.errors)}")
        return response.to_dict()

    def _merge_for_validation(self, response: PipelineResponse) -> str:
        """
        Merge pipeline sections into a single text body for validators.
        """
        parts = []

        def add_section(title: str, content: Any) -> None:
            if not content:
                return
            parts.append(f"\n--- {title} ---\n")
            parts.append(str(content))

        add_section("ISSUES", response.issues)
        add_section("RESEARCH", response.research)
        add_section("ANALYSIS", response.analysis)
        add_section("ARGUMENTS", response.arguments)

        return "\n".join(parts)
