"""
Indian Kanoon Connector

Ethical, rate-limited connector for retrieving publicly available
legal documents from Indian Kanoon for academic and research use.

IMPORTANT:
- This connector must be used in compliance with Indian Kanoon's Terms of Service.
- No captcha bypassing, authentication circumvention, or bulk scraping.

Aligned with:
- src/ingestion/fetchers/hc_scraper.py
- src/ingestion/parsers/*
- docs/design/ingestion_strategy.md
"""

from __future__ import annotations

import time
from typing import Dict, Iterable, List, Optional
from urllib.parse import urlencode, urljoin

import requests

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------

class IndianKanoonError(Exception):
    """Base error for Indian Kanoon connector."""


# ---------------------------------------------------------------------
# Connector
# ---------------------------------------------------------------------

class IndianKanoonConnector:
    """
    Connector for Indian Kanoon public search and document pages.
    """

    BASE_URL = "https://indiankanoon.org"

    def __init__(
        self,
        *,
        request_delay_sec: float = 2.0,
        timeout_sec: int = 20,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self.request_delay_sec = request_delay_sec
        self.timeout_sec = timeout_sec

        self.session = requests.Session()
        self.session.headers.update(
            headers
            or {
                "User-Agent": (
                    "LegalAIResearchBot/1.0 "
                    "(academic, non-commercial use)"
                )
            }
        )

    # -----------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------

    def search(
        self,
        *,
        query: str,
        max_results: int = 10,
        court: Optional[str] = None,
    ) -> List[str]:
        """
        Perform a search query and return document URLs.

        This uses the public search interface.
        """
        params = {"q": query}
        if court:
            params["court"] = court

        search_url = urljoin(
            self.BASE_URL, "/search/?" + urlencode(params)
        )

        logger.info("Indian Kanoon search | query=%s", query)

        html = self._get(search_url)
        links = self._extract_document_links(html)

        return links[:max_results]

    def fetch_document(self, *, document_url: str) -> Dict[str, object]:
        """
        Fetch a single document page.

        Returns a raw ingestion record:
        {
            "id": str,
            "source": "indian_kanoon",
            "url": str,
            "html": str,
            "metadata": dict
        }
        """
        logger.debug("Fetching Indian Kanoon document | url=%s", document_url)

        html = self._get(document_url)

        return {
            "id": document_url,
            "source": "indian_kanoon",
            "url": document_url,
            "html": html,
            "metadata": {
                "provider": "Indian Kanoon",
                "fetch_ts": time.time(),
            },
        }

    def fetch_by_query(
        self,
        *,
        query: str,
        max_documents: int = 5,
        court: Optional[str] = None,
    ) -> Iterable[Dict[str, object]]:
        """
        High-level generator: search → fetch documents.
        """
        links = self.search(
            query=query,
            max_results=max_documents,
            court=court,
        )

        for link in links:
            try:
                yield self.fetch_document(document_url=link)
            except IndianKanoonError as exc:
                logger.warning(str(exc))
                continue

    # -----------------------------------------------------------------
    # Internal Helpers
    # -----------------------------------------------------------------

    def _get(self, url: str) -> str:
        try:
            response = self.session.get(
                url, timeout=self.timeout_sec
            )
            response.raise_for_status()
        except Exception as exc:
            raise IndianKanoonError(
                f"Failed to fetch URL: {url}"
            ) from exc

        time.sleep(self.request_delay_sec)
        return response.text

    @staticmethod
    def _extract_document_links(html: str) -> List[str]:
        """
        Extract document links conservatively.

        NOTE:
        We intentionally avoid BeautifulSoup here to keep
        this connector lightweight and non-invasive.
        """
        links: List[str] = []

        for line in html.splitlines():
            if 'href="/doc/' in line:
                start = line.find('href="') + 6
                end = line.find('"', start)
                href = line[start:end]

                if href.startswith("/doc/"):
                    links.append(
                        urljoin(
                            IndianKanoonConnector.BASE_URL, href
                        )
                    )

        unique_links = list(dict.fromkeys(links))
        logger.info(
            "Extracted %s Indian Kanoon document links",
            len(unique_links),
        )
        return unique_links
