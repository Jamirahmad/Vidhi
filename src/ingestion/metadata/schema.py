"""
Metadata Schema

Defines canonical metadata fields used across the ingestion,
chunking, retrieval, and evaluation pipelines.

This schema acts as a contract:
- fetchers populate source fields
- extractors enrich document fields
- chunker propagates metadata
- evaluators rely on consistency

Aligned with:
- src/ingestion/fetchers/*
- src/ingestion/metadata/metadata_extractor.py
- src/evaluation/*
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


# ---------------------------------------------------------------------
# Base Metadata
# ---------------------------------------------------------------------

@dataclass
class BaseMetadata:
    """
    Metadata common to all ingested documents.
    """

    # Source & provenance
    source: str
    id: str

    url: Optional[str] = None
    path: Optional[str] = None

    fetch_ts: Optional[float] = None
    upload_ts: Optional[float] = None

    provider: Optional[str] = None

    # Technical
    mime_type: Optional[str] = None
    file_name: Optional[str] = None
    file_size_bytes: Optional[int] = None

    language: Optional[str] = None
    language_confidence: Optional[float] = None


# ---------------------------------------------------------------------
# Legal-Specific Metadata
# ---------------------------------------------------------------------

@dataclass
class LegalMetadata:
    """
    Metadata specific to legal documents.
    """

    court: Optional[str] = None
    tribunal: Optional[str] = None

    case_number: Optional[str] = None
    decision_date: Optional[str] = None
    decision_year: Optional[int] = None

    judges: Optional[List[str]] = field(default_factory=list)

    bench: Optional[str] = None
    jurisdiction: Optional[str] = None

    document_type: Optional[str] = None  # judgment, order, statute, etc.


# ---------------------------------------------------------------------
# Chunk Metadata
# ---------------------------------------------------------------------

@dataclass
class ChunkMetadata:
    """
    Metadata propagated to individual chunks.
    """

    chunk_id: str
    chunk_index: int

    start_char: Optional[int] = None
    end_char: Optional[int] = None

    section_title: Optional[str] = None
    paragraph_number: Optional[int] = None


# ---------------------------------------------------------------------
# Unified Metadata
# ---------------------------------------------------------------------

@dataclass
class IngestionMetadata:
    """
    Unified metadata object attached to documents and chunks.
    """

    base: BaseMetadata
    legal: LegalMetadata
    chunk: Optional[ChunkMetadata] = None
