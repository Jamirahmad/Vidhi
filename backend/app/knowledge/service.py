from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import parse_qs, urlparse

import httpx

from .ingestion_pipeline import KnowledgeIngestionPipeline


class KnowledgeService:
    def __init__(self, root_dir: Path):
        self._pipeline = KnowledgeIngestionPipeline(root_dir=root_dir)
        self._seed_documents_path = root_dir / "backend" / "data" / "knowledge" / "seed_documents.json"
        self._pipeline.bootstrap_from_local_files()
        self._auto_refresh_on_empty = os.getenv("VIDHI_AUTO_REFRESH_PUBLIC_CASES", "true").strip().lower() in {
            "1",
            "true",
            "yes",
        }
        self._did_auto_refresh = False

        self._kb_scope = os.getenv("VIDHI_KB_SCOPE", "indian_penal_courts").strip().lower()
        self._rag_mode = os.getenv("VIDHI_RAG_MODE", "regressive").strip().lower()
        self._local_min_results = int(os.getenv("VIDHI_LOCAL_MIN_RESULTS", "3"))
        self._local_min_top_score = float(os.getenv("VIDHI_LOCAL_MIN_TOP_SCORE", "0.08"))
        self._web_search_provider = os.getenv("VIDHI_WEB_SEARCH_PROVIDER", "searchapi").strip().lower()
        self._searchapi_api_key = (
            os.getenv("SEARCHAPI_API_KEY", "").strip()
            or os.getenv("SEARCH_API_KEY", "").strip()
            or os.getenv("SERPAPI_API_KEY", "").strip()
        )
        self._last_web_error = ""
        self._web_search_country = os.getenv("VIDHI_WEB_SEARCH_COUNTRY", "IN").strip().upper()
        self._web_search_language = os.getenv("VIDHI_WEB_SEARCH_LANGUAGE", "en").strip().lower()
        self._external_endpoints = [
            endpoint.strip()
            for endpoint in os.getenv("VIDHI_EXTERNAL_KNOWLEDGE_ENDPOINTS", "").split(",")
            if endpoint.strip()
        ]
        self._external_timeout_s = float(os.getenv("VIDHI_EXTERNAL_KNOWLEDGE_TIMEOUT_S", "8"))
        self._india_keywords = ("india", "indian")
        self._penal_keywords = (
            "ipc",
            "indian penal code",
            "bharatiya nyaya sanhita",
            "bns",
            "crpc",
            "bnss",
            "criminal",
            "penal",
            "offence",
            "offense",
        )
        self._court_keywords = ("court", "judgment", "judgement", "case", "precedent")
        self._verdict_only = os.getenv("VIDHI_VERDICT_ONLY", "true").strip().lower() in {"1", "true", "yes"}
        self._verdict_keywords = (
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
            "type=j",
        )

    async def search(self, query: str, limit: int = 12) -> List[Dict[str, Any]]:
        local_results = [
            item
            for item in self._pipeline.store.similarity_search(query=query, limit=limit)
            if self._is_allowed_payload(item)
        ]
        if not local_results and self._auto_refresh_on_empty and not self._did_auto_refresh:
            self._did_auto_refresh = True
            await self.refresh_public_cases(years=5, limit=200)
            local_results = [
                item
                for item in self._pipeline.store.similarity_search(query=query, limit=limit)
                if self._is_allowed_payload(item)
            ]

        merged = [
            {
                "id": item.get("id"),
                "title": item.get("title"),
                "category": item.get("category"),
                "summary": item.get("summary"),
                "content": item.get("content"),
            }
            for item in local_results
        ]

        if self._should_fallback(local_results=local_results, limit=limit):
            web_results = await self._search_web(query=query, limit=limit)
            merged.extend(web_results)

            if self._external_endpoints:
                external_results = await self._search_external(query=query, limit=limit)
                merged.extend(external_results)

        deduped: List[Dict[str, Any]] = []
        seen = set()
        for item in merged:
            cleaned = {
                "id": item.get("id"),
                "title": str(item.get("title") or "").strip(),
                "category": str(item.get("category") or "").strip(),
                "summary": str(item.get("summary") or "").strip(),
                "content": self._sanitize_content(
                    title=str(item.get("title") or ""),
                    summary=str(item.get("summary") or ""),
                    content=str(item.get("content") or ""),
                ),
            }
            if not self._is_allowed_payload(cleaned):
                continue
            if self._verdict_only and not self._has_verdict_payload(cleaned):
                continue

            key = (
                cleaned.get("title", "").strip().lower(),
                cleaned.get("content", "").strip()[:240].lower(),
            )
            if key in seen:
                continue
            seen.add(key)
            deduped.append(cleaned)
            if len(deduped) >= limit:
                break

        return deduped

    async def search_provisions(self, query: str, limit: int = 12) -> List[Dict[str, Any]]:
        raw_results = self._pipeline.store.similarity_search(query=query, limit=max(limit * 4, limit, 1))
        if not raw_results and self._auto_refresh_on_empty and not self._did_auto_refresh:
            self._did_auto_refresh = True
            await self.refresh_public_cases(years=5, limit=200)
            raw_results = self._pipeline.store.similarity_search(query=query, limit=max(limit * 4, limit, 1))

        filtered: List[Dict[str, Any]] = []
        seen = set()
        for item in raw_results:
            category = str(item.get("category") or "").strip().lower()
            corpus = " ".join(
                [
                    str(item.get("title") or ""),
                    str(item.get("summary") or ""),
                    str(item.get("content") or ""),
                ]
            ).lower()
            is_provision = category in {"provision", "statute"} or any(
                keyword in corpus for keyword in ("section", "article", "act", "code", "ipc", "bns", "crpc", "bnss")
            )
            if not is_provision:
                continue

            cleaned = {
                "id": item.get("id"),
                "title": str(item.get("title") or "").strip(),
                "category": str(item.get("category") or "").strip(),
                "summary": str(item.get("summary") or "").strip(),
                "content": self._sanitize_content(
                    title=str(item.get("title") or ""),
                    summary=str(item.get("summary") or ""),
                    content=str(item.get("content") or ""),
                ),
                "source_url": str(item.get("source_url") or "").strip(),
            }

            key = (
                cleaned.get("title", "").strip().lower(),
                cleaned.get("content", "").strip()[:240].lower(),
            )
            if key in seen:
                continue
            seen.add(key)
            filtered.append(cleaned)
            if len(filtered) >= limit:
                break

        return filtered

    def search_seed_provisions(self, query: str, limit: int = 12) -> List[Dict[str, Any]]:
        try:
            if not self._seed_documents_path.exists():
                return []
            raw = self._seed_documents_path.read_text(encoding="utf-8")
            data = json.loads(raw)
        except Exception:
            return []

        if not isinstance(data, list):
            return []

        tokens = [token.lower() for token in re.split(r"[^a-zA-Z0-9]+", query or "") if token]
        if not tokens:
            tokens = [str(query or "").lower().strip()] if str(query or "").strip() else []

        scored: List[Dict[str, Any]] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            category = str(item.get("category") or "").strip().lower()
            if category not in {"provision", "statute"}:
                continue

            corpus = " ".join(
                [
                    str(item.get("title") or ""),
                    str(item.get("summary") or ""),
                    str(item.get("text") or ""),
                    " ".join([str(tag) for tag in (item.get("tags") or []) if isinstance(tag, (str, int, float))]),
                ]
            ).lower()

            score = 0
            for token in tokens:
                if token and token in corpus:
                    score += 1
            if score == 0 and tokens:
                continue

            scored.append(
                {
                    "score": score,
                    "id": str(item.get("id") or ""),
                    "title": str(item.get("title") or "").strip(),
                    "category": str(item.get("category") or "").strip(),
                    "summary": str(item.get("summary") or "").strip(),
                    "content": str(item.get("text") or "").strip(),
                    "source_url": str(item.get("source_url") or "").strip(),
                }
            )

        scored.sort(key=lambda row: (-int(row.get("score") or 0), len(str(row.get("title") or ""))))
        if scored:
            return scored[: max(1, limit)]

        # deterministic baseline fallback when query tokens do not match seed text
        baseline: List[Dict[str, Any]] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            category = str(item.get("category") or "").strip().lower()
            if category not in {"provision", "statute"}:
                continue
            baseline.append(
                {
                    "id": str(item.get("id") or ""),
                    "title": str(item.get("title") or "").strip(),
                    "category": str(item.get("category") or "").strip(),
                    "summary": str(item.get("summary") or "").strip(),
                    "content": str(item.get("text") or "").strip(),
                    "source_url": str(item.get("source_url") or "").strip(),
                }
            )
        return baseline[: max(1, limit)]

    async def refresh_public_cases(self, years: int = 5, limit: int = 200) -> Dict[str, Any]:
        return await self._pipeline.refresh_from_public_sources(years=years, limit=limit)

    def _should_fallback(self, local_results: List[Dict[str, Any]], limit: int) -> bool:
        if self._rag_mode not in {"regressive", "fallback"}:
            return False
        if not local_results:
            return True

        top_score = max((float(item.get("score") or 0.0) for item in local_results), default=0.0)
        minimum_expected = min(max(self._local_min_results, 1), max(limit, 1))
        return len(local_results) < minimum_expected and top_score < self._local_min_top_score

    def _is_allowed_payload(self, item: Dict[str, Any]) -> bool:
        corpus = " ".join(
            [
                str(item.get("title") or ""),
                str(item.get("category") or ""),
                str(item.get("summary") or ""),
                str(item.get("content") or ""),
            ]
        )
        return self._matches_scope(corpus)

    def _matches_scope(self, raw_text: str) -> bool:
        if self._kb_scope not in {"indian_penal_courts", "indian-penal-courts", "ipc-courts"}:
            return True

        text = raw_text.lower()
        in_india = any(keyword in text for keyword in self._india_keywords)
        in_penal_domain = any(keyword in text for keyword in self._penal_keywords)
        in_court_context = any(keyword in text for keyword in self._court_keywords)
        return in_india and in_penal_domain and in_court_context

    def _scoped_query(self, query: str) -> str:
        if self._kb_scope in {"indian_penal_courts", "indian-penal-courts", "ipc-courts"}:
            return f"{query.strip()} Indian penal criminal court judgment"
        return query

    @staticmethod
    def _normalize_line_key(line: str) -> str:
        return re.sub(r"[^a-z0-9]+", "", line.lower())

    def _sanitize_content(self, title: str, summary: str, content: str) -> str:
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        if not lines:
            return content.strip()

        title_key = self._normalize_line_key(title)
        summary_key = self._normalize_line_key(summary)
        seen = set()
        cleaned_lines: List[str] = []

        for raw_line in lines:
            normalized_spaces = re.sub(r"\s+", " ", raw_line).strip()
            line_key = self._normalize_line_key(normalized_spaces)
            if not line_key:
                continue

            if line_key in seen:
                continue

            if line_key in {title_key, summary_key} and line_key in seen:
                continue

            seen.add(line_key)
            cleaned_lines.append(normalized_spaces)

        return "\n\n".join(cleaned_lines)

    def _has_verdict_payload(self, item: Dict[str, Any]) -> bool:
        text = " ".join(
            [
                str(item.get("title") or ""),
                str(item.get("summary") or ""),
                str(item.get("content") or ""),
            ]
        ).lower()
        if any(keyword in text for keyword in self._verdict_keywords):
            return True

        match = re.search(r"reference url:\s*(https?://\S+)", text, flags=re.IGNORECASE)
        if not match:
            return False

        url = match.group(1)
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        link_type = (query.get("type", [""])[0] or "").lower()
        if link_type in {"j", "judgment", "judgement", "verdict"}:
            return True

        path = parsed.path.lower()
        return "judgment" in path or "judgement" in path or "verdict" in path

    async def _search_web(self, query: str, limit: int) -> List[Dict[str, Any]]:
        if self._web_search_provider in {"", "none", "disabled"}:
            return []
        return await self._search_searchapi(query=query, limit=limit)

    async def _search_searchapi(self, query: str, limit: int) -> List[Dict[str, Any]]:
        if not self._searchapi_api_key:
            return []

        try:
            max_results = max(1, min(limit, 20))
            params = {
                "api_key": self._searchapi_api_key,
                "engine": "google",
                "q": self._scoped_query(query),
                "num": max_results,
                "gl": self._web_search_country.lower(),
                "hl": self._web_search_language,
            }
            async with httpx.AsyncClient(timeout=self._external_timeout_s) as client:
                response = await client.get("https://www.searchapi.io/api/v1/search", params=params)
            if response.status_code >= 300:
                return []
            data = response.json()
        except Exception:
            return []

        raw_results = data.get("organic_results", [])
        if not isinstance(raw_results, list):
            return []

        out: List[Dict[str, Any]] = []
        for idx, item in enumerate(raw_results):
            if not isinstance(item, dict):
                continue

            title = str(item.get("title") or "Web legal reference").strip()
            url = str(item.get("link") or "").strip()
            summary = str(item.get("snippet") or "Relevant result from SearchApi.io.").strip()
            source = str(item.get("source") or "Google via SearchApi.io").strip()
            rank = item.get("position")
            rank_text = f"Rank: {rank}" if isinstance(rank, int) else "Rank: n/a"
            out.append(
                {
                    "id": f"web-searchapi-{idx}",
                    "title": title,
                    "category": "web-reference",
                    "summary": summary,
                    "content": "\n\n".join(
                        [
                            summary,
                            "Source: SearchApi.io (Google)",
                            f"Reference URL: {url or 'N/A'}",
                            f"Publisher: {source}",
                            rank_text,
                        ]
                    ).strip(),
                }
            )
        return out

    async def _search_external(self, query: str, limit: int) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        scoped_query = self._scoped_query(query)
        for endpoint in self._external_endpoints:
            try:
                async with httpx.AsyncClient(timeout=self._external_timeout_s) as client:
                    response = await client.get(endpoint, params={"q": scoped_query, "limit": limit})
                if response.status_code >= 300:
                    continue

                payload = response.json()
                items = payload if isinstance(payload, list) else payload.get("items", [])
                if not isinstance(items, list):
                    continue

                for idx, item in enumerate(items):
                    if not isinstance(item, dict):
                        continue

                    source_name = str(item.get("source_name") or item.get("source") or "External Knowledge API")
                    source_url = str(item.get("source_url") or item.get("url") or endpoint)
                    out.append(
                        {
                            "id": str(item.get("id") or f"external-{idx}-{source_name}"),
                            "title": str(item.get("title") or "Legal reference"),
                            "category": str(item.get("category") or "external-reference"),
                            "summary": str(item.get("summary") or "Reference returned by external knowledge source."),
                            "content": "\n\n".join(
                                [
                                    str(item.get("content") or item.get("text") or ""),
                                    f"Source: {source_name}",
                                    f"Reference URL: {source_url}",
                                ]
                            ).strip(),
                        }
                    )
            except Exception:
                continue
        return out




    async def live_web_search(self, query: str, limit: int = 10, intent: str = "case_law") -> List[Dict[str, Any]]:
        normalized_intent = (intent or "case_law").strip().lower()
        if normalized_intent not in {"case_law", "provision"}:
            normalized_intent = "case_law"

        if not self._searchapi_api_key:
            self._last_web_error = "searchapi API key is missing."
            return []

        engine_query = self._build_live_query(query=query, intent=normalized_intent)
        try:
            params = {
                "api_key": self._searchapi_api_key,
                "engine": "google",
                "q": engine_query,
                "num": max(1, min(limit, 20)),
                "gl": self._web_search_country.lower(),
                "hl": self._web_search_language,
            }
            async with httpx.AsyncClient(timeout=self._external_timeout_s) as client:
                response = await client.get("https://www.searchapi.io/api/v1/search", params=params)
            if response.status_code >= 300:
                self._last_web_error = f"searchapi HTTP {response.status_code}: {response.text[:180]}"
                return []
            payload = response.json()
        except Exception:
            self._last_web_error = "searchapi request failed due to network or timeout."
            return []

        organic = payload.get("organic_results", [])
        if not isinstance(organic, list):
            self._last_web_error = "searchapi returned invalid organic_results payload."
            return []

        out: List[Dict[str, Any]] = []
        seen_urls = set()
        for idx, item in enumerate(organic):
            if not isinstance(item, dict):
                continue
            url = str(item.get("link") or "").strip()
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)

            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            title = str(item.get("title") or "Legal source").strip()
            snippet = str(item.get("snippet") or "").strip()
            published = str(item.get("date") or "").strip()
            out.append(
                {
                    "id": f"live-searchapi-{normalized_intent}-{idx}",
                    "intent": normalized_intent,
                    "title": title,
                    "snippet": snippet,
                    "url": url,
                    "domain": domain,
                    "publishedAt": published,
                    "provider": "searchapi",
                }
            )
            if len(out) >= limit:
                break

        self._last_web_error = ""
        return out

    def get_last_web_error(self) -> str:
        return self._last_web_error

    def _stable_web_doc_id(self, url: str, title: str) -> str:
        base = (url or "").strip() or (title or "").strip()
        return "searchapi-provision-" + hashlib.sha256(base.encode("utf-8")).hexdigest()[:24]

    def cache_live_provision_results(self, results: List[Dict[str, Any]]) -> int:
        if not results:
            return 0

        today = datetime.now(UTC).strftime("%Y-%m-%d")
        docs: List[Dict[str, Any]] = []
        for item in results:
            if not isinstance(item, dict):
                continue
            url = str(item.get("url") or "").strip()
            title = str(item.get("title") or "Legal provision").strip()
            snippet = str(item.get("snippet") or "").strip()
            if not url:
                continue
            docs.append(
                {
                    "id": self._stable_web_doc_id(url=url, title=title),
                    "title": title,
                    "category": "provision",
                    "summary": snippet or "Provision result from SearchApi.io.",
                    "text": "\n\n".join(
                        [
                            snippet or title,
                            "Source: SearchApi.io (Google)",
                            f"Reference URL: {url}",
                            f"Updated: {today}",
                        ]
                    ).strip(),
                    "source_name": "SearchApi.io (Google)",
                    "source_url": url,
                    "authority": "Public Web Source",
                    "jurisdiction": "India",
                    "tags": ["provision", "searchapi", "cached"],
                    "updated_at": today,
                }
            )

        return self._pipeline.store.add_cases(docs)

    def clear_cached_provision_results(self) -> int:
        deleted_searchapi = self._pipeline.store.delete_by_metadata({"source_name": "SearchApi.io (Google)", "category": "provision"})
        return deleted_searchapi

    async def hybrid_provision_search(self, query: str, limit: int = 12, web_limit: int = 12) -> List[Dict[str, Any]]:
        local_results = await self.search_provisions(query=query, limit=max(limit, 1))
        web_results = await self.live_web_search(query=query, limit=max(web_limit, 1), intent="provision")

        if not local_results and web_results:
            self.cache_live_provision_results(web_results)
            local_results = await self.search_provisions(query=query, limit=max(limit, 1))

        combined: List[Dict[str, Any]] = []
        seen = set()

        def key_for(item: Dict[str, Any]) -> str:
            url = str(item.get("url") or item.get("source_url") or "").strip().lower()
            title = str(item.get("title") or "").strip().lower()
            source = str(item.get("source") or "").strip().lower()
            if url:
                parsed = urlparse(url)
                path = (parsed.path or "").strip()
                # Root/homepage URLs are not unique enough for provisions; include title to avoid collapsing to one item.
                if path in {"", "/"}:
                    return f"root::{parsed.netloc.lower()}::{title}::{source}"
                return f"url::{url}::{source}"
            return f"title::{title}::{source}"

        local_mapped = [
            {
                "id": str(item.get("id") or ""),
                "title": str(item.get("title") or "").strip(),
                "snippet": str(item.get("summary") or "").strip(),
                "url": str(item.get("source_url") or "").strip(),
                "domain": urlparse(str(item.get("source_url") or "").strip()).netloc.lower(),
                "publishedAt": str(item.get("updated_at") or ""),
                "source": "local-kb",
            }
            for item in local_results
        ]

        web_mapped = [
            {
                "id": str(item.get("id") or ""),
                "title": str(item.get("title") or "").strip(),
                "snippet": str(item.get("snippet") or "").strip(),
                "url": str(item.get("url") or "").strip(),
                "domain": str(item.get("domain") or "").strip().lower(),
                "publishedAt": str(item.get("publishedAt") or ""),
                "source": "searchapi-live",
            }
            for item in web_results
        ]

        local_quota = max(1, limit // 2) if local_mapped and web_mapped else limit
        for item in local_mapped[:local_quota]:
            k = key_for(item)
            if k in seen:
                continue
            seen.add(k)
            combined.append(item)

        for item in web_mapped:
            if len(combined) >= limit:
                break
            k = key_for(item)
            if k in seen:
                continue
            seen.add(k)
            combined.append(item)

        for item in local_mapped[local_quota:]:
            if len(combined) >= limit:
                break
            k = key_for(item)
            if k in seen:
                continue
            seen.add(k)
            combined.append(item)

        if not combined:
            seed = self.search_seed_provisions(query=query, limit=limit)
            for item in seed:
                mapped = {
                    "id": str(item.get("id") or ""),
                    "title": str(item.get("title") or "").strip(),
                    "snippet": str(item.get("summary") or "").strip(),
                    "url": str(item.get("source_url") or "").strip(),
                    "domain": urlparse(str(item.get("source_url") or "").strip()).netloc.lower(),
                    "publishedAt": "",
                    "source": "local-kb",
                }
                k = key_for(mapped)
                if k in seen:
                    continue
                seen.add(k)
                combined.append(mapped)
                if len(combined) >= limit:
                    break

        return combined

    def _build_live_query(self, query: str, intent: str) -> str:
        q = (query or "").strip()
        if intent == "provision":
            return f"{q} site:indiacode.nic.in (section OR article OR act) India law"
        return f"{q} site:sci.gov.in (judgment OR judgement OR order) India criminal law"


















