from typing import TypedDict, List, Dict, Any


class GraphState(TypedDict):
    """
    Central state object passed across LangGraph nodes.
    Mirrors orchestrator + agent contracts.
    """

    # Input
    user_query: str

    # Core agent outputs
    issues: List[str]
    precedents: List[Dict[str, Any]]
    limitation_analysis: Dict[str, Any]
    arguments: Dict[str, Any]
    draft_document: str
    compliance_report: Dict[str, Any]
    legal_aid_info: Dict[str, Any]

    # Observability & evaluation
    traces: List[Dict[str, Any]]
    evaluation: Dict[str, Any]

    # Governance
    human_review_required: bool
