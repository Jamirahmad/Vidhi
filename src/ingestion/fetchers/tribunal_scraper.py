"""
Tribunal Scraper

Generic, configurable scraper for Indian tribunals such as:
- NCLT
- ITAT
- CAT
- NGT
- SAT
- APTEL

Designed to handle structural inconsistency across tribunal websites
while maintaining a unified ingestion contract.

IMPORTANT:
- No CAPTCHA bypass
- No restricted endpoints
- Respect tribunal-specific Terms of Use

Aligned with:
- src/ingestion/fetchers/hc_scraper.py
- src/ingestion/fetchers/sc_scraper.py
- ingestion metadata-first architecture
"""

from __future__ import annotations

import time
from typing import Dict, Iterable, List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------

class TribunalScrapeError(Exception):
    """Base error for Tribunal scraper."""


# ---------------------------------------------------------------------
# Scraper
# ---------------------------------------------------------------------

class TribunalScraper:
    """
    Configurable scraper for Indian tribunal judgment/order listings.
    """

    def __init__(
        self,
        *,
        tribunal_name: str,
        base_url: str,
        listing_path: str,
        link_keywords: Optional[List[str]] = None,
        headers: Optional[Dict[str, str]] = None,
        request_delay_sec: float = 2.0,
        timeout_sec: int = 25,
    ) -> None:
        self.tribunal_name = tribunal_name
        self.base_url = base_url.rstrip("/")
        self.listing_path = listing_path
        self.request_delay_sec = request_delay_sec
        self.timeout_sec = timeout_sec
        self.link_keywords = link_keywords or [
            "order",
            "judgment",
            "appeal",
            "case",
            "petition",
        ]

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

    def fetch_listing_page(self, *, page_url: Optional[str] = None) -> str:
        """
        Fetch tribunal listing page HTML.
        """
        url = page_url or urljoin(self.base_url, self.listing_path)

        logger.info(
            "Fetching tribunal listing | tribunal=%s | url=%s",
            self.tribunal_name,
            url,
        )

        try:
            response = self.session.get(
                url, timeout=self.timeout_sec
            )
            response.raise_for_status()
        except Exception as exc:
            raise TribunalScrapeError(
                f"Failed to fetch listing page: {url}"
            ) from exc

        time.sleep(self.request_delay_sec)
        return response.text

    def extract_case_links(self, html: str) -> List[str]:
        """
        Extract judgment/order links from tribunal listing HTML.

        Uses keyword-based heuristics due to inconsistent DOMs.
        """
        soup = BeautifulSoup(html, "html.parser")
        links: List[str] = []

        for anchor in soup.find_all("a", href=True):
            href = anchor["href"]
            if self._looks_like_case_link(href):
                links.append(urljoin(self.base_url, href))

        unique_links = list(dict.fromkeys(links))

        logger.info(
            "Extracted %s tribunal case links | tribunal=%s",
            len(unique_links),
            self.tribunal_name,
        )

        return unique_links

    def fetch_case_page(self, *, case_url: str) -> str:
        """
        Fetch individual tribunal case page HTML.
        """
        logger.debug(
            "Fetching tribunal case page | tribunal=%s | url=%s",
            self.tribunal_name,
            case_url,
        )

        try:
            response = self.session.get(
                case_url, timeout=self.timeout_sec
            )
            response.raise_for_status()
        except Exception as exc:
            raise TribunalScrapeError(
                f"Failed to fetch case page: {case_url}"
            ) from exc

        time.sleep(self.request_delay_sec)
        return response.text

    def scrape_cases(
        self,
        *,
        max_cases: Optional[int] = None,
    ) -> Iterable[Dict[str, object]]:
        """
        Generator yielding raw tribunal case records.

        Output format:
        {
            "id": str,
            "source": "tribunal",
            "url": str,
            "html": str,
            "metadata": dict
        }
        """
        listing_html = self.fetch_listing_page()
        case_links = self.extract_case_links(listing_html)

        count = 0
        for link in case_links:
            if max_cases and count >= max_cases:
                break

            try:
                html = self.fetch_case_page(case_url=link)
            except TribunalScrapeError as exc:
                logger.warning(str(exc))
                continue

            yield {
                "id": link,
                "source": "tribunal",
                "url": link,
                "html": html,
                "metadata": {
                    "tribunal": self.tribunal_name,
                    "base_url": self.base_url,
                    "fetch_ts": time.time(),
                },
            }

            count += 1

    # -----------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------

    def _looks_like_case_link(self, href: str) -> bool:
        """
        Heuristic to identify tribunal judgment/order links.
        Conservative by design.
        """
        href_lower = href.lower()
        return any(keyword in href_lower for keyword in self.link_keywords)
