from langgraph.graph import StateGraph


def build_edges(builder: StateGraph) -> None:
    """
    Defines deterministic, linear agent execution flow.
    Branching can be introduced later without changing node logic.
    """

    builder.add_edge("issue_identifier", "case_law_search")
    builder.add_edge("case_law_search", "limitation_analysis")
    builder.add_edge("limitation_analysis", "argument_builder")
    builder.add_edge("argument_builder", "document_generator")
    builder.add_edge("document_generator", "compliance_check")
    builder.add_edge("compliance_check", "legal_aid_finder")
