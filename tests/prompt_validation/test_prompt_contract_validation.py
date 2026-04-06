from __future__ import annotations

import copy

from tests.prompt_validation.contracts import PROMPT_CONTRACTS, validate_prompt_output
from tests.prompt_validation.fixtures import VALID_PROMPT_OUTPUTS


def test_all_prompt_contract_fixtures_validate() -> None:
    for task, contract in PROMPT_CONTRACTS.items():
        payload = VALID_PROMPT_OUTPUTS[task]
        errors = validate_prompt_output(contract, payload)
        assert errors == [], f"{task} failed contract validation: {errors}"


def test_contract_validation_catches_missing_required_field() -> None:
    payload = copy.deepcopy(VALID_PROMPT_OUTPUTS["limitation_checker"])
    payload["assessment"].pop("computedDeadline")

    errors = validate_prompt_output(PROMPT_CONTRACTS["limitation_checker"], payload)

    assert any("computedDeadline" in error for error in errors)
