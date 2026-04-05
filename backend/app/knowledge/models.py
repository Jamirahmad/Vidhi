from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class KnowledgeDocument:
    id: str
    title: str
    category: str
    summary: str
    text: str
    source_name: str
    source_url: str
    authority: str
    jurisdiction: str
    tags: List[str]
    updated_at: str


@dataclass(frozen=True)
class KnowledgeSearchResult:
    document: KnowledgeDocument
    relevance_score: float
    matched_terms: List[str]

    def to_article_payload(self) -> Dict[str, Any]:
        tag_text = ", ".join(self.document.tags[:6]) if self.document.tags else "legal-reference"
        matched_text = ", ".join(self.matched_terms[:8]) if self.matched_terms else "query relevance"
        content = "\n\n".join(
            [
                self.document.text,
                f"Source: {self.document.source_name}",
                f"Authority: {self.document.authority}",
                f"Jurisdiction: {self.document.jurisdiction}",
                f"Reference URL: {self.document.source_url}",
                f"Matched terms: {matched_text}",
                f"Last reviewed: {self.document.updated_at}",
            ]
        )

        return {
            "id": self.document.id,
            "title": self.document.title,
            "category": self.document.category,
            "summary": f"{self.document.summary} (tags: {tag_text})",
            "content": content,
        }
