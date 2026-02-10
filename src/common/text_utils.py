"""
Text Utilities

Shared, low-level text processing utilities used across
validation, quality checks, and safety layers.

All functions are deterministic and side-effect free.
"""

from __future__ import annotations

import re
from typing import List


# ---------------------------------------------------------------------
# Absolute / Overconfident Language Detection
# ---------------------------------------------------------------------

ABSOLUTE_PHRASES = [
    "always",
    "never",
    "guarantees",
    "guaranteed",
    "must",
    "clearly",
    "undoubtedly",
    "certainly",
    "without exception",
    "no doubt",
]


def contains_absolute_language(text: str) -> bool:
    """
    Detects presence of absolute or overconfident language.
    """
    lowered = text.lower()
    return any(phrase in lowered for phrase in ABSOLUTE_PHRASES)


def extract_absolute_phrases(text: str) -> List[str]:
    """
    Returns a list of absolute phrases found in the text.
    """
    lowered = text.lower()
    return [p for p in ABSOLUTE_PHRASES if p in lowered]


# ---------------------------------------------------------------------
# Citation Signals
# ---------------------------------------------------------------------

CITATION_PATTERNS = [
    r"\bAIR\s\d{4}\b",
    r"\bSCC\b",
    r"\bSCR\b",
    r"\bILR\b",
    r"\bvs\.?\b",
    r"\bv\.?\b",
    r"\bSection\s+\d+",
    r"\bArticle\s+\d+",
]


def contains_citation_markers(text: str) -> bool:
    """
    Detects whether text contains any legal citation markers.
    """
    for pattern in CITATION_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return True
    return False


# ---------------------------------------------------------------------
# Text Normalization
# ---------------------------------------------------------------------

def normalize_text(text: str) -> str:
    """
    Normalizes text for comparison:
    - lowercases
    - removes extra whitespace
    """
    return re.sub(r"\s+", " ", text.strip().lower())


# ---------------------------------------------------------------------
# Sentence & Length Heuristics
# ---------------------------------------------------------------------

def sentence_count(text: str) -> int:
    """
    Rough sentence count based on punctuation.
    """
    return len(re.findall(r"[.!?]", text))


def is_text_too_short(text: str, min_words: int = 30) -> bool:
    """
    Determines if text is too short to be meaningful.
    """
    return len(text.split()) < min_words


def is_text_too_long(text: str, max_words: int = 2000) -> bool:
    """
    Determines if text is excessively long.
    """
    return len(text.split()) > max_words


# ---------------------------------------------------------------------
# Neutrality & Tone
# ---------------------------------------------------------------------

ADVICE_PHRASES = [
    "you should",
    "you must",
    "it is advised",
    "we recommend",
    "it is mandatory",
]


def contains_legal_advice(text: str) -> bool:
    """
    Detects direct legal advice phrasing.
    """
    lowered = text.lower()
    return any(phrase in lowered for phrase in ADVICE_PHRASES)


# ---------------------------------------------------------------------
# Public exports
# ---------------------------------------------------------------------

__all__ = [
    "contains_absolute_language",
    "extract_absolute_phrases",
    "contains_citation_markers",
    "normalize_text",
    "sentence_count",
    "is_text_too_short",
    "is_text_too_long",
    "contains_legal_advice",
]
