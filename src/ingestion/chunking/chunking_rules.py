"""
Chunking Rules

Defines chunking policies and rules based on:
- document type
- source
- legal structure

These rules are consumed by the TextChunker and ingestion pipeline.

Aligned with:
- src/ingestion/chunking/chunker.py
- docs/design/ingestion_strategy.md
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional

from src.config.settings import get_settings

settings = get_settings()


# ---------------------------------------------------------------------
# Document Types
# ---------------------------------------------------------------------

class DocumentType(str, Enum):
    JUDGMENT = "judgment"
    STATUTE = "statute"
    CONTRACT = "contract"
    PLEADING = "pleading"
    COMMENTARY = "commentary"
    UNKNOWN = "unknown"


# ---------------------------------------------------------------------
# Chunking Rule Model
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class ChunkingRule:
    """
    Defines how a document should be chunked.
    """
    chunk_size: int
    chunk_overlap: int
    preserve_sections: bool = False
    description: Optional[str] = None


# ---------------------------------------------------------------------
# Default Rules
# ---------------------------------------------------------------------

DEFAULT_RULE = ChunkingRule(
    chunk_size=settings.CHUNK_SIZE,
    chunk_overlap=settings.CHUNK_OVERLAP,
    preserve_sections=False,
    description="Default character-based chunking",
)


DOCUMENT_TYPE_RULES: Dict[DocumentType, ChunkingRule] = {
    DocumentType.JUDGMENT: ChunkingRule(
        chunk_size=900,
        chunk_overlap=200,
        preserve_sections=True,
        description="Judgments benefit from larger contextual windows",
    ),
    DocumentType.STATUTE: ChunkingRule(
        chunk_size=700,
        chunk_overlap=150,
        preserve_sections=True,
        description="Acts and sections should remain intact where possible",
    ),
    DocumentType.CONTRACT: ChunkingRule(
        chunk_size=800,
        chunk_overlap=200,
        preserve_sections=True,
        description="Clauses often span multiple sentences",
    ),
    DocumentType.PLEADING: ChunkingRule(
        chunk_size=600,
        chunk_overlap=120,
        preserve_sections=False,
        description="Pleadings are more repetitive; smaller chunks suffice",
    ),
    DocumentType.COMMENTARY: ChunkingRule(
        chunk_size=500,
        chunk_overlap=100,
        preserve_sections=False,
        description="Secondary material optimized for retrieval precision",
    ),
}


# ---------------------------------------------------------------------
# Rule Resolution
# ---------------------------------------------------------------------

def resolve_chunking_rule(
    *,
    document_type: DocumentType | str | None,
    override: Optional[ChunkingRule] = None,
) -> ChunkingRule:
    """
    Resolve the effective chunking rule for a document.

    Priority:
    1. Explicit override
    2. Document-type specific rule
    3. Default rule
    """

    if override:
        return override

    if isinstance(document_type, str):
        try:
            document_type = DocumentType(document_type.lower())
        except Exception:
            document_type = DocumentType.UNKNOWN

    if document_type and document_type in DOCUMENT_TYPE_RULES:
        return DOCUMENT_TYPE_RULES[document_type]

    return DEFAULT_RULE
