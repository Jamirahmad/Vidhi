"""
LII – Legal Issue Identifier Agent

Responsibilities:
- Extract key legal issues from case facts
- Identify potentially applicable statutes and sections
- Clearly separate facts vs legal questions
- NEVER classify guilt, liability, or outcome
"""
# src/agents/lii_issue_identifier_agent.py

from __future__ import annotations

from typing import Any

from src.agents.base_agent import BaseAgent


class LIIIssueIdentifierAgent(BaseAgent):
    """
    LII - Legal Issue Identifier Agent

    Responsibility:
    - Extract primary and secondary legal issues from the case description.
    - Provide structured and deterministic output.
    - Avoid hallucinating facts not present in input.

    Output contract:
    {
        "primary_issues": list[str],
        "secondary_issues": list[str],
        "summary": str
    }
    """

    agent_name = "LIIIssueIdentifierAgent"
    agent_version = "2.0"

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config=config)

    def _execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Expected payload:
        {
            "case_description": str,
            "jurisdiction": str (optional),
            "document_type": str (optional)
        }
        """
        case_description = str(payload.get("case_description", "")).strip()
        jurisdiction = str(payload.get("jurisdiction", "")).strip()
        document_type = str(payload.get("document_type", "")).strip()

        if not case_description:
            return {
                "primary_issues": [],
                "secondary_issues": [],
                "summary": "No case description provided. Unable to identify legal issues.",
            }

        text = case_description.lower()

        primary_issues: list[str] = []
        secondary_issues: list[str] = []

        # Heuristic issue extraction (rule-based)
        if "fraud" in text or "cheating" in text or "misrepresentation" in text:
            primary_issues.append("Fraud / Misrepresentation")

        if "breach" in text or "contract" in text or "agreement" in text:
            primary_issues.append("Breach of Contract / Contractual Dispute")

        if "property" in text or "land" in text or "possession" in text or "ownership" in text:
            primary_issues.append("Property Ownership / Possession Dispute")

        if "tenant" in text or "rent" in text or "eviction" in text:
            primary_issues.append("Tenancy / Eviction Dispute")

        if "injury" in text or "accident" in text or "damage" in text:
            primary_issues.append("Tort / Negligence / Compensation Claim")

        if "divorce" in text or "marriage" in text or "maintenance" in text or "custody" in text:
            primary_issues.append("Family Law Dispute")

        if "consumer" in text or "deficiency" in text or "service" in text:
            primary_issues.append("Consumer Protection / Deficiency in Service")

        if "criminal" in text or "police" in text or "fir" in text or "arrest" in text:
            primary_issues.append("Criminal Law Procedure / FIR / Investigation")

        if "termination" in text or "salary" in text or "employment" in text:
            primary_issues.append("Employment / Labor Dispute")

        # Secondary issues (common legal angles)
        if "notice" in text:
            secondary_issues.append("Notice / Legal Notice Requirements")

        if "limitation" in text or "delay" in text or "time-bar" in text:
            secondary_issues.append("Limitation Period / Delay Considerations")

        if "jurisdiction" in text or "court" in text:
            secondary_issues.append("Jurisdiction / Maintainability")

        if "evidence" in text or "document" in text or "proof" in text:
            secondary_issues.append("Evidence and Documentation Requirements")

        # Fallback if nothing detected
        if not primary_issues:
            primary_issues.append("General Civil/Legal Dispute (requires detailed classification)")

        summary = (
            f"Identified {len(primary_issues)} primary issue(s)"
            + (f" and {len(secondary_issues)} secondary issue(s)." if secondary_issues else ".")
        )

        if jurisdiction:
            summary += f" Jurisdiction considered: {jurisdiction}."
        if document_type:
            summary += f" Document type: {document_type}."

        return {
            "primary_issues": primary_issues,
            "secondary_issues": secondary_issues,
            "summary": summary.strip(),
        }
