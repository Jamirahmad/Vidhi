import pytest
from pydantic import ValidationError

from backend.app.request_models import FeedbackSubmitRequest, GenericAgentRequest


def test_feedback_submit_request_validates_ranges() -> None:
    payload = FeedbackSubmitRequest(screen="issue-spotter", rating=5, comment="good", metadata={"source": "ui"})

    assert payload.rating == 5


def test_feedback_submit_request_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        FeedbackSubmitRequest(screen="issue", rating=2, comment="ok", unknown="x")


def test_generic_agent_request_requires_non_empty_object() -> None:
    with pytest.raises(ValidationError):
        GenericAgentRequest.model_validate({})


def test_generic_agent_request_rejects_overly_long_strings() -> None:
    with pytest.raises(ValidationError):
        GenericAgentRequest.model_validate({"facts": "a" * 20001})


def test_generic_agent_request_accepts_nested_safe_payload() -> None:
    payload = GenericAgentRequest.model_validate(
        {
            "facts": "sample facts",
            "context": {
                "issues": ["issue1", "issue2"],
                "meta": {"priority": "high"},
            },
        }
    )

    assert "facts" in payload.as_payload()
