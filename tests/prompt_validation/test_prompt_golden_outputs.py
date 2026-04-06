from __future__ import annotations

from typing import Any, Dict, Iterable, List

from tests.prompt_validation.contracts import PROMPT_CONTRACTS, validate_prompt_output
from tests.prompt_validation.golden_cases import GOLDEN_INVALID_CASES, GOLDEN_VALID_CASES


def _validate_list_of_dicts(value: Any, required_keys: Iterable[str], path: str) -> List[str]:
    errors: List[str] = []
    if not isinstance(value, list):
        return [f"{path} must be list"]
    for idx, item in enumerate(value):
        if not isinstance(item, dict):
            errors.append(f"{path}[{idx}] must be object")
            continue
        for key in required_keys:
            if key not in item:
                errors.append(f"missing {path}[{idx}].{key}")
    return errors


def _strict_field_validation(task: str, payload: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    if task == "issue_spotter":
        errors.extend(_validate_list_of_dicts(payload.get("issues"), ("id", "title", "statute", "rationale"), "issues"))
    elif task == "case_finder":
        errors.extend(
            _validate_list_of_dicts(
                payload.get("precedents"),
                ("citation", "title", "court", "year", "relevanceScore", "supports", "summary", "sourceUrl", "sourceName"),
                "precedents",
            )
        )
    elif task == "limitation_checker":
        assessment = payload.get("assessment")
        if not isinstance(assessment, dict):
            errors.append("assessment must be object")
        else:
            expected = {
                "inTime": bool,
                "limitationWindowDays": int,
                "elapsedDays": int,
                "excludedDays": int,
                "effectiveElapsedDays": int,
                "computedDeadline": str,
                "daysRemaining": int,
                "rationale": str,
                "assumptions": list,
                "checkpoints": list,
            }
            for key, expected_type in expected.items():
                if key not in assessment:
                    errors.append(f"missing assessment.{key}")
                elif not isinstance(assessment[key], expected_type):
                    errors.append(f"assessment.{key} must be {expected_type.__name__}")
    elif task == "argument_builder":
        argument_set = payload.get("argumentSet")
        if not isinstance(argument_set, dict):
            errors.append("argumentSet must be object")
        else:
            for key in ("supporting", "opposing", "riskNotes"):
                if not isinstance(argument_set.get(key), list):
                    errors.append(f"argumentSet.{key} must be list")
    elif task == "doc_composer":
        draft = payload.get("draft")
        if not isinstance(draft, dict):
            errors.append("draft must be object")
        else:
            for key in ("documentType", "language", "content", "citations"):
                if key not in draft:
                    errors.append(f"missing draft.{key}")
    elif task == "compliance_guard":
        errors.extend(_validate_list_of_dicts(payload.get("findings"), ("ruleId", "status", "message"), "findings"))
    elif task == "aid_connector":
        aid = payload.get("aid")
        if not isinstance(aid, dict):
            errors.append("aid must be object")
        else:
            if not isinstance(aid.get("eligible"), bool):
                errors.append("aid.eligible must be bool")
            errors.extend(_validate_list_of_dicts(aid.get("providers"), ("name", "location", "contact"), "aid.providers"))
    elif task == "judgment_summarizer":
        summary = payload.get("summary")
        if not isinstance(summary, dict):
            errors.append("summary must be object")
        else:
            for key in (
                "caseTitle",
                "court",
                "judgmentDate",
                "issues",
                "decision",
                "reasoning",
                "keyPoints",
                "plainLanguageSummary",
                "citations",
            ):
                if key not in summary:
                    errors.append(f"missing summary.{key}")
    elif task == "knowledge_drilldown":
        analysis = payload.get("analysis")
        if not isinstance(analysis, dict):
            errors.append("analysis must be object")
        else:
            for key in ("summary", "keyPoints", "nextSteps", "citedSourceIds", "citationNotes"):
                if key not in analysis:
                    errors.append(f"missing analysis.{key}")
    elif task == "provision_lookup":
        analysis = payload.get("analysis")
        if not isinstance(analysis, dict):
            errors.append("analysis must be object")
        else:
            for key in (
                "applicableProvisionIds",
                "plainLanguageSummary",
                "howToApply",
                "riskNotes",
                "citedSourceIds",
                "citationNotes",
            ):
                if key not in analysis:
                    errors.append(f"missing analysis.{key}")

    return errors


def test_golden_valid_outputs_match_contract_and_strict_shape() -> None:
    for task, payload in GOLDEN_VALID_CASES.items():
        contract_errors = validate_prompt_output(PROMPT_CONTRACTS[task], payload)
        strict_errors = _strict_field_validation(task, payload)
        assert contract_errors == [], f"{task} contract errors: {contract_errors}"
        assert strict_errors == [], f"{task} strict errors: {strict_errors}"


def test_golden_invalid_outputs_fail_contract_or_strict_checks() -> None:
    for task, payload in GOLDEN_INVALID_CASES.items():
        contract_errors = validate_prompt_output(PROMPT_CONTRACTS[task], payload)
        strict_errors = _strict_field_validation(task, payload)
        assert contract_errors or strict_errors, f"{task} invalid case unexpectedly passed"
