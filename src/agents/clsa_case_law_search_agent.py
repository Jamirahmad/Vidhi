"""
CLSA – Case Law Search Agent

Responsibilities:
- Retrieve relevant case laws and judicial precedents
- Use vector + keyword hybrid retrieval
- NEVER fabricate citations
- Return traceable sources only
- Escalate to human review on low confidence or empty results
"""

from typing import Dict, Any, List

from src.agents.base_agent import BaseAgent, AgentResultStatus
from src.retrieval.retriever import HybridRetriever


class CaseLawSearchAgent(BaseAgent):
    """
    CLSA – Case Law Search Agent
    """

    def __init__(self, retriever: HybridRetriever | None = None):
        super().__init__(
            name="CLSA_CaseLawSearchAgent",
            requires_human_review=False
        )
        self.retriever = retriever or HybridRetriever()

    # ------------------------------------------------------------------
    # Input Validation
    # ------------------------------------------------------------------

    def validate_input(self, input_data: Dict[str, Any]) -> None:
        required_fields = [
            "query",
            "jurisdiction",
            "court",
            "case_type"
        ]

        missing = [f for f in required_fields if f not in input_data]
        if missing:
            raise ValueError(f"Missing required input fields: {missing}")

        if not isinstance(input_data["query"], str):
            raise TypeError("query must be a string")

    # ------------------------------------------------------------------
    # Core Logic
    # ------------------------------------------------------------------

    def run(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        query = input_data["query"]
        jurisdiction = input_data["jurisdiction"]
        court = input_data["court"]
        case_type = input_data["case_type"]

        results = self.retriever.search(
            query=query,
            filters={
                "jurisdiction": jurisdiction,
                "court": court,
                "case_type": case_type
            },
            top_k=10
        )

        if not results:
            return {
                "status": AgentResultStatus.UNCERTAIN,
                "cases": [],
                "confidence": 0.0,
                "reason": "No relevant case laws found",
            }

        structured_cases: List[Dict[str, Any]] = []
        scores: List[float] = []

        for item in results:
            structured_cases.append({
                "case_title": item.get("case_title"),
                "court": item.get("court"),
                "year": item.get("year"),
                "citation": item.get("citation"),
                "summary": item.get("summary"),
                "source_url": item.get("source_url")
            })
            scores.append(item.get("score", 0.0))

        avg_confidence = sum(scores) / max(len(scores), 1)

        status = (
            AgentResultStatus.SUCCESS
            if avg_confidence >= 0.65
            else AgentResultStatus.UNCERTAIN
        )

        return {
            "status": status,
            "cases": structured_cases,
            "confidence": round(avg_confidence, 3),
            "total_cases": len(structured_cases),
            "jurisdiction": jurisdiction,
            "court": court,
            "case_type": case_type
        }

    # ------------------------------------------------------------------
    # Output Validation
    # ------------------------------------------------------------------

    def validate_output(self, output_data: Dict[str, Any]) -> None:
        required_fields = [
            "status",
            "cases",
            "confidence"
        ]

        missing = [f for f in required_fields if f not in output_data]
        if missing:
            raise ValueError(f"Missing required output fields: {missing}")

        if not isinstance(output_data["cases"], list):
            raise TypeError("cases must be a list")
