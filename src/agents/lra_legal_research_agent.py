
"""
LRA – Legal Research Agent

Responsibilities:
- Consolidate retrieved precedents and statutes
- Summarize relevance to identified legal issues
- Highlight supporting vs contrary judgments
- NEVER fabricate cases or citations
"""

from typing import Dict, Any, List

from src.agents.base_agent import BaseAgent, AgentResultStatus


class LegalResearchAgent(BaseAgent):
    """
    LRA – Legal Research Agent
    """

    def __init__(self):
        super().__init__(
            name="LRA_LegalResearchAgent",
            requires_human_review=True  # Research conclusions must be verified
        )

    # ------------------------------------------------------------------
    # Input Validation
    # ------------------------------------------------------------------

    def validate_input(self, input_data: Dict[str, Any]) -> None:
        required_fields = [
            "legal_issues",
            "retrieved_documents"
        ]

        missing = [f for f in required_fields if f not in input_data]
        if missing:
            raise ValueError(f"Missing required input fields: {missing}")

        if not isinstance(input_data["legal_issues"], list):
            raise TypeError("legal_issues must be a list")

        if not isinstance(input_data["retrieved_documents"], list):
            raise TypeError("retrieved_documents must be a list")

    # ------------------------------------------------------------------
    # Core Logic
    # ------------------------------------------------------------------

    def run(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        legal_issues: List[str] = input_data["legal_issues"]
        retrieved_docs: List[Dict[str, Any]] = input_data["retrieved_documents"]

        supporting_cases = []
        contrary_cases = []
        neutral_cases = []
        gaps = []

        if not retrieved_docs:
            return {
                "status": AgentResultStatus.FAIL,
                "message": "No relevant precedents retrieved",
                "research_summary": None,
                "gaps": ["No case law available for provided issues"]
            }

        for doc in retrieved_docs:
            citation = doc.get("citation")
            relevance = doc.get("relevance", "neutral")

            if not citation:
                continue  # Skip uncitable material

            case_entry = {
                "case_name": doc.get("case_name"),
                "citation": citation,
                "court": doc.get("court"),
                "summary": doc.get("summary"),
                "year": doc.get("year")
            }

            if relevance == "supporting":
                supporting_cases.append(case_entry)
            elif relevance == "contrary":
                contrary_cases.append(case_entry)
            else:
                neutral_cases.append(case_entry)

        if not supporting_cases and not contrary_cases:
            gaps.append(
                "No clear supporting or contrary precedents found for the identified issues"
            )

        status = (
            AgentResultStatus.SUCCESS
            if supporting_cases or contrary_cases
            else AgentResultStatus.UNCERTAIN
        )

        return {
            "status": status,
            "legal_issues": legal_issues,
            "supporting_precedents": supporting_cases,
            "contrary_precedents": contrary_cases,
            "neutral_references": neutral_cases,
            "research_notes": (
                "Precedents are grouped based on relevance inferred from retrieval metadata. "
                "Final applicability must be assessed by a legal professional."
            ),
            "gaps": gaps
        }

    # ------------------------------------------------------------------
    # Output Validation
    # ------------------------------------------------------------------

    def validate_output(self, output_data: Dict[str, Any]) -> None:
        required_fields = [
            "status",
            "supporting_precedents",
            "contrary_precedents"
        ]

        missing = [f for f in required_fields if f not in output_data]
        if missing:
            raise ValueError(f"Missing required output fields: {missing}")

        if not isinstance(output_data["supporting_precedents"], list):
            raise TypeError("supporting_precedents must be a list")

        if not isinstance(output_data["contrary_precedents"], list):
            raise TypeError("contrary_precedents must be a list")
