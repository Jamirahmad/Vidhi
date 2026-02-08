from typing import TypedDict, List, Dict, Any


class VidhiState(TypedDict):
    session_id: str

    # Inputs
    case_facts: Dict[str, Any]
    jurisdiction: str
    case_type: str

    # Agent outputs
    precedents: List[Dict[str, Any]]
    issues: List[str]
    limitation_analysis: Dict[str, Any]
    arguments: Dict[str, Any]
    draft_document: str
    compliance_flags: List[str]
    legal_aid_options: List[str]

    # Observability
    evaluation: Dict[str, Any]
    human_review_required: bool
