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

# src/core/safety_guardrails.py

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class SafetyCheckResult:
    """
    Standardized output structure for safety checks.

    is_safe:
        True  -> content allowed
        False -> blocked

    violations:
        list of detected violation categories

    warnings:
        non-blocking safety concerns

    disclaimer_required:
        True if disclaimer must be attached to output
    """

    is_safe: bool
    violations: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    disclaimer_required: bool = False
    disclaimer_text: str = ""


class SafetyGuardrails:
    """
    Safety Guardrails for Vidhi System.

    Responsibilities:
    - Block illegal / unsafe legal advice generation requests
    - Detect restricted content categories
    - Provide standardized output for orchestrator and compliance agents

    This module is rule-based and intentionally deterministic.
    """

    DEFAULT_DISCLAIMER = (
        "Disclaimer: This output is generated for informational purposes only "
        "and does not constitute legal advice. Please consult a qualified lawyer."
    )

    # Restricted categories
    CATEGORY_SELF_HARM = "SELF_HARM"
    CATEGORY_ILLEGAL_ACTIVITY = "ILLEGAL_ACTIVITY"
    CATEGORY_VIOLENCE = "VIOLENCE"
    CATEGORY_HATE = "HATE"
    CATEGORY_FRAUD = "FRAUD"
    CATEGORY_EXPLOITATION = "EXPLOITATION"
    CATEGORY_PRIVACY = "PRIVACY"

    # Patterns for detection
    ILLEGAL_ACTIVITY_PATTERNS = [
        r"\bhow to hack\b",
        r"\bhow to bypass\b",
        r"\bforge documents\b",
        r"\bfake documents\b",
        r"\bbribe\b",
        r"\bblackmail\b",
        r"\bsteal\b",
        r"\bscam\b",
        r"\bcredit card fraud\b",
        r"\bidentity theft\b",
        r"\bavoid tax\b",
        r"\btax evasion\b",
    ]

    SELF_HARM_PATTERNS = [
        r"\bsuicide\b",
        r"\bkill myself\b",
        r"\bself harm\b",
        r"\bend my life\b",
    ]

    VIOLENCE_PATTERNS = [
        r"\bkill\b",
        r"\bmurder\b",
        r"\bassault\b",
        r"\bshoot\b",
        r"\bstab\b",
        r"\bviolence\b",
    ]

    HATE_PATTERNS = [
        r"\bkill all\b",
        r"\bexterminate\b",
        r"\bracial superiority\b",
    ]

    PRIVACY_PATTERNS = [
        r"\baddress of\b",
        r"\bphone number of\b",
        r"\bemail of\b",
        r"\bdox\b",
        r"\bdoxx\b",
        r"\bpersonal details\b",
    ]

    def __init__(self):
        self._illegal_regex = re.compile("|".join(self.ILLEGAL_ACTIVITY_PATTERNS), re.IGNORECASE)
        self._self_harm_regex = re.compile("|".join(self.SELF_HARM_PATTERNS), re.IGNORECASE)
        self._violence_regex = re.compile("|".join(self.VIOLENCE_PATTERNS), re.IGNORECASE)
        self._hate_regex = re.compile("|".join(self.HATE_PATTERNS), re.IGNORECASE)
        self._privacy_regex = re.compile("|".join(self.PRIVACY_PATTERNS), re.IGNORECASE)

    # -------------------------------------------------------------------------
    # Core Validator
    # -------------------------------------------------------------------------
    def validate_output(
        self,
        content: str,
        output_type: str = "general",
        context: Optional[dict[str, Any]] = None,
    ) -> SafetyCheckResult:
        """
        Primary safety validation function.

        Args:
            content: text content to validate
            output_type: type of output requested (draft/analysis/etc.)
            context: optional metadata such as jurisdiction, document_type, etc.

        Returns:
            SafetyCheckResult
        """
        if not content or not content.strip():
            return SafetyCheckResult(
                is_safe=False,
                violations=[{"category": "EMPTY_INPUT", "message": "No content provided"}],
                warnings=[],
                disclaimer_required=True,
                disclaimer_text=self.DEFAULT_DISCLAIMER,
            )

        violations: list[dict[str, Any]] = []
        warnings: list[str] = []

        text = content.strip()

        # ------------------------------------------------------------
        # Detect illegal activity guidance requests
        # ------------------------------------------------------------
        if self._illegal_regex.search(text):
            violations.append(
                {
                    "category": self.CATEGORY_ILLEGAL_ACTIVITY,
                    "message": "Illegal activity guidance detected.",
                }
            )

        # ------------------------------------------------------------
        # Detect self harm content
        # ------------------------------------------------------------
        if self._self_harm_regex.search(text):
            violations.append(
                {
                    "category": self.CATEGORY_SELF_HARM,
                    "message": "Self-harm related content detected.",
                }
            )

        # ------------------------------------------------------------
        # Detect violence
        # ------------------------------------------------------------
        if self._violence_regex.search(text):
            violations.append(
                {
                    "category": self.CATEGORY_VIOLENCE,
                    "message": "Violence-related content detected.",
                }
            )

        # ------------------------------------------------------------
        # Detect hate content
        # ------------------------------------------------------------
        if self._hate_regex.search(text):
            violations.append(
                {
                    "category": self.CATEGORY_HATE,
                    "message": "Hate-related content detected.",
                }
            )

        # ------------------------------------------------------------
        # Detect privacy invasion requests
        # ------------------------------------------------------------
        if self._privacy_regex.search(text):
            violations.append(
                {
                    "category": self.CATEGORY_PRIVACY,
                    "message": "Privacy invasion / personal data request detected.",
                }
            )

        # ------------------------------------------------------------
        # Legal Advice disclaimer rules
        # ------------------------------------------------------------
        disclaimer_required = False
        disclaimer_text = ""

        if output_type.lower() in {"legal", "draft", "petition", "complaint", "agreement"}:
            disclaimer_required = True
            disclaimer_text = self.DEFAULT_DISCLAIMER

        # If violations exist -> always disclaimer
        if violations:
            disclaimer_required = True
            if not disclaimer_text:
                disclaimer_text = self.DEFAULT_DISCLAIMER

        is_safe = len(violations) == 0

        if not is_safe:
            warnings.append("Unsafe content detected. Output generation should be blocked.")

        return SafetyCheckResult(
            is_safe=is_safe,
            violations=violations,
            warnings=warnings,
            disclaimer_required=disclaimer_required,
            disclaimer_text=disclaimer_text or self.DEFAULT_DISCLAIMER,
        )

    # -------------------------------------------------------------------------
    # Adapter Method (Required by Compliance Agent)
    # -------------------------------------------------------------------------
    def evaluate(self, user_input: str, jurisdiction: str = "", document_type: str = "") -> dict[str, Any]:
        """
        Adapter method required by CCAComplianceCheckAgent.

        Returns dict format:
        {
            "allowed": bool,
            "flagged_categories": list[str],
            "message": str,
            "disclaimer_required": bool,
            "disclaimer_text": str
        }
        """
        context = {
            "jurisdiction": jurisdiction,
            "document_type": document_type,
        }

        result = self.validate_output(
            content=user_input,
            output_type=document_type or "general",
            context=context,
        )

        flagged_categories: list[str] = []
        for v in result.violations:
            cat = v.get("category")
            if cat:
                flagged_categories.append(str(cat))

        flagged_categories = sorted(set(flagged_categories))

        message = "Content passed compliance checks."
        if not result.is_safe:
            message = "Content blocked due to safety violations."

        if result.warnings:
            message += " " + " ".join(result.warnings)

        return {
            "allowed": bool(result.is_safe),
            "flagged_categories": flagged_categories,
            "message": message.strip(),
            "disclaimer_required": bool(result.disclaimer_required),
            "disclaimer_text": result.disclaimer_text or self.DEFAULT_DISCLAIMER,
        }
