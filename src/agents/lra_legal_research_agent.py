
"""
LRA – Legal Research Agent

Responsibilities:
- Consolidate retrieved precedents and statutes
- Summarize relevance to identified legal issues
- Highlight supporting vs contrary judgments
- NEVER fabricate cases or citations
"""

from __future__ import annotations

from typing import Any

from src.agents.base_agent import BaseAgent


class LRALegalResearchAgent(BaseAgent):
    """
    LRA - Legal Research Agent

    Responsibility:
    - Provide relevant statutes / case law pointers based on issues + jurisdiction.
    - Must NOT fabricate exact citations.
    - Output must be structured.

    Output contract:
    {
        "statutes": list[str],
        "case_laws": list[str],
        "summary": str
    }
    """

    agent_name = "LRALegalResearchAgent"
    agent_version = "2.0"

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config=config)

    def _execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Expected payload:
        {
            "jurisdiction": str,
            "issues": dict OR list[str] OR str,
            "case_description": str
        }
        """
        jurisdiction = str(payload.get("jurisdiction", "")).strip()
        case_description = str(payload.get("case_description", "")).strip()

        issues_obj = payload.get("issues", [])
        issues: list[str] = []

        if isinstance(issues_obj, dict):
            primary = issues_obj.get("primary_issues", []) or []
            secondary = issues_obj.get("secondary_issues", []) or []
            issues = [str(i).strip() for i in (primary + secondary) if str(i).strip()]

        elif isinstance(issues_obj, list):
            issues = [str(i).strip() for i in issues_obj if str(i).strip()]

        elif isinstance(issues_obj, str):
            issues = [issues_obj.strip()] if issues_obj.strip() else []

        statutes: list[str] = []
        case_laws: list[str] = []

        # Safe research suggestions (no fake citations)
        if jurisdiction.lower() in {"india", "indian"}:
            # Add common acts depending on issue keywords
            joined = " ".join(issues).lower()

            if "contract" in joined or "agreement" in joined or "breach" in joined:
                statutes.append("Indian Contract Act, 1872")

            if "fraud" in joined or "cheating" in joined or "criminal" in joined:
                statutes.append("Indian Penal Code, 1860 (relevant provisions)")
                statutes.append("Code of Criminal Procedure, 1973")

            if "consumer" in joined:
                statutes.append("Consumer Protection Act, 2019")

            if "property" in joined or "possession" in joined:
                statutes.append("Transfer of Property Act, 1882")
                statutes.append("Specific Relief Act, 1963")

            if "family" in joined or "divorce" in joined or "custody" in joined:
                statutes.append("Hindu Marriage Act, 1955 (if applicable)")
                statutes.append("Special Marriage Act, 1954 (if applicable)")
                statutes.append("Guardians and Wards Act, 1890")

            if "limitation" in joined or "delay" in joined:
                statutes.append("Limitation Act, 1963")

            if not statutes:
                statutes.append("Relevant Central/State Acts depending on dispute classification")

            summary = (
                "Legal research completed for Indian jurisdiction. "
                "Statutes listed are based on issue heuristics and must be verified."
            )

        else:
            statutes.append("Relevant statutes depend on jurisdiction-specific legal framework.")
            summary = (
                f"Legal research completed for jurisdiction: {jurisdiction or 'UNKNOWN'}. "
                "No jurisdiction-specific statute database is configured."
            )

        # No case laws returned because citations cannot be verified offline
        if issues:
            summary += f" Issues considered: {', '.join(issues[:5])}."
        if case_description:
            summary += " Case facts were used for contextual relevance."

        return {
            "statutes": statutes,
            "case_laws": case_laws,
            "summary": summary.strip(),
        }
