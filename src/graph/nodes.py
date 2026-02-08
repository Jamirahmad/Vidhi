from logs.tracer import trace_agent
from src.agents import (
    CaseFinder,
    IssueSpotter,
    LimitationChecker,
    ArgumentBuilder,
    DocComposer,
    ComplianceGuard,
    AidConnector,
)
from .state import VidhiState


@trace_agent("CaseFinder")
def case_finder_node(state: VidhiState) -> VidhiState:
    state["precedents"] = CaseFinder.run(state)
    return state


@trace_agent("IssueSpotter")
def issue_spotter_node(state: VidhiState) -> VidhiState:
    state["issues"] = IssueSpotter.run(state)
    return state


@trace_agent("LimitationChecker")
def limitation_checker_node(state: VidhiState) -> VidhiState:
    state["limitation_analysis"] = LimitationChecker.run(state)
    return state


@trace_agent("ArgumentBuilder")
def argument_builder_node(state: VidhiState) -> VidhiState:
    state["arguments"] = ArgumentBuilder.run(state)
    return state


@trace_agent("DocComposer")
def doc_composer_node(state: VidhiState) -> VidhiState:
    state["draft_document"] = DocComposer.run(state)
    return state


@trace_agent("ComplianceGuard")
def compliance_guard_node(state: VidhiState) -> VidhiState:
    flags = ComplianceGuard.run(state)
    state["compliance_flags"] = flags
    state["human_review_required"] = len(flags) > 0
    return state


@trace_agent("AidConnector")
def aid_connector_node(state: VidhiState) -> VidhiState:
    state["legal_aid_options"] = AidConnector.run(state)
    return state
