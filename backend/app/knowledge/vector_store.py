from __future__ import annotations

import hashlib
import re
from typing import Any, Dict, List, Set

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .embeddings import HashEmbeddings


class LangChainVectorStore:
    def __init__(self, persist_directory: str, collection_name: str = "vidhi_cases"):
        self._splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=120)
        self._store = Chroma(
            collection_name=collection_name,
            persist_directory=persist_directory,
            embedding_function=HashEmbeddings(),
        )

    def similarity_search(self, query: str, limit: int = 12) -> List[Dict[str, Any]]:
        if not query.strip():
            return []

        rows = self._store.similarity_search_with_score(query=query, k=max(limit * 4, limit, 1))
        out: List[Dict[str, Any]] = []
        seen_case_ids: Set[str] = set()

        for doc, distance in rows:
            metadata = doc.metadata or {}
            case_id = str(metadata.get("case_id") or self._stable_id(doc.page_content))
            if case_id in seen_case_ids:
                continue
            seen_case_ids.add(case_id)

            score = 1.0 / (1.0 + max(float(distance), 0.0))
            out.append(
                {
                    "id": case_id,
                    "title": str(metadata.get("title") or "Case law reference"),
                    "category": str(metadata.get("category") or "Criminal Law"),
                    "summary": str(metadata.get("summary") or "Relevant case law chunk."),
                    "content": doc.page_content,
                    "score": score,
                    "source_url": str(metadata.get("source_url") or ""),
                    "updated_at": str(metadata.get("updated_at") or ""),
                }
            )
            if len(out) >= limit:
                break

        return out

    def add_cases(self, cases: List[Dict[str, Any]]) -> int:
        if not cases:
            return 0

        docs: List[Document] = []
        ids: List[str] = []
        for case in cases:
            title = str(case.get("title") or "Case law reference").strip()
            summary = str(case.get("summary") or "").strip()
            body = str(case.get("text") or "").strip()
            source_name = str(case.get("source_name") or "Supreme Court of India")
            source_url = str(case.get("source_url") or "")
            updated_at = str(case.get("updated_at") or "")
            category = str(case.get("category") or "Criminal Law")
            jurisdiction = str(case.get("jurisdiction") or "India")
            authority = str(case.get("authority") or "Supreme Court of India")
            case_id = str(case.get("id") or self._stable_id(f"{title}-{updated_at}-{source_url}"))
            tags = case.get("tags") or []
            if not isinstance(tags, list):
                tags = []

            # Replace previous chunks of the same case to avoid stale duplicated content.
            try:
                self._store.delete(where={"case_id": case_id})
            except Exception:
                pass

            main_text = self._clean_main_text(body or summary or title)
            canonical_text = "\n\n".join(
                [
                    main_text,
                    f"Authority: {authority}",
                    f"Jurisdiction: {jurisdiction}",
                    f"Source: {source_name}",
                    f"Reference URL: {source_url}",
                    f"Updated: {updated_at}",
                    f"Tags: {', '.join([str(tag) for tag in tags])}",
                ]
            ).strip()

            chunks = self._splitter.split_text(canonical_text)
            for chunk_index, chunk in enumerate(chunks):
                chunk_id = f"{case_id}-chunk-{chunk_index}"
                ids.append(chunk_id)
                docs.append(
                    Document(
                        page_content=chunk,
                        metadata={
                            "case_id": case_id,
                            "title": title,
                            "summary": summary,
                            "category": category,
                            "source_url": source_url,
                            "source_name": source_name,
                            "updated_at": updated_at,
                            "jurisdiction": jurisdiction,
                            "authority": authority,
                        },
                    )
                )

        self._store.add_documents(documents=docs, ids=ids)
        return len(ids)

    def has_documents(self) -> bool:
        return self._store._collection.count() > 0

    def delete_by_metadata(self, where: Dict[str, Any]) -> int:
        before = self._store._collection.count()
        try:
            self._store.delete(where=where)
        except Exception:
            return 0
        after = self._store._collection.count()
        return max(before - after, 0)

    @staticmethod
    def _clean_main_text(text: str) -> str:
        raw_lines = [line.strip() for line in re.split(r"[\r\n]+", text) if line.strip()]
        deduped_lines: List[str] = []
        seen: Set[str] = set()
        for line in raw_lines:
            normalized = re.sub(r"\s+", " ", line).strip().lower()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            deduped_lines.append(line)
        if not deduped_lines:
            return text.strip()
        return "\n".join(deduped_lines)

    @staticmethod
    def _stable_id(value: str) -> str:
        return hashlib.sha256((value or "").encode("utf-8")).hexdigest()[:24]
