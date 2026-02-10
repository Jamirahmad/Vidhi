"""
High Court Scraper

Generic, configurable scraper for Indian High Court
judgment/order listings.

Designed to be:
- respectful (rate-limited, user-agent set)
- configurable per High Court
- ingestion-pipeline friendly

Aligned with:
- src/ingestion/cleaners/*
- src/ingestion/parsers/*
- docs/design/ingestion_strategy.md
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
# Models
# ---------------------------------------------------------------------

class HighCourtScrapeError(Exception):
    pass


# ---------------------------------------------------------------------
# Scraper
# ---------------------------------------------------------------------

class HighCourtScraper:
    """
    Configurable scraper for High Court judgment listings.
    """

    def __init__(
        self,
        *,
        base_url: str,
        listing_path: str,
        headers: Optional[Dict[str, str]] = None,
        request_delay_sec: float = 1.5,
        timeout_sec: int = 20,
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
        Fetch a listing page HTML.
        """
        url = page_url or urljoin(self.base_url, self.listing_path)

        logger.info("Fetching HC listing page | url=%s", url)

        try:
            response = self.session.get(
                url, timeout=self.timeout_sec
            )
            response.raise_for_status()
        except Exception as exc:
            raise HighCourtScrapeError(
                f"Failed to fetch listing page: {url}"
            ) from exc

        time.sleep(self.request_delay_sec)
        return response.text

    def extract_case_links(self, html: str) -> List[str]:
        """
        Extract judgment/order links from listing HTML.

        NOTE: This is intentionally generic and expects
        HC-specific selectors to be refined later.
        """
        soup = BeautifulSoup(html, "html.parser")
        links: List[str] = []

        for a in soup.find_all("a", href=True):
            href = a["href"]
            if self._looks_like_case_link(href):
                links.append(urljoin(self.base_url, href))

        logger.info("Extracted %s case links", len(links))
        return list(set(links))

    def fetch_case_page(self, *, case_url: str) -> str:
        """
        Fetch individual case page HTML.
        """
        logger.debug("Fetching case page | url=%s", case_url)

        try:
            response = self.session.get(
                case_url, timeout=self.timeout_sec
            )
            response.raise_for_status()
        except Exception as exc:
            raise HighCourtScrapeError(
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
        Generator yielding raw case records:
        {
            "id": str,
            "source": "high_court",
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
            except HighCourtScrapeError as exc:
                logger.warning(str(exc))
                continue

            yield {
                "id": link,
                "source": "high_court",
                "url": link,
                "html": html,
                "metadata": {
                    "court": self.base_url,
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
        Heuristic to identify judgment/order links.
        Conservative by design.
        """
        href_lower = href.lower()
        keywords = ("judgment", "order", "case", "view")

        return any(k in href_lower for k in keywords)
