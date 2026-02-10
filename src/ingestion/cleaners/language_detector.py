"""
Language Detector

Detects the primary language of a document for downstream
processing (chunking rules, retrieval filters, evaluation).

Designed to be:
- lightweight
- deterministic-first
- safe for legal ingestion pipelines
"""

from __future__ import annotations

from typing import Dict, Optional

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------
# Simple Heuristic-Based Detector
# ---------------------------------------------------------------------

class LanguageDetector:
    """
    Lightweight language detector using character heuristics.

    This avoids heavy dependencies and works well for
    common legal document languages.
    """

    # Unicode ranges for quick detection
    _UNICODE_RANGES = {
        "en": [(0x0041, 0x007A)],  # Basic Latin
        "hi": [(0x0900, 0x097F)],  # Devanagari
        "bn": [(0x0980, 0x09FF)],  # Bengali
        "ta": [(0x0B80, 0x0BFF)],  # Tamil
        "te": [(0x0C00, 0x0C7F)],  # Telugu
        "kn": [(0x0C80, 0x0CFF)],  # Kannada
        "ml": [(0x0D00, 0x0D7F)],  # Malayalam
    }

    @classmethod
    def detect(cls, text: str, *, min_chars: int = 100) -> Dict[str, Optional[str]]:
        """
        Detect primary language of text.

        Returns:
        {
            "language": "en",
            "confidence": 0.92,
            "method": "unicode_heuristic"
        }
        """

        if not text or len(text.strip()) < min_chars:
            logger.debug("Insufficient text for language detection")
            return {
                "language": None,
                "confidence": None,
                "method": "insufficient_text",
            }

        counts = {lang: 0 for lang in cls._UNICODE_RANGES}
        total_chars = 0

        for ch in text:
            code_point = ord(ch)
            total_chars += 1

            for lang, ranges in cls._UNICODE_RANGES.items():
                if any(start <= code_point <= end for start, end in ranges):
                    counts[lang] += 1
                    break

        if total_chars == 0:
            return {
                "language": None,
                "confidence": None,
                "method": "empty_text",
            }

        detected_lang = max(counts, key=counts.get)
        confidence = counts[detected_lang] / total_chars

        logger.debug(
            "Language detected | language=%s | confidence=%.2f",
            detected_lang,
            confidence,
        )

        return {
            "language": detected_lang,
            "confidence": round(confidence, 2),
            "method": "unicode_heuristic",
        }


# ---------------------------------------------------------------------
# Convenience Helper
# ---------------------------------------------------------------------

def detect_language_metadata(text: str) -> Dict[str, Optional[str]]:
    """
    Convenience wrapper to attach language metadata during ingestion.
    """
    return LanguageDetector.detect(text)
