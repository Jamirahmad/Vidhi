"""
Response Models

Defines all response schemas returned by Vidhi API endpoints.
Ensures consistency, traceability, and human-in-the-loop signaling.
"""

from typing import Optional, Dict, List
from pydantic import BaseModel, Field


# -------------------------------------------------------------------
# Base Response (shared by all workflows)
# -------------------------------------------------------------------

class BaseResponse(BaseModel):
    """
    Common response fields returned by all API endpoints.
    """

    request_id: str = Field(
        ...,
        description="Echoes the client-provided request identifier",
        example="REQ-2026-0001",
    )

    status: str = Field(
        ...,
        description="Execution status of the workflow",
        example="SUCCESS",
    )

    requires_human_review: bool = Field(
        ...,
        description="Indicates whether human review is mandatory before use",
        example=True,
    )

    messages: Optional[List[str]] = Field(
        default_factory=list,
        description="System or agent messages for transparency",
    )

    trace_id: Optional[str] = Field(
        None,
        description="Trace identifier for logs and agent tracing",
        example="TRACE-abc123",
    )


# -------------------------------------------------------------------
# Research Workflow Response
# -------------------------------------------------------------------

class ResearchResponse(BaseResponse):
    """
    Response returned by legal research workflows.
    """

    issues_identified: List[str] = Field(
        default_factory=list,
        description="Key legal issues identified in the case",
    )

    precedents: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Relevant case law and statutory references",
        example=[
            {
                "title": "State of Punjab vs Baldev Singh",
                "citation": "(1999) 6 SCC 172",
                "court": "Supreme Court of India",
            }
        ],
    )

    confidence_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="System confidence in the research output",
    )


# -------------------------------------------------------------------
# Document Generation Workflow Response
# -------------------------------------------------------------------

class DocumentGenerationResponse(BaseResponse):
    """
    Response returned by document drafting workflows.
    """

    document_type: str = Field(
        ...,
        description="Type of legal document generated",
        example="Bail Application",
    )

    draft_text: str = Field(
        ...,
        description="Generated legal document draft",
    )

    warnings: Optional[List[str]] = Field(
        default_factory=list,
        description="Legal or compliance warnings detected",
    )


# -------------------------------------------------------------------
# Compliance Check Workflow Response
# -------------------------------------------------------------------

class ComplianceCheckResponse(BaseResponse):
    """
    Response returned by compliance and safety checks.
    """

    compliance_passed: bool = Field(
        ...,
        description="Whether the document passed all compliance checks",
        example=False,
    )

    findings: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Detailed compliance findings",
        example=[
            {
                "type": "citation_accuracy",
                "severity": "HIGH",
                "message": "Citation could not be verified",
            }
        ],
    )


# -------------------------------------------------------------------
# Feedback Response
# -------------------------------------------------------------------

class FeedbackResponse(BaseModel):
    """
    Response returned after feedback submission.
    """

    status: str = Field(
        ...,
        example="RECEIVED",
    )

    message: str = Field(
        ...,
        example="Feedback recorded successfully",
    )
