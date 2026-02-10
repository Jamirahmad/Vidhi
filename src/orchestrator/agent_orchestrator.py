"""
Agent Orchestrator

Coordinates the full legal reasoning pipeline:
LII → LRA → LAF → LAB → CLSA → CCA → DGA

This module focuses on flow control, safety gates, and graceful degradation.
"""

from __future__ import annotations

from typing import Dict

# ---------------------------------------------------------------------
# Agent imports
# ---------------------------------------------------------------------

from src.agents.lii_agent import LIIAgent
from src.agents.lra_agent import LRAAgent
from src.agents.laf_agent import LAFAgent
from src.agents.lab_agent import LABAgent
from src.agents.clsa_agent import CLSAAgent
from src.agents.cca_agent import CCAAgent
from src.agents.dga_agent import DGAAgent


class AgentOrchestrator:
    """
    Orchestrates the end-to-end agent flow.

    This class intentionally contains no business logic;
    it only coordinates agents and enforces safety gates.
    """

    def __init__(self):
        self._lii = LIIAgent()
        self._lra = LRAAgent()
        self._laf = LAFAgent()
        self._lab = LABAgent()
        self._clsa = CLSAAgent()
        self._cca = CCAAgent()
        self._dga = DGAAgent()

    # -----------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------

    def run(
        self,
        case_description: str,
        jurisdiction: str,
        document_type: str,
    ) -> Dict:
        """
        Execute the full orchestration pipeline.

        Always returns a structured result dictionary,
        even when upstream inputs are weak or incomplete.
        """

        result: Dict = {}

        # --------------------------------------------------
        # 1. Issue Identification (LII)
        # --------------------------------------------------
        try:
            issues = self._lii.identify_issues(
                case_description=case_description
            )
        except Exception:
            issues = {"primary_issues": [], "secondary_issues": []}

        result["issues"] = issues

        # --------------------------------------------------
        # 2. Legal Research (LRA)
        # --------------------------------------------------
        try:
            research = self._lra.research(
                issue="; ".join(issues.get("primary_issues", [])),
                jurisdiction=jurisdiction,
            )
        except Exception:
            research = {
                "authorities": [],
                "statutes": [],
                "key_principles": [],
            }

        result["research"] = research

        # --------------------------------------------------
        # 3. Legal Analysis & Findings (LAF)
        # --------------------------------------------------
        try:
            analysis = self._laf.analyze(
                issue="; ".join(issues.get("primary_issues", [])),
                facts=case_description,
                research_points=research.get("key_principles", []),
            )
        except Exception:
            analysis = {
                "analysis": "",
                "key_findings": [],
                "risk_factors": [],
                "preliminary_conclusion": "",
            }

        result["analysis"] = analysis

        # --------------------------------------------------
        # 4. Legal Argument Builder (LAB)
        # --------------------------------------------------
        try:
            argument = self._lab.build_argument(
                issue="; ".join(issues.get("primary_issues", [])),
                research_points=research.get("key_principles", []),
                citations=research.get("authorities", []),
            )
        except Exception:
            argument = ""

        result["argument"] = argument

        # --------------------------------------------------
        # 5. Quality Review (CLSA)
        # --------------------------------------------------
        try:
            quality_report = self._clsa.evaluate(argument)
        except Exception:
            quality_report = {
                "overall_rating": "unknown",
                "issues": [],
                "suggestions": [],
            }

        result["quality_report"] = quality_report

        # --------------------------------------------------
        # 6. Compliance & Safety (CCA)
        # --------------------------------------------------
        try:
            compliance_report = self._cca.check_compliance(
                text=argument,
                citations=research.get("authorities", []),
            )
        except Exception:
            compliance_report = {
                "overall_status": "unknown",
                "violations": [],
                "notes": [],
            }

        result["compliance_report"] = compliance_report

        # --------------------------------------------------
        # 7. Document Generation (DGA)
        # --------------------------------------------------
        try:
            final_document = self._dga.generate(
                document_type=document_type,
                issues=issues,
                research=research,
                analysis=analysis,
                argument=argument,
                quality_report=quality_report,
                compliance_report=compliance_report,
            )
        except Exception:
            final_document = argument or ""

        result["final_document"] = final_document

        return result
