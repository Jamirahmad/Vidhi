# src/core/config.py

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


def _get_env_str(name: str, default: Optional[str] = None) -> str:
    val = os.getenv(name, default)
    if val is None:
        raise ValueError(f"Missing required environment variable: {name}")
    return str(val)


def _get_env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    raw = raw.strip().lower()
    return raw in ("1", "true", "yes", "y", "on")


def _get_env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw.strip())
    except ValueError as e:
        raise ValueError(f"Environment variable {name} must be an integer. Got: {raw}") from e


def _get_env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw.strip())
    except ValueError as e:
        raise ValueError(f"Environment variable {name} must be a float. Got: {raw}") from e


@dataclass(frozen=True)
class AppConfig:
    """
    Centralized application configuration.

    This config is intentionally strict and explicit because the orchestrator,
    validators, and agents depend on stable toggles and thresholds.
    """

    # ----------------------------
    # App Metadata
    # ----------------------------
    APP_NAME: str = "Vidhi"
    ENVIRONMENT: str = "dev"  # dev | test | prod

    # ----------------------------
    # Logging
    # ----------------------------
    LOG_LEVEL: str = "INFO"

    # ----------------------------
    # Orchestrator Behavior
    # ----------------------------
    ORCHESTRATOR_STRICT_MODE: bool = True
    ORCHESTRATOR_MAX_AGENTS: int = 10
    ORCHESTRATOR_MAX_RETRIES: int = 1
    ORCHESTRATOR_TIMEOUT_SECONDS: int = 120

    # ----------------------------
    # Validation Toggles
    # ----------------------------
    ENABLE_CITATION_VALIDATION: bool = True
    ENABLE_HALLUCINATION_DETECTION: bool = True

    # ----------------------------
    # Citation Validation Rules
    # ----------------------------
    CITATION_MIN_COUNT: int = 1
    CITATION_MAX_COUNT: int = 25
    CITATION_ALLOW_UNCITED_SHORT_ANSWERS: bool = False
    CITATION_SHORT_ANSWER_THRESHOLD_CHARS: int = 350

    # ----------------------------
    # Hallucination Detection Rules
    # ----------------------------
    HALLUCINATION_MAX_RISK_SCORE: float = 0.65
    HALLUCINATION_FLAG_IF_NO_SOURCES: bool = True
    HALLUCINATION_REQUIRE_CITATIONS_FOR_FACTS: bool = True

    # ----------------------------
    # Safety Guardrails
    # ----------------------------
    ENABLE_SAFETY_GUARDRAILS: bool = True
    BLOCK_DISALLOWED_CONTENT: bool = True
    REDACT_SENSITIVE_DATA: bool = True

    # ----------------------------
    # LLM / Model (optional future use)
    # ----------------------------
    MODEL_NAME: str = "gpt-4o-mini"
    MODEL_TEMPERATURE: float = 0.2
    MODEL_MAX_TOKENS: int = 2000

    @staticmethod
    def from_env() -> "AppConfig":
        """
        Loads config from environment variables with safe defaults.
        """

        return AppConfig(
            APP_NAME=_get_env_str("APP_NAME", "Vidhi"),
            ENVIRONMENT=_get_env_str("ENVIRONMENT", "dev"),
            LOG_LEVEL=_get_env_str("LOG_LEVEL", "INFO"),

            ORCHESTRATOR_STRICT_MODE=_get_env_bool("ORCHESTRATOR_STRICT_MODE", True),
            ORCHESTRATOR_MAX_AGENTS=_get_env_int("ORCHESTRATOR_MAX_AGENTS", 10),
            ORCHESTRATOR_MAX_RETRIES=_get_env_int("ORCHESTRATOR_MAX_RETRIES", 1),
            ORCHESTRATOR_TIMEOUT_SECONDS=_get_env_int("ORCHESTRATOR_TIMEOUT_SECONDS", 120),

            ENABLE_CITATION_VALIDATION=_get_env_bool("ENABLE_CITATION_VALIDATION", True),
            ENABLE_HALLUCINATION_DETECTION=_get_env_bool("ENABLE_HALLUCINATION_DETECTION", True),

            CITATION_MIN_COUNT=_get_env_int("CITATION_MIN_COUNT", 1),
            CITATION_MAX_COUNT=_get_env_int("CITATION_MAX_COUNT", 25),
            CITATION_ALLOW_UNCITED_SHORT_ANSWERS=_get_env_bool(
                "CITATION_ALLOW_UNCITED_SHORT_ANSWERS", False
            ),
            CITATION_SHORT_ANSWER_THRESHOLD_CHARS=_get_env_int(
                "CITATION_SHORT_ANSWER_THRESHOLD_CHARS", 350
            ),

            HALLUCINATION_MAX_RISK_SCORE=_get_env_float("HALLUCINATION_MAX_RISK_SCORE", 0.65),
            HALLUCINATION_FLAG_IF_NO_SOURCES=_get_env_bool("HALLUCINATION_FLAG_IF_NO_SOURCES", True),
            HALLUCINATION_REQUIRE_CITATIONS_FOR_FACTS=_get_env_bool(
                "HALLUCINATION_REQUIRE_CITATIONS_FOR_FACTS", True
            ),

            ENABLE_SAFETY_GUARDRAILS=_get_env_bool("ENABLE_SAFETY_GUARDRAILS", True),
            BLOCK_DISALLOWED_CONTENT=_get_env_bool("BLOCK_DISALLOWED_CONTENT", True),
            REDACT_SENSITIVE_DATA=_get_env_bool("REDACT_SENSITIVE_DATA", True),

            MODEL_NAME=_get_env_str("MODEL_NAME", "gpt-4o-mini"),
            MODEL_TEMPERATURE=_get_env_float("MODEL_TEMPERATURE", 0.2),
            MODEL_MAX_TOKENS=_get_env_int("MODEL_MAX_TOKENS", 2000),
        )


# Singleton config object used across application
CONFIG: AppConfig = AppConfig.from_env()
