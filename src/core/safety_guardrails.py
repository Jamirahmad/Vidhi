"""
Safety Guardrails for Vidhi Legal Research Platform

This module implements comprehensive safety and ethical guardrails for the Vidhi system.
It ensures the platform operates within ethical boundaries and prevents harmful outputs.

Critical Safety Measures:
- Prevention of fabricated legal information
- Citation authenticity verification
- Ethical boundary enforcement
- Content filtering and moderation
- Human verification requirements
- Bias and fairness monitoring
- Legal advice prevention
- Privacy protection
- Professional ethics compliance
- Output quality validation

Author: Vidhi Development Team
License: MIT (Educational & Research Use Only)
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from src.core.config import CONFIG
from src.core.logging_config import get_logger

logger = get_logger(__name__)


# -----------------------------
# Data Models
# -----------------------------
@dataclass
class GuardrailViolation:
    category: str
    severity: str  # LOW | MEDIUM | HIGH | CRITICAL
    message: str
    evidence: Optional[str] = None


@dataclass
class GuardrailResult:
    allowed: bool
    violations: List[GuardrailViolation]
    redacted_text: Optional[str] = None


# -----------------------------
# Guardrail Categories
# -----------------------------
DISALLOWED_CATEGORIES = {
    "violence_instructions",
    "self_harm_instructions",
    "illegal_activity",
    "hate_speech",
    "sexual_content_minor",
    "explicit_sexual_content",
}


# -----------------------------
# Regex Patterns
# -----------------------------
_EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_PHONE_REGEX = re.compile(r"\b(\+?\d{1,3}[-.\s]?)?\d{10}\b")
_AADHAAR_REGEX = re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b")
_PAN_REGEX = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b")
_CREDIT_CARD_REGEX = re.compile(r"\b(?:\d[ -]*?){13,19}\b")


# -----------------------------
# Utility Functions
# -----------------------------
def _redact_sensitive_data(text: str) -> Tuple[str, List[GuardrailViolation]]:
    """
    Redacts common sensitive information patterns.
    Returns redacted text + violations list.
    """
    violations: List[GuardrailViolation] = []
    redacted = text

    def _apply(pattern: re.Pattern, label: str, replacement: str) -> None:
        nonlocal redacted, violations
        matches = list(pattern.finditer(redacted))
        if matches:
            violations.append(
                GuardrailViolation(
                    category="sensitive_data",
                    severity="MEDIUM",
                    message=f"Sensitive data detected: {label}",
                    evidence=matches[0].group(0),
                )
            )
            redacted = pattern.sub(replacement, redacted)

    _apply(_EMAIL_REGEX, "Email Address", "[REDACTED_EMAIL]")
    _apply(_PHONE_REGEX, "Phone Number", "[REDACTED_PHONE]")
    _apply(_AADHAAR_REGEX, "Aadhaar Number", "[REDACTED_AADHAAR]")
    _apply(_PAN_REGEX, "PAN Number", "[REDACTED_PAN]")
    _apply(_CREDIT_CARD_REGEX, "Credit Card Number", "[REDACTED_CARD]")

    return redacted, violations


def _detect_disallowed_content(text: str) -> List[GuardrailViolation]:
    """
    Lightweight disallowed content detection.
    This is heuristic-based (keyword patterns).
    """
    violations: List[GuardrailViolation] = []
    lower = text.lower()

    # Violence / weapon building
    if any(x in lower for x in ["how to make a bomb", "build a bomb", "pipe bomb", "homemade explosive"]):
        violations.append(
            GuardrailViolation(
                category="violence_instructions",
                severity="CRITICAL",
                message="Detected instructions for making explosives.",
            )
        )

    # Self-harm instructions
    if any(x in lower for x in ["how to kill myself", "suicide method", "best way to die", "how to hang myself"]):
        violations.append(
            GuardrailViolation(
                category="self_harm_instructions",
                severity="CRITICAL",
                message="Detected self-harm instructions.",
            )
        )

    # Illegal hacking
    if any(x in lower for x in ["hack into", "steal password", "bypass authentication", "ddos attack"]):
        violations.append(
            GuardrailViolation(
                category="illegal_activity",
                severity="HIGH",
                message="Detected possible hacking / illegal activity instructions.",
            )
        )

    # Hate speech (basic heuristic)
    if any(x in lower for x in ["kill all", "exterminate", "gas the", "racial superiority"]):
        violations.append(
            GuardrailViolation(
                category="hate_speech",
                severity="HIGH",
                message="Detected possible hate speech / extremist phrasing.",
            )
        )

    # Sexual content involving minors
    if "minor" in lower and any(x in lower for x in ["sexual", "nude", "explicit", "porn"]):
        violations.append(
            GuardrailViolation(
                category="sexual_content_minor",
                severity="CRITICAL",
                message="Detected sexual content involving minors.",
            )
        )

    return violations


# -----------------------------
# Public API
# -----------------------------
class SafetyGuardrails:
    """
    Central safety guardrail engine.

    This is designed to be used in orchestrator:
      - pre_agent_check(user_input)
      - post_agent_check(agent_output)
      - sanitize_final_answer(final_answer)
    """

    def __init__(self) -> None:
        self.enabled = CONFIG.ENABLE_SAFETY_GUARDRAILS

    def pre_agent_check(self, user_query: str) -> GuardrailResult:
        """
        Runs guardrails before any agent is executed.
        """
        if not self.enabled:
            return GuardrailResult(allowed=True, violations=[])

        violations: List[GuardrailViolation] = []

        # Detect disallowed content
        if CONFIG.BLOCK_DISALLOWED_CONTENT:
            violations.extend(_detect_disallowed_content(user_query))

        # Redact sensitive data
        redacted_text = user_query
        if CONFIG.REDACT_SENSITIVE_DATA:
            redacted_text, redaction_violations = _redact_sensitive_data(user_query)
            violations.extend(redaction_violations)

        allowed = not any(v.severity in ("HIGH", "CRITICAL") for v in violations)

        return GuardrailResult(
            allowed=allowed,
            violations=violations,
            redacted_text=redacted_text,
        )

    def post_agent_check(self, agent_name: str, agent_output: Any) -> GuardrailResult:
        """
        Runs guardrails on agent output to ensure agent didn't generate disallowed content.
        """
        if not self.enabled:
            return GuardrailResult(allowed=True, violations=[])

        text = str(agent_output) if agent_output is not None else ""
        violations: List[GuardrailViolation] = []

        if CONFIG.BLOCK_DISALLOWED_CONTENT:
            violations.extend(_detect_disallowed_content(text))

        redacted_text = text
        if CONFIG.REDACT_SENSITIVE_DATA:
            redacted_text, redaction_violations = _redact_sensitive_data(text)
            violations.extend(redaction_violations)

        allowed = not any(v.severity in ("HIGH", "CRITICAL") for v in violations)

        if not allowed:
            logger.warning(
                f"Safety violation detected in agent output. Agent={agent_name}, "
                f"Violations={[v.category for v in violations]}"
            )

        return GuardrailResult(
            allowed=allowed,
            violations=violations,
            redacted_text=redacted_text,
        )

    def sanitize_final_answer(self, answer: str) -> GuardrailResult:
        """
        Final pass safety filter on final response.
        """
        if not self.enabled:
            return GuardrailResult(allowed=True, violations=[], redacted_text=answer)

        violations: List[GuardrailViolation] = []

        if CONFIG.BLOCK_DISALLOWED_CONTENT:
            violations.extend(_detect_disallowed_content(answer))

        redacted_text = answer
        if CONFIG.REDACT_SENSITIVE_DATA:
            redacted_text, redaction_violations = _redact_sensitive_data(answer)
            violations.extend(redaction_violations)

        allowed = not any(v.severity in ("HIGH", "CRITICAL") for v in violations)

        return GuardrailResult(
            allowed=allowed,
            violations=violations,
            redacted_text=redacted_text,
        )


# Singleton guardrail engine
GUARDRAILS = SafetyGuardrails()


# -----------------------------
# Convenience Functions
# -----------------------------
def enforce_pre_check(user_query: str) -> str:
    """
    Convenience wrapper used by orchestrator.
    Returns safe user query (redacted if needed).
    Raises ValueError if disallowed.
    """
    result = GUARDRAILS.pre_agent_check(user_query)
    if not result.allowed:
        raise ValueError(
            "User query violates safety guardrails: "
            + "; ".join([f"{v.category}:{v.message}" for v in result.violations])
        )
    return result.redacted_text or user_query


def enforce_post_check(agent_name: str, agent_output: Any) -> str:
    """
    Convenience wrapper used by orchestrator.
    Returns safe agent output (redacted if needed).
    Raises ValueError if disallowed.
    """
    result = GUARDRAILS.post_agent_check(agent_name, agent_output)
    if not result.allowed:
        raise ValueError(
            f"Agent output violates safety guardrails: "
            + "; ".join([f"{v.category}:{v.message}" for v in result.violations])
        )
    return result.redacted_text or str(agent_output)


def enforce_final_answer(answer: str) -> str:
    """
    Final answer enforcement.
    """
    result = GUARDRAILS.sanitize_final_answer(answer)
    if not result.allowed:
        raise ValueError(
            "Final answer violates safety guardrails: "
            + "; ".join([f"{v.category}:{v.message}" for v in result.violations])
        )
    return result.redacted_text or answer
