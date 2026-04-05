from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta
from typing import Any, Dict, List
from urllib.parse import parse_qs, urljoin, urlparse

import httpx
from bs4 import BeautifulSoup


class SupremeCourtCaseFetcher:
    """Fetches publicly accessible Supreme Court of India case snippets."""

    def __init__(self, timeout_s: float = 15.0):
        self._timeout_s = timeout_s
        self._source_pages = [
            "https://www.sci.gov.in/",
            "https://www.sci.gov.in/page/2/",
            "https://www.sci.gov.in/page/3/",
        ]
        self._criminal_tokens = (
            "crl",
            "criminal",
            "ipc",
            "bns",
            "bnss",
            "narcotic",
            "state of",
            "murder",
            "bail",
            "dowry",
            "rape",
            "cheating",
            "fiduciary",
            "penal",
        )
        self._verdict_tokens = (
            "judgment",
            "judgement",
            "verdict",
            "disposed",
            "decided",
            "convicted",
            "acquitted",
            "appeal dismissed",
            "appeal allowed",
            "final order",
        )

    async def fetch_recent_cases(self, years: int = 5, limit: int = 200) -> List[Dict[str, Any]]:
        min_date = datetime.now(UTC).date() - timedelta(days=365 * years)
        collected: List[Dict[str, Any]] = []
        seen = set()

        async with httpx.AsyncClient(timeout=self._timeout_s, follow_redirects=True) as client:
            for page_url in self._source_pages:
                try:
                    response = await client.get(page_url)
                except Exception:
                    continue
                if response.status_code >= 300:
                    continue

                soup = BeautifulSoup(response.text, "html.parser")
                for anchor in soup.find_all("a"):
                    label = " ".join(anchor.get_text(" ", strip=True).split())
                    if not label or len(label) < 16:
                        continue

                    parsed_date = self._extract_date(label)
                    if parsed_date is None or parsed_date < min_date:
                        continue
                    if not self._is_criminal_case(label):
                        continue

                    href = (anchor.get("href") or "").strip()
                    source_url = urljoin(page_url, href) if href else page_url
                    if not self._has_verdict_marker(label=label, source_url=source_url):
                        continue

                    case_id = self._build_id(label=label, date_iso=parsed_date.isoformat(), source_url=source_url)
                    if case_id in seen:
                        continue
                    seen.add(case_id)

                    title = self._extract_title(label)
                    summary = self._extract_summary(label)
                    collected.append(
                        {
                            "id": case_id,
                            "title": title,
                            "category": "Criminal Law",
                            "summary": summary,
                            "text": label,
                            "source_name": "Supreme Court of India",
                            "source_url": source_url,
                            "authority": "Supreme Court of India",
                            "jurisdiction": "India",
                            "tags": ["criminal law", "supreme court", "india", "public source", "verdict"],
                            "updated_at": parsed_date.isoformat(),
                        }
                    )
                    if len(collected) >= limit:
                        return collected

        return collected

    def _is_criminal_case(self, text: str) -> bool:
        normalized = text.lower()
        return any(token in normalized for token in self._criminal_tokens)

    def _has_verdict_marker(self, label: str, source_url: str) -> bool:
        normalized = label.lower()
        if any(token in normalized for token in self._verdict_tokens):
            return True

        parsed = urlparse(source_url)
        query = parse_qs(parsed.query)
        link_type = (query.get("type", [""])[0] or "").lower()
        if link_type in {"j", "judgment", "judgement", "verdict"}:
            return True

        path = parsed.path.lower()
        return "judgment" in path or "judgement" in path or "verdict" in path

    @staticmethod
    def _extract_title(text: str) -> str:
        parts = [part.strip() for part in text.split(" - ") if part.strip()]
        return parts[0] if parts else text[:180]

    @staticmethod
    def _extract_summary(text: str) -> str:
        compact = re.sub(r"\s+", " ", text).strip()
        return compact[:320]

    @staticmethod
    def _build_id(label: str, date_iso: str, source_url: str) -> str:
        normalized = f"{label.lower()}|{date_iso}|{source_url.lower()}"
        cleaned = re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")
        return cleaned[:96]

    @staticmethod
    def _extract_date(text: str):
        patterns = [
            r"(\d{2}-[A-Za-z]{3}-\d{4})",
            r"(\d{2}/\d{2}/\d{4})",
            r"(\d{4}-\d{2}-\d{2})",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if not match:
                continue
            value = match.group(1)
            for fmt in ("%d-%b-%Y", "%d/%m/%Y", "%Y-%m-%d"):
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
        return None
