from langgraph.graph import StateGraph, END
from .state import GraphState
from .nodes import (
    issue_identifier,
    case_law_search,
    limitation_analysis,
    argument_builder,
    document_generator,
    compliance_check,
    legal_aid_finder,
)
from .edges import build_edges


def build_graph():
    """
    Compiles the LangGraph multi-agent workflow.

    This graph:
    - Preserves existing agent logic
    - Adds observability via shared state
    - Enforces human-in-the-loop governance
    """

    builder = StateGraph(GraphState)

    # Register nodes
    builder.add_node("issue_identifier", issue_identifier)
    builder.add_node("case_law_search", case_law_search)
    builder.add_node("limitation_analysis", limitation_analysis)
    builder.add_node("argument_builder", argument_builder)
    builder.add_node("document_generator", document_generator)
    builder.add_node("compliance_check", compliance_check)
    builder.add_node("legal_aid_finder", legal_aid_finder)

    # Entry point
    builder.set_entry_point("issue_identifier")

    # Edges
    build_edges(builder)

    # Exit
    builder.add_edge("legal_aid_finder", END)

    return builder.compile()
