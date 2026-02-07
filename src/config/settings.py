# src/config/settings.py

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env (if present)
load_dotenv()


def _get_bool(key: str, default: bool = False) -> bool:
    val = os.getenv(key, str(default)).strip().lower()
    return val in ("true", "1", "yes", "y", "on")


def _get_int(key: str, default: int) -> int:
    try:
        return int(os.getenv(key, str(default)).strip())
    except Exception:
        return default


def _get_float(key: str, default: float) -> float:
    try:
        return float(os.getenv(key, str(default)).strip())
    except Exception:
        return default


def _get_str(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()


def _get_path(key: str, default: str) -> Path:
    return Path(os.getenv(key, default)).expanduser().resolve()


@dataclass(frozen=True)
class Settings:
    # ----------------------------
    # Application Settings
    # ----------------------------
    APP_NAME: str = _get_str("APP_NAME", "Vidhi")
    APP_ENV: str = _get_str("APP_ENV", "development")  # development | staging | production
    DEBUG: bool = _get_bool("DEBUG", True)
    LOG_LEVEL: str = _get_str("LOG_LEVEL", "INFO")

    # ----------------------------
    # API Server (FastAPI)
    # ----------------------------
    API_HOST: str = _get_str("API_HOST", "0.0.0.0")
    API_PORT: int = _get_int("API_PORT", 8000)

    # ----------------------------
    # Streamlit UI
    # ----------------------------
    UI_HOST: str = _get_str("UI_HOST", "0.0.0.0")
    UI_PORT: int = _get_int("UI_PORT", 8501)

    # ----------------------------
    # LLM Provider (OpenAI)
    # ----------------------------
    OPENAI_API_KEY: str = _get_str("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = _get_str("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_EMBEDDING_MODEL: str = _get_str("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

    # Optional Azure OpenAI
    AZURE_OPENAI_API_KEY: str = _get_str("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_ENDPOINT: str = _get_str("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_DEPLOYMENT_NAME: str = _get_str("AZURE_OPENAI_DEPLOYMENT_NAME", "")

    # ----------------------------
    # Vector Store Configuration
    # ----------------------------
    VECTOR_STORE_TYPE: str = _get_str("VECTOR_STORE_TYPE", "chroma")  # chroma | faiss
    CHROMA_DB_PATH: Path = _get_path("CHROMA_DB_PATH", "./vectorstore/chroma_db")
    FAISS_INDEX_PATH: Path = _get_path("FAISS_INDEX_PATH", "./vectorstore/faiss_index")

    # ----------------------------
    # Data Paths (Local Storage)
    # ----------------------------
    RAW_DATA_PATH: Path = _get_path("RAW_DATA_PATH", "./data/raw")
    PROCESSED_DATA_PATH: Path = _get_path("PROCESSED_DATA_PATH", "./data/processed")
    CHUNKS_PATH: Path = _get_path("CHUNKS_PATH", "./data/chunks")
    OUTPUTS_PATH: Path = _get_path("OUTPUTS_PATH", "./outputs")

    # ----------------------------
    # Document Uploads
    # ----------------------------
    USER_UPLOAD_PATH: Path = _get_path("USER_UPLOAD_PATH", "./data/raw/user_uploads")
    MAX_UPLOAD_SIZE_MB: int = _get_int("MAX_UPLOAD_SIZE_MB", 25)

    # ----------------------------
    # Ingestion Settings
    # ----------------------------
    ENABLE_OCR: bool = _get_bool("ENABLE_OCR", True)
    OCR_LANGUAGE: str = _get_str("OCR_LANGUAGE", "eng+hin")

    CHUNK_SIZE: int = _get_int("CHUNK_SIZE", 800)
    CHUNK_OVERLAP: int = _get_int("CHUNK_OVERLAP", 150)

    # ----------------------------
    # Retrieval / RAG Settings
    # ----------------------------
    TOP_K_RESULTS: int = _get_int("TOP_K_RESULTS", 5)
    RERANK_RESULTS: bool = _get_bool("RERANK_RESULTS", True)
    MAX_CONTEXT_TOKENS: int = _get_int("MAX_CONTEXT_TOKENS", 6000)

    # ----------------------------
    # Citation Validation
    # ----------------------------
    ENABLE_CITATION_VALIDATION: bool = _get_bool("ENABLE_CITATION_VALIDATION", True)
    CITATION_CONFIDENCE_THRESHOLD: float = _get_float("CITATION_CONFIDENCE_THRESHOLD", 0.70)

    # ----------------------------
    # Rate Limiting / Safety
    # ----------------------------
    ENABLE_RATE_LIMITING: bool = _get_bool("ENABLE_RATE_LIMITING", True)
    REQUESTS_PER_MINUTE: int = _get_int("REQUESTS_PER_MINUTE", 60)
    ENABLE_SAFETY_GUARDRAILS: bool = _get_bool("ENABLE_SAFETY_GUARDRAILS", True)

    # ----------------------------
    # Storage Options
    # ----------------------------
    STORAGE_BACKEND: str = _get_str("STORAGE_BACKEND", "local")  # local | s3

    # AWS S3 Settings
    AWS_ACCESS_KEY_ID: str = _get_str("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = _get_str("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION: str = _get_str("AWS_REGION", "ap-south-1")
    S3_BUCKET_NAME: str = _get_str("S3_BUCKET_NAME", "")

    # ----------------------------
    # LangSmith / Tracing (Optional)
    # ----------------------------
    LANGSMITH_API_KEY: str = _get_str("LANGSMITH_API_KEY", "")
    LANGSMITH_PROJECT: str = _get_str("LANGSMITH_PROJECT", "vidhi-capstone")
    ENABLE_TRACING: bool = _get_bool("ENABLE_TRACING", False)

    # ----------------------------
    # Monitoring / Logging Outputs
    # ----------------------------
    LOG_DIR: Path = _get_path("LOG_DIR", "./logs")
    AGENT_TRACE_LOG: Path = _get_path("AGENT_TRACE_LOG", "./logs/agent_traces.log")
    RETRIEVAL_LOG: Path = _get_path("RETRIEVAL_LOG", "./logs/retrieval.log")
    APP_LOG: Path = _get_path("APP_LOG", "./logs/app.log")

    # ----------------------------
    # Security / Secrets
    # ----------------------------
    SECRET_KEY: str = _get_str("SECRET_KEY", "replace_this_with_random_string")
    JWT_SECRET_KEY: str = _get_str("JWT_SECRET_KEY", "replace_this_with_another_random_string")

    # ----------------------------
    # Deployment Mode
    # ----------------------------
    DEPLOYMENT_MODE: str = _get_str("DEPLOYMENT_MODE", "local")  # local | aws | streamlit_cloud | render | replit

    # ----------------------------
    # Validation Helpers
    # ----------------------------
    def validate(self) -> None:
        """
        Validates key environment settings required for runtime.
        This is intentionally strict only where required.
        """
        if self.VECTOR_STORE_TYPE not in ("chroma", "faiss"):
            raise ValueError("VECTOR_STORE_TYPE must be 'chroma' or 'faiss'")

        if self.STORAGE_BACKEND not in ("local", "s3"):
            raise ValueError("STORAGE_BACKEND must be 'local' or 's3'")

        if self.DEPLOYMENT_MODE not in ("local", "aws", "streamlit_cloud", "render", "replit"):
            raise ValueError("DEPLOYMENT_MODE must be one of: local/aws/streamlit_cloud/render/replit")

        if self.TOP_K_RESULTS <= 0:
            raise ValueError("TOP_K_RESULTS must be greater than 0")

        if self.CHUNK_SIZE <= 0:
            raise ValueError("CHUNK_SIZE must be greater than 0")

        if self.CHUNK_OVERLAP < 0:
            raise ValueError("CHUNK_OVERLAP cannot be negative")

        if self.MAX_CONTEXT_TOKENS <= 0:
            raise ValueError("MAX_CONTEXT_TOKENS must be greater than 0")

        if not (0.0 <= self.CITATION_CONFIDENCE_THRESHOLD <= 1.0):
            raise ValueError("CITATION_CONFIDENCE_THRESHOLD must be between 0.0 and 1.0")

    def ensure_directories(self) -> None:
        """
        Creates required directories if they do not exist.
        """
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.RAW_DATA_PATH.mkdir(parents=True, exist_ok=True)
        self.PROCESSED_DATA_PATH.mkdir(parents=True, exist_ok=True)
        self.CHUNKS_PATH.mkdir(parents=True, exist_ok=True)
        self.OUTPUTS_PATH.mkdir(parents=True, exist_ok=True)
        self.USER_UPLOAD_PATH.mkdir(parents=True, exist_ok=True)

        if self.VECTOR_STORE_TYPE == "chroma":
            self.CHROMA_DB_PATH.mkdir(parents=True, exist_ok=True)
        elif self.VECTOR_STORE_TYPE == "faiss":
            self.FAISS_INDEX_PATH.mkdir(parents=True, exist_ok=True)


# Singleton settings object
settings = Settings()
