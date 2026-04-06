from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class HealthKnowledgeResponse(BaseModel):
    provider: str
    seedPath: str
    publicSource: str
    available: bool
    error: Optional[str] = None


class HealthMiddlewareRateLimitResponse(BaseModel):
    enabled: bool
    windowSeconds: int
    maxRequests: int
    bypassPaths: List[str] = Field(default_factory=list)


class HealthMiddlewareResponse(BaseModel):
    exceptionHandler: bool
    requestLogger: bool
    securityHeaders: bool
    rateLimiter: HealthMiddlewareRateLimitResponse


class HealthResponse(BaseModel):
    status: str
    appVersion: str
    provider: str
    model: str
    apiKeyConfigured: bool
    knowledge: HealthKnowledgeResponse
    middleware: HealthMiddlewareResponse


class MetricsStatusBucketsResponse(BaseModel):
    model_config = ConfigDict(extra="allow")


class MetricsRouteStatResponse(BaseModel):
    requests: int
    avgDurationMs: float


class MetricsResponse(BaseModel):
    status: str
    appVersion: str
    processStartTime: str
    uptimeSeconds: int
    totalRequests: int
    totalErrors: int
    statusBuckets: MetricsStatusBucketsResponse
    routes: Dict[str, MetricsRouteStatResponse] = Field(default_factory=dict)

class PromptVersionResponse(BaseModel):
    manifestVersion: str
    systemPromptStackVersion: str
    taskPromptVersions: Dict[str, str] = Field(default_factory=dict)


class KnowledgeSearchItemResponse(BaseModel):
    model_config = ConfigDict(extra="allow")


class RefreshResponse(BaseModel):
    model_config = ConfigDict(extra="allow")


class LiveSearchResultItemResponse(BaseModel):
    id: str
    intent: str
    title: str
    snippet: str
    url: str
    domain: str
    publishedAt: str = ""
    source: str = ""


class LiveSearchDiagnosticsResponse(BaseModel):
    webConfigured: bool
    webProvider: str
    webFetchedCount: Optional[int] = None
    webError: str = ""


class LiveSearchResponse(BaseModel):
    query: str
    intent: str
    results: List[LiveSearchResultItemResponse] = Field(default_factory=list)
    count: int
    source: str
    sourceBreakdown: Dict[str, int] = Field(default_factory=dict)
    diagnostics: LiveSearchDiagnosticsResponse


class DrilldownSourceResponse(BaseModel):
    id: str
    title: str
    url: str
    snippet: str
    extractedText: str


class DrilldownAnalysisResponse(BaseModel):
    model_config = ConfigDict(extra="allow")


class DrilldownGroundingResponse(BaseModel):
    strictSourceValidation: bool
    allowedSourceIds: List[str] = Field(default_factory=list)


class LiveSearchDrilldownResponse(BaseModel):
    query: str
    objective: str
    sources: List[DrilldownSourceResponse] = Field(default_factory=list)
    analysis: Optional[DrilldownAnalysisResponse] = None
    analysisError: Optional[str] = None
    grounding: DrilldownGroundingResponse


class ProvisionItemResponse(BaseModel):
    sourceId: str
    title: str
    category: str
    summary: str
    textExcerpt: str
    sourceName: str
    sourceUrl: str



class ProvisionRetrievalDiagnosticsResponse(BaseModel):
    ragCount: int = 0
    webCount: int = 0
    hybridCount: int = 0
    seedCount: int = 0
    llmScoutCount: int = 0
    webError: str = ""
    pipeline: List[str] = Field(default_factory=list)


class ProvisionLookupResponse(BaseModel):
    query: str
    facts: str
    provisions: List[ProvisionItemResponse] = Field(default_factory=list)
    analysis: Optional[Dict[str, Any]] = None
    analysisError: Optional[str] = None
    analysisStatus: Optional[str] = None
    analysisJobId: Optional[str] = None
    grounding: Optional[Dict[str, Any]] = None
    retrievalDiagnostics: Optional[ProvisionRetrievalDiagnosticsResponse] = None

class FeedbackItemResponse(BaseModel):
    id: str
    createdAt: str
    payload: Dict[str, Any]

class FeedbackSubmitResponse(BaseModel):
    status: str
    feedbackId: str

class FeedbackListResponse(BaseModel):
    count: int
    items: List[FeedbackItemResponse] = Field(default_factory=list)

class GenericDictResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

class GenericListItemResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    model_config = ConfigDict(extra="allow")
