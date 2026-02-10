"""
HTML Parser

Parses raw HTML pages from legal sources (HC, SC, Tribunals,
Indian Kanoon) into structured plain text suitable for
cleaning and chunking.

Design goals:
- Conservative extraction
- Structure preservation
- Source-agnostic behavior

Aligned with:
- src/ingestion/fetchers/*
- src/ingestion/cleaners/*
- src/ingestion/metadata/*
"""

from __future__ import annotations

from typing import List, Optional

from bs4 import BeautifulSoup, NavigableString, Tag

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------

class HTMLParser:
    """
    Generic HTML parser for legal documents.
    """

    BLOCK_TAGS = {
        "p",
        "div",
        "section",
        "article",
        "pre",
        "blockquote",
        "li",
    }

    HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}

    REMOVE_TAGS = {
        "script",
        "style",
        "noscript",
        "header",
        "footer",
        "nav",
        "aside",
        "form",
    }

    @classmethod
    def parse(
        cls,
        *,
        html: str,
        preserve_headings: bool = True,
    ) -> str:
        """
        Parse HTML into structured plain text.
        """
        if not html:
            return ""

        soup = BeautifulSoup(html, "html.parser")

        cls._remove_noise(soup)

        blocks: List[str] = []

        body = soup.body or soup
        for element in body.descendants:
            if isinstance(element, Tag):
                if cls._is_heading(element) and preserve_headings:
                    text = cls._get_text(element)
                    if text:
                        blocks.append(text.upper())
                elif cls._is_block(element):
                    text = cls._get_text(element)
                    if text:
                        blocks.append(text)

        parsed_text = "\n\n".join(blocks)

        logger.debug(
            "HTML parsed | blocks=%s | length=%s",
            len(blocks),
            len(parsed_text),
        )

        return parsed_text

    # -----------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------

    @classmethod
    def _remove_noise(cls, soup: BeautifulSoup) -> None:
        """
        Remove non-content tags.
        """
        for tag in soup.find_all(cls.REMOVE_TAGS):
            tag.decompose()

    @classmethod
    def _is_block(cls, tag: Tag) -> bool:
        return tag.name in cls.BLOCK_TAGS

    @classmethod
    def _is_heading(cls, tag: Tag) -> bool:
        return tag.name in cls.HEADING_TAGS

    @staticmethod
    def _get_text(tag: Tag) -> Optional[str]:
        """
        Extract visible text from a tag.
        """
        text_parts: List[str] = []

        for node in tag.descendants:
            if isinstance(node, NavigableString):
                text = str(node).strip()
                if text:
                    text_parts.append(text)

        text = " ".join(text_parts).strip()
        return text if text else None
