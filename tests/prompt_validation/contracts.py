from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class PromptContract:
    task: str
    root_key: str
    root_type: type
    required_keys: tuple[str, ...] = ()


def _is_instance(value: Any, expected: type) -> bool:
    if expected is bool:
        return isinstance(value, bool)
    if expected is int:
        return isinstance(value, int) and not isinstance(value, bool)
    return isinstance(value, expected)


def validate_prompt_output(contract: PromptContract, payload: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    if contract.root_key not in payload:
        return [f"missing root key: {contract.root_key}"]

    root = payload[contract.root_key]
    if not _is_instance(root, contract.root_type):
        return [f"{contract.root_key} must be {contract.root_type.__name__}"]

    if isinstance(root, dict):
        for key in contract.required_keys:
            if key not in root:
                errors.append(f"missing required field: {contract.root_key}.{key}")

    return errors


PROMPT_CONTRACTS: Dict[str, PromptContract] = {
    "issue_spotter": PromptContract("issue_spotter", "issues", list),
    "case_finder": PromptContract("case_finder", "precedents", list),
    "limitation_checker": PromptContract(
        "limitation_checker",
        "assessment",
        dict,
        required_keys=("inTime", "limitationWindowDays", "computedDeadline", "rationale"),
    ),
    "argument_builder": PromptContract("argument_builder", "argumentSet", dict),
    "doc_composer": PromptContract("doc_composer", "draft", dict, required_keys=("documentType", "content")),
    "compliance_guard": PromptContract("compliance_guard", "findings", list),
    "aid_connector": PromptContract("aid_connector", "aid", dict, required_keys=("eligible", "providers")),
    "judgment_summarizer": PromptContract(
        "judgment_summarizer",
        "summary",
        dict,
        required_keys=("caseTitle", "court", "decision", "plainLanguageSummary"),
    ),
    "knowledge_drilldown": PromptContract(
        "knowledge_drilldown",
        "analysis",
        dict,
        required_keys=("summary", "citedSourceIds"),
    ),
    "provision_lookup": PromptContract(
        "provision_lookup",
        "analysis",
        dict,
        required_keys=("applicableProvisionIds", "citedSourceIds"),
    ),
}
