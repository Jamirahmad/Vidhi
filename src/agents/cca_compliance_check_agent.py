"""
CCA – Compliance Check Agent

Responsibilities:
- Validate court-specific filing requirements
- Check document structure & mandatory sections
- Flag missing annexures, affidavits, signatures
- Enforce human review on any uncertainty

This agent NEVER auto-fixes content.
It only validates and flags issues.
"""

from __future__ import annotations

from typing import Any

from src.agents.base_agent import BaseAgent
from src.core.safety_guardrails import SafetyGuardrails


class CCAComplianceCheckAgent(BaseAgent):
    """
    CCA - Compliance Check Agent

    Responsibility:
    - Validate whether the system can proceed with legal draft generation.
    - Enforce safety guardrails for restricted content.
    - Provide structured compliance decision.

    Output contract:
    {
        "can_generate_draft": bool,
        "notes": str,
        "disclaimer_required": bool,
        "disclaimer_text": str,
        "flagged_risks": list[str]
    }
    """

    agent_name = "CCAComplianceCheckAgent"
    agent_version = "2.0"

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config=config)
        self.guardrails = SafetyGuardrails()

    def _execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Expected payload:
        {
            "request_id": str,
            "case_description": str,
            "jurisdiction": str,
            "document_type": str,
            "analysis_text": str (optional),
            "arguments_text": str (optional)
        }
        """
        case_description = str(payload.get("case_description", "")).strip()
        jurisdiction = str(payload.get("jurisdiction", "")).strip()
        document_type = str(payload.get("document_type", "")).strip()

        analysis_text = str(payload.get("analysis_text", "")).strip()
        arguments_text = str(payload.get("arguments_text", "")).strip()

        combined_text = "\n\n".join(
            [t for t in [case_description, analysis_text, arguments_text] if t]
        ).strip()

        if not combined_text:
            return {
                "can_generate_draft": False,
                "notes": "No content provided for compliance evaluation.",
                "disclaimer_required": True,
                "disclaimer_text": "No sufficient details were provided. This output is informational only.",
                "flagged_risks": ["EMPTY_INPUT"],
            }

        safety_result = self.guardrails.evaluate(
            user_input=combined_text,
            jurisdiction=jurisdiction,
            document_type=document_type,
        )

        # safety_result expected structure (based on review guardrails design):
        # {
        #   "allowed": bool,
        #   "flagged_categories": [...],
        #   "message": "...",
        #   "disclaimer_required": bool,
        #   "disclaimer_text": "..."
        # }

        allowed = bool(safety_result.get("allowed", True))
        flagged_categories = safety_result.get("flagged_categories", []) or []
        message = str(safety_result.get("message", "")).strip()

        disclaimer_required = bool(safety_result.get("disclaimer_required", False))
        disclaimer_text = str(safety_result.get("disclaimer_text", "")).strip()

        if not disclaimer_text:
            disclaimer_text = (
                "This response is generated for informational purposes only "
                "and does not constitute legal advice."
            )

        return {
            "can_generate_draft": allowed,
            "notes": message if message else "Compliance evaluation completed.",
            "disclaimer_required": disclaimer_required,
            "disclaimer_text": disclaimer_text,
            "flagged_risks": flagged_categories,
        }
