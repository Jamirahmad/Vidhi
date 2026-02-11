# src/core/config.py

from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv


class ConfigError(Exception):
    """Raised when mandatory configuration is missing or invalid."""


def _get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    """Fetch environment variable safely."""
    return os.getenv(name, default)


def _require_env(name: str) -> str:
    """Fetch a mandatory environment variable or raise a ConfigError."""
    value = os.getenv(name)
    if value is None or not value.strip():
        raise ConfigError(f"Missing required environment variable: {name}")
    return value.strip()


def _to_bool(value: Optional[str], default: bool = False) -> bool:
    """Convert env string to bool."""
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _to_int(value: Optional[str], default: int) -> int:
    """Convert env string to int."""
    if value is None or not value.strip():
        return default
    try:
        return int(value.strip())
    except ValueError:
        return default


class AppConfig:
    """
    Centralized configuration for Vidhi.

    Loads from environment variables (supports .env file via python-dotenv).
    Designed for:
    - Fail-fast validation
    - Central source of truth
    - Clean access across modules
    """

    def __init__(self) -> None:
        # Load .env file (safe if missing)
        load_dotenv(override=False)

        # -------------------------
        # Core Environment
        # -------------------------
        self.env: str = _get_env("VIDHI_ENV", "dev")
        self.debug: bool = _to_bool(_get_env("VIDHI_DEBUG"), default=False)

        # -------------------------
        # LLM / OpenAI / Providers
        # -------------------------
        self.openai_api_key: Optional[str] = _get_env("OPENAI_API_KEY")
        self.openai_model: str = _get_env("OPENAI_MODEL", "gpt-4o-mini")
        self.embedding_model: str = _get_env(
            "EMBEDDING_MODEL", "text-embedding-3-small"
        )

        # -------------------------
        # Vectorstore / Chroma
        # -------------------------
        self.vectorstore_dir: str = _get_env("VECTORSTORE_DIR", "vectorstore")
        self.collection_name: str = _get_env("VECTORSTORE_COLLECTION", "vidhi_cases")

        # -------------------------
        # Logging
        # -------------------------
        self.log_dir: str = _get_env("LOG_DIR", "logs")
        self.log_level: str = _get_env("LOG_LEVEL", "INFO")

        # -------------------------
        # Pipeline Controls
        # -------------------------
        self.enable_citations: bool = _to_bool(
            _get_env("ENABLE_CITATIONS"), default=True
        )
        self.enable_guardrails: bool = _to_bool(
            _get_env("ENABLE_GUARDRAILS"), default=True
        )
        self.enable_hallucination_detection: bool = _to_bool(
            _get_env("ENABLE_HALLUCINATION_DETECTION"), default=True
        )

        self.max_context_documents: int = _to_int(
            _get_env("MAX_CONTEXT_DOCUMENTS"), default=10
        )

        # -------------------------
        # Optional Paths
        # -------------------------
        self.output_dir: str = _get_env("OUTPUT_DIR", "outputs")

        # -------------------------
        # Validation / Fail-fast
        # -------------------------
        self._validate()

    def _validate(self) -> None:
        """
        Validate configuration. This should fail-fast in production.
        """

        # OPENAI key is required only if you are actually calling OpenAI
        if self.env.lower() in {"prod", "production"}:
            if not self.openai_api_key:
                raise ConfigError(
                    "OPENAI_API_KEY is required in production environment."
                )

        if not self.openai_model.strip():
            raise ConfigError("OPENAI_MODEL cannot be empty.")

        if not self.embedding_model.strip():
            raise ConfigError("EMBEDDING_MODEL cannot be empty.")

        if self.max_context_documents <= 0:
            raise ConfigError("MAX_CONTEXT_DOCUMENTS must be > 0.")

        if not self.vectorstore_dir.strip():
            raise ConfigError("VECTORSTORE_DIR cannot be empty.")

        if not self.collection_name.strip():
            raise ConfigError("VECTORSTORE_COLLECTION cannot be empty.")

        if not self.log_level.strip():
            raise ConfigError("LOG_LEVEL cannot be empty.")

    def masked_secrets(self) -> list[str]:
        """
        Returns a list of secrets that should be masked in logs.
        """
        secrets = []
        if self.openai_api_key:
            secrets.append(self.openai_api_key)
        return secrets

    def as_dict(self) -> dict:
        """Return config as dict for debugging (secrets not included)."""
        return {
            "env": self.env,
            "debug": self.debug,
            "openai_model": self.openai_model,
            "embedding_model": self.embedding_model,
            "vectorstore_dir": self.vectorstore_dir,
            "collection_name": self.collection_name,
            "log_dir": self.log_dir,
            "log_level": self.log_level,
            "enable_citations": self.enable_citations,
            "enable_guardrails": self.enable_guardrails,
            "enable_hallucination_detection": self.enable_hallucination_detection,
            "max_context_documents": self.max_context_documents,
            "output_dir": self.output_dir,
        }


@lru_cache(maxsize=1)
def get_config() -> AppConfig:
    """
    Cached config loader.
    Use this everywhere instead of creating AppConfig repeatedly.
    """
    return AppConfig()


# Backward-compatible alias (if older code expects `config`)
config = get_config()
