"""
Supreme Court of India Scraper

Conservative, configurable scraper for Supreme Court of India
judgments and orders.

IMPORTANT:
- No CAPTCHA bypass
- No restricted endpoints
- Respect robots.txt and Terms of Use

Aligned with:
- src/ingestion/fetchers/hc_scraper.py
- src/ingestion/fetchers/indian_kanoon_connector.py
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

class SupremeCourtScrapeError(Exception):
    """Base error for Supreme Court scraper."""


# ---------------------------------------------------------------------
# Scraper
# ---------------------------------------------------------------------

class SupremeCourtScraper:
    """
    Scraper for Supreme Court of India public judgment listings.
    """

    def __init__(
        self,
        *,
        base_url: str,
        listing_path: str,
        headers: Optional[Dict[str, str]] = None,
        request_delay_sec: float = 2.0,
        timeout_sec: int = 25,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.listing_path = listing_path
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

    def fetch_listing_page(self, *, page_url: Optional[str] = None) -> str:
        """
        Fetch the Supreme Court listing page HTML.
        """
        url = page_url or urljoin(self.base_url, self.listing_path)

        logger.info("Fetching SC listing page | url=%s", url)

        try:
            response = self.session.get(
                url, timeout=self.timeout_sec
            )
            response.raise_for_status()
        except Exception as exc:
            raise SupremeCourtScrapeError(
                f"Failed to fetch SC listing page: {url}"
            ) from exc

        time.sleep(self.request_delay_sec)
        return response.text

    def extract_case_links(self, html: str) -> List[str]:
        """
        Extract judgment/order links from listing HTML.

        Conservative approach:
        - no reliance on CSS classes
        - filters by link intent
        """
        soup = BeautifulSoup(html, "html.parser")
        links: List[str] = []

        for anchor in soup.find_all("a", href=True):
            href = anchor["href"]
            if self._looks_like_case_link(href):
                links.append(urljoin(self.base_url, href))

        unique_links = list(dict.fromkeys(links))

        logger.info(
            "Extracted %s SC case links",
            len(unique_links),
        )
        return unique_links

    def fetch_case_page(self, *, case_url: str) -> str:
        """
        Fetch individual Supreme Court case page HTML.
        """
        logger.debug("Fetching SC case page | url=%s", case_url)

        try:
            response = self.session.get(
                case_url, timeout=self.timeout_sec
            )
            response.raise_for_status()
        except Exception as exc:
            raise SupremeCourtScrapeError(
                f"Failed to fetch SC case page: {case_url}"
            ) from exc

        time.sleep(self.request_delay_sec)
        return response.text

    def scrape_cases(
        self,
        *,
        max_cases: Optional[int] = None,
    ) -> Iterable[Dict[str, object]]:
        """
        Generator yielding raw Supreme Court case records.

        Output format:
        {
            "id": str,
            "source": "supreme_court",
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
            except SupremeCourtScrapeError as exc:
                logger.warning(str(exc))
                continue

            yield {
                "id": link,
                "source": "supreme_court",
                "url": link,
                "html": html,
                "metadata": {
                    "court": "Supreme Court of India",
                    "fetch_ts": time.time(),
                },
            }

            count += 1

    # -----------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------

    @staticmethod
    def _looks_like_case_link(href: str) -> bool:
        """
        Heuristic to identify Supreme Court judgment/order links.
        Designed to minimize false positives.
        """
        href_lower = href.lower()

        keywords = (
            "judgment",
            "order",
            "case",
            "diary",
            "sc",
            "judis",
        )

        return any(keyword in href_lower for keyword in keywords)
