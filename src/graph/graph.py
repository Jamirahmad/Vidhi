from langgraph.graph import StateGraph, END
from .state import VidhiState
from .nodes import *


def build_vidhi_graph():
    graph = StateGraph(VidhiState)

    graph.add_node("case_finder", case_finder_node)
    graph.add_node("issue_spotter", issue_spotter_node)
    graph.add_node("limitation_checker", limitation_checker_node)
    graph.add_node("argument_builder", argument_builder_node)
    graph.add_node("doc_composer", doc_composer_node)
    graph.add_node("compliance_guard", compliance_guard_node)
    graph.add_node("aid_connector", aid_connector_node)

    graph.set_entry_point("case_finder")

    graph.add_edge("case_finder", "issue_spotter")
    graph.add_edge("issue_spotter", "limitation_checker")
    graph.add_edge("limitation_checker", "argument_builder")
    graph.add_edge("argument_builder", "doc_composer")
    graph.add_edge("doc_composer", "compliance_guard")
    graph.add_edge("compliance_guard", "aid_connector")
    graph.add_edge("aid_connector", END)

    return graph.compile()
