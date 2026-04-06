from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List

from backend.app.error_handlers import HttpError


@dataclass(frozen=True)
class PromptOutputContract:
    root_key: str
    root_type: type
    required_keys: tuple[str, ...] = ()


PROMPT_OUTPUT_CONTRACTS: Dict[str, PromptOutputContract] = {
    "issue_spotter": PromptOutputContract("issues", list),
    "case_finder": PromptOutputContract("precedents", list),
    "limitation_checker": PromptOutputContract(
        "assessment",
        dict,
        required_keys=("inTime", "limitationWindowDays", "computedDeadline", "rationale"),
    ),
    "argument_builder": PromptOutputContract("argumentSet", dict),
    "doc_composer": PromptOutputContract("draft", dict, required_keys=("documentType", "content")),
    "compliance_guard": PromptOutputContract("findings", list),
    "aid_connector": PromptOutputContract("aid", dict, required_keys=("eligible", "providers")),
    "judgment_summarizer": PromptOutputContract(
        "summary",
        dict,
        required_keys=("caseTitle", "court", "decision", "plainLanguageSummary"),
    ),
    "knowledge_drilldown": PromptOutputContract("analysis", dict, required_keys=("summary", "citedSourceIds")),
    "provision_lookup": PromptOutputContract(
        "analysis",
        dict,
        required_keys=("applicableProvisionIds", "citedSourceIds"),
    ),
}

_FORBIDDEN_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"ignore\s+previous\s+instructions", re.IGNORECASE),
    re.compile(r"(reveal|print|show).*(system\s+prompt|developer\s+message)", re.IGNORECASE),
    re.compile(r"<script", re.IGNORECASE),
)



def _iter_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            if isinstance(key, str):
                yield key
            yield from _iter_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_strings(item)



def _validate_contract(task: str, payload: Dict[str, Any]) -> List[str]:
    contract = PROMPT_OUTPUT_CONTRACTS.get(task)
    if contract is None:
        return []

    errors: List[str] = []
    if contract.root_key not in payload:
        return [f"missing root key: {contract.root_key}"]

    root = payload[contract.root_key]
    if not isinstance(root, contract.root_type):
        return [f"{contract.root_key} must be {contract.root_type.__name__}"]

    if isinstance(root, dict):
        for key in contract.required_keys:
            if key not in root:
                errors.append(f"missing required field: {contract.root_key}.{key}")

    return errors



def apply_output_guardrails(task: str, payload: Any) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise HttpError(
            status=502,
            code="INVALID_LLM_SCHEMA",
            message="LLM output must be a JSON object",
            user_message="AI response format was invalid. Please retry.",
        )

    contract_errors = _validate_contract(task, payload)
    if contract_errors:
        raise HttpError(
            status=502,
            code="INVALID_LLM_SCHEMA",
            message=f"LLM output failed contract validation: {', '.join(contract_errors)}",
            user_message="AI response was incomplete for the requested task. Please retry.",
        )

    for text in _iter_strings(payload):
        if len(text) > 20000:
            raise HttpError(
                status=502,
                code="SAFETY_FILTER_BLOCKED",
                message="LLM output exceeded maximum allowed field length",
                user_message="AI response was blocked by safety filters. Please retry with shorter input.",
            )
        for pattern in _FORBIDDEN_PATTERNS:
            if pattern.search(text):
                raise HttpError(
                    status=502,
                    code="SAFETY_FILTER_BLOCKED",
                    message="LLM output matched forbidden safety pattern",
                    user_message="AI response was blocked by safety filters. Please retry.",
                )

    return payload
