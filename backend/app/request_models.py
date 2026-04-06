from __future__ import annotations

from typing import Any, Dict, List, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class LiveSearchRequest(BaseModel):
    query: str = Field(min_length=2)
    intent: Literal["case_law", "provision"] = "case_law"
    limit: int = Field(default=10, ge=1, le=20)


class DrilldownSelectedSource(BaseModel):
    id: str = ""
    title: str = ""
    url: str = ""
    snippet: str = ""


class LiveSearchDrilldownRequest(BaseModel):
    query: str = ""
    objective: str = "summarize"
    selected: List[DrilldownSelectedSource] = Field(default_factory=list)


class ProvisionLookupRequest(BaseModel):
    query: str = Field(min_length=2)
    facts: str = ""
    limit: int = Field(default=8, ge=1, le=12)
    startAnalysis: bool = False


class FeedbackSubmitRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    screen: str = Field(default="unknown", min_length=1, max_length=120)
    rating: int = Field(default=0, ge=0, le=5)
    comment: str = Field(default="", max_length=2000)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GenericAgentRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    @model_validator(mode="before")
    @classmethod
    def validate_payload(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            raise ValueError("Request payload must be a JSON object")
        if not value:
            raise ValueError("Request payload must include at least one field")
        _validate_nested_payload(value, depth=0)
        return value

    def as_payload(self) -> Dict[str, Any]:
        return self.model_dump(mode="python")


def _validate_nested_payload(value: Any, depth: int) -> None:
    if depth > 6:
        raise ValueError("Payload nesting is too deep")

    if isinstance(value, str):
        if len(value) > 20000:
            raise ValueError("String input exceeds max length of 20000 characters")
        return

    if isinstance(value, (int, float, bool)) or value is None:
        return

    if isinstance(value, list):
        if len(value) > 200:
            raise ValueError("Array input exceeds max length of 200 items")
        for item in value:
            _validate_nested_payload(item, depth + 1)
        return

    if isinstance(value, dict):
        if len(value) > 200:
            raise ValueError("Object input exceeds max size of 200 keys")
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("Object keys must be strings")
            _validate_nested_payload(item, depth + 1)
        return

    raise ValueError("Unsupported payload data type")
