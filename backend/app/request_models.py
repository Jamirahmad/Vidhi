from __future__ import annotations

from typing import Any, Dict, List, Literal

from pydantic import BaseModel, ConfigDict, Field


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
    model_config = ConfigDict(extra="allow")


class GenericAgentRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    def as_payload(self) -> Dict[str, Any]:
        return self.model_dump(mode="python")
