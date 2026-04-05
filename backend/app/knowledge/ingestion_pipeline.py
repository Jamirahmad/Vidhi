from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

from .case_fetcher import SupremeCourtCaseFetcher
from .vector_store import LangChainVectorStore


class KnowledgeIngestionPipeline:
    def __init__(self, root_dir: Path):
        self._root_dir = root_dir
        self._data_dir = root_dir / "backend" / "data" / "knowledge"
        self._court_cases_dir = self._data_dir / "court_cases"
        self._chroma_dir = self._data_dir / "chroma_db"
        self._court_cases_dir.mkdir(parents=True, exist_ok=True)
        self._chroma_dir.mkdir(parents=True, exist_ok=True)
        self._store = LangChainVectorStore(persist_directory=str(self._chroma_dir), collection_name="vidhi_cases")
        self._fetcher = SupremeCourtCaseFetcher()

    @property
    def store(self) -> LangChainVectorStore:
        return self._store

    def bootstrap_from_local_files(self, max_records: int = 2000) -> Dict[str, Any]:
        if self._store.has_documents():
            return {"loaded": 0, "source": "existing_vector_store"}

        loaded_cases: List[Dict[str, Any]] = []
        for file_path in sorted(self._court_cases_dir.glob("authentic_cases_*.json"), reverse=True):
            try:
                raw = json.loads(file_path.read_text(encoding="utf-8"))
            except Exception:
                continue

            entries = raw if isinstance(raw, list) else []
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                if not self._is_within_last_five_years(str(entry.get("updated_at") or "")):
                    continue
                loaded_cases.append(entry)
                if len(loaded_cases) >= max_records:
                    break
            if len(loaded_cases) >= max_records:
                break

        chunks = self._store.add_cases(loaded_cases)
        return {"loaded": len(loaded_cases), "chunks": chunks, "source": "local_json"}

    async def refresh_from_public_sources(self, years: int = 5, limit: int = 200) -> Dict[str, Any]:
        cases = await self._fetcher.fetch_recent_cases(years=years, limit=limit)
        if not cases:
            return {"fetched": 0, "chunks": 0, "saved": ""}

        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        path = self._court_cases_dir / f"authentic_cases_{timestamp}.json"
        path.write_text(json.dumps(cases, indent=2, ensure_ascii=False), encoding="utf-8")

        chunks = self._store.add_cases(cases)
        return {
            "fetched": len(cases),
            "chunks": chunks,
            "saved": str(path),
            "source": "sci.gov.in",
            "windowYears": years,
        }

    @staticmethod
    def _is_within_last_five_years(iso_date: str) -> bool:
        try:
            parsed = datetime.strptime(iso_date[:10], "%Y-%m-%d").date()
        except Exception:
            return False

        now = datetime.now(UTC).date()
        cutoff = now - timedelta(days=365 * 5)
        return parsed >= cutoff


