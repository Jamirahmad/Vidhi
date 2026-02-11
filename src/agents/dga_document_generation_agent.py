"""
DGA – Document Generation Agent

Responsibilities:
- Generate draft legal documents using approved templates
- Populate drafts using verified inputs only
- NEVER invent facts, citations, or legal opinions
- ALWAYS require human (lawyer) review before use
"""

from __future__ import annotations

from typing import Any

from src.agents.base_agent import BaseAgent


class DGADocumentGenerationAgent(BaseAgent):
    """
    DGA - Document Generation Agent

    Responsibility:
    - Generate final legal draft based on structured pipeline outputs.
    - Must be deterministic and safe.
    - Must include disclaimer when required.

    Output contract:
    {
        "draft_text": str,
        "format": str,
        "metadata": {...}
    }
    """

    agent_name = "DGADocumentGenerationAgent"
    agent_version = "2.0"

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config=config)

    def _execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Expected payload:
        {
            "request_id": str,
            "jurisdiction": str,
            "document_type": str,
            "case_description": str,

            "issues": dict (optional),
            "research": dict (optional),
            "analysis": dict (optional),
            "arguments": dict (optional),

            "compliance": dict (optional),
            "disclaimer_text": str (optional),
            "disclaimer_required": bool (optional)
        }
        """
        request_id = str(payload.get("request_id", "")).strip()
        jurisdiction = str(payload.get("jurisdiction", "")).strip()
        document_type = str(payload.get("document_type", "Legal Draft")).strip()
        case_description = str(payload.get("case_description", "")).strip()

        issues = payload.get("issues") or {}
        research = payload.get("research") or {}
        analysis = payload.get("analysis") or {}
        arguments = payload.get("arguments") or {}

        compliance = payload.get("compliance") or {}
        disclaimer_required = bool(
            payload.get("disclaimer_required", compliance.get("disclaimer_required", False))
        )
        disclaimer_text = str(
            payload.get("disclaimer_text", compliance.get("disclaimer_text", ""))
        ).strip()

        if not disclaimer_text:
            disclaimer_text = (
                "Disclaimer: This document is generated for informational purposes only "
                "and does not constitute legal advice. Please consult a qualified lawyer."
            )

        # Extract key details safely
        primary_issues = issues.get("primary_issues", [])
        if not isinstance(primary_issues, list):
            primary_issues = []

        statutes = research.get("statutes", [])
        if not isinstance(statutes, list):
            statutes = []

        case_laws = research.get("case_laws", [])
        if not isinstance(case_laws, list):
            case_laws = []

        analysis_text = str(analysis.get("analysis_text", "")).strip()
        arguments_text = str(arguments.get("arguments_text", "")).strip()

        # Build draft
        draft_lines: list[str] = []

        draft_lines.append(f"DOCUMENT TYPE: {document_type}")
        if jurisdiction:
            draft_lines.append(f"JURISDICTION: {jurisdiction}")
        if request_id:
            draft_lines.append(f"REQUEST ID: {request_id}")

        draft_lines.append("\n---\n")

        if case_description:
            draft_lines.append("FACTS / CASE BACKGROUND")
            draft_lines.append(case_description)
            draft_lines.append("\n---\n")

        if primary_issues:
            draft_lines.append("LEGAL ISSUES IDENTIFIED")
            for idx, issue in enumerate(primary_issues, start=1):
                draft_lines.append(f"{idx}. {issue}")
            draft_lines.append("\n---\n")

        if statutes:
            draft_lines.append("RELEVANT STATUTES / PROVISIONS")
            for idx, statute in enumerate(statutes, start=1):
                draft_lines.append(f"{idx}. {statute}")
            draft_lines.append("\n---\n")

        if case_laws:
            draft_lines.append("RELEVANT CASE LAWS (UNVERIFIED)")
            for idx, cl in enumerate(case_laws, start=1):
                draft_lines.append(f"{idx}. {cl}")
            draft_lines.append("\n---\n")

        if analysis_text:
            draft_lines.append("LEGAL ANALYSIS")
            draft_lines.append(analysis_text)
            draft_lines.append("\n---\n")

        if arguments_text:
            draft_lines.append("ARGUMENTS")
            draft_lines.append(arguments_text)
            draft_lines.append("\n---\n")

        draft_lines.append("CONCLUSION / NEXT STEPS")
        draft_lines.append(
            "Based on the provided facts, the above issues and analysis may be relevant. "
            "Further review of official case law and statutory provisions is recommended."
        )

        if disclaimer_required:
            draft_lines.append("\n---\n")
            draft_lines.append(disclaimer_text)

        draft_text = "\n".join(draft_lines).strip()

        return {
            "draft_text": draft_text,
            "format": "text",
            "metadata": {
                "generated_by": self.agent_name,
                "version": self.agent_version,
                "document_type": document_type,
            },
        }
