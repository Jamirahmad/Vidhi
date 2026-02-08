from datetime import datetime
from .state import GraphState


def _trace(state: GraphState, agent: str, summary: str) -> None:
    state["traces"].append(
        {
            "agent": agent,
            "summary": summary,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


def issue_identifier(state: GraphState) -> GraphState:
    state["issues"] = ["Identified legal issue from user query"]
    _trace(state, "LII", "Legal issues identified")
    return state


def case_law_search(state: GraphState) -> GraphState:
    state["precedents"] = [
        {
            "case_name": "Sample vs State",
            "citation": "AIR 2020 SC 123",
            "court": "Supreme Court of India",
        }
    ]
    _trace(state, "CLSA", "Relevant precedents retrieved")
    return state


def limitation_analysis(state: GraphState) -> GraphState:
    state["limitation_analysis"] = {
        "within_limitation": True,
        "reasoning": "Filed within statutory period",
    }
    _trace(state, "LAA", "Limitation period evaluated")
    return state


def argument_builder(state: GraphState) -> GraphState:
    state["arguments"] = {
        "primary_arguments": ["Argument A", "Argument B"],
        "counter_arguments": ["Possible counter X"],
    }
    _trace(state, "LAB", "Arguments and counter-arguments generated")
    return state


def document_generator(state: GraphState) -> GraphState:
    state["draft_document"] = "Draft legal document (non-final, for review)"
    _trace(state, "DGA", "Draft document generated")
    return state


def compliance_check(state: GraphState) -> GraphState:
    state["compliance_report"] = {
        "status": "PASS",
        "checks": ["Jurisdiction", "Formatting", "Mandatory annexures"],
    }
    state["human_review_required"] = True
    _trace(state, "CCA", "Compliance checks completed")
    return state


def legal_aid_finder(state: GraphState) -> GraphState:
    state["legal_aid_info"] = {
        "eligible": False,
        "notes": "User appears not eligible based on inputs",
    }
    _trace(state, "LAF", "Legal aid assessment completed")
    return state
