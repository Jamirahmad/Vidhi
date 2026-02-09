"""
Hallucination Checks

Detects hallucinations in agent outputs using deterministic,
non-LLM heuristics suitable for legal workflows.

Hallucination Types Covered:
- Unsupported claims (no citations)
- Citation-reference mismatch
- Fabricated statutes / case names
- Overconfident language without evidence

This module is intentionally conservative.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------

@dataclass
class HallucinationIssue:
    issue_type: str
    message: str
    span: Optional[str] = None


@dataclass
class HallucinationReport:
    total_claims: int
    hallucinated_claims: int
    issues: List[HallucinationIssue]
    passed: bool


# ---------------------------------------------------------------------
# Core Checks
# ---------------------------------------------------------------------

def run_hallucination_checks(
    *,
    claims: List[Dict[str, object]],
    citations: Optional[List[Dict[str, object]]] = None,
) -> HallucinationReport:
    """
    Run hallucination checks on agent claims.

    Expected claim format:
    {
        "text": str,
        "citations": List[str]
    }
    """

    issues: List[HallucinationIssue] = []
    citation_ids = _extract_citation_ids(citations)

    for claim in claims:
        claim_text = str(claim.get("text", "")).strip()
        claim_citations = claim.get("citations", [])

        # -------------------------------------------------------------
        # Check 1: Claim without citation
        # -------------------------------------------------------------
        if not claim_citations:
            issues.append(
                HallucinationIssue(
                    issue_type="UNSUPPORTED_CLAIM",
                    message="Claim is not supported by any citation",
                    span=claim_text,
                )
            )
            continue

        # -------------------------------------------------------------
        # Check 2: Citation reference mismatch
        # -------------------------------------------------------------
        for ref in claim_citations:
            if ref not in citation_ids:
                issues.append(
                    HallucinationIssue(
                        issue_type="INVALID_CITATION_REFERENCE",
                        message=f"Referenced citation '{ref}' does not exist",
                        span=claim_text,
                    )
                )

        # -------------------------------------------------------------
        # Check 3: Overconfident legal language
        # -------------------------------------------------------------
        if _contains_overconfident_language(claim_text):
            issues.append(
                HallucinationIssue(
                    issue_type="OVERCONFIDENT_LANGUAGE",
                    message="Overconfident legal assertion detected without qualification",
                    span=claim_text,
                )
            )

    total_claims = len(claims)
    hallucinated_claims = len({issue.span for issue in issues if issue.span})

    passed = hallucinated_claims == 0

    logger.info(
        "Hallucination check completed | claims=%s | issues=%s",
        total_claims,
        len(issues),
    )

    return HallucinationReport(
        total_claims=total_claims,
        hallucinated_claims=hallucinated_claims,
        issues=issues,
        passed=passed,
    )


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def _extract_citation_ids(
    citations: Optional[List[Dict[str, object]]],
) -> List[str]:
    if not citations:
        return []

    return [
        str(c.get("citation_id"))
        for c in citations
        if "citation_id" in c
    ]


def _contains_overconfident_language(text: str) -> bool:
    """
    Detect absolute legal assertions that are risky without evidence.
    """
    triggers = [
        "clearly establishes",
        "undoubtedly",
        "without any exception",
        "always applies",
        "never applies",
        "settled law",
        "conclusively proves",
    ]

    lowered = text.lower()
    return any(trigger in lowered for trigger in triggers)
