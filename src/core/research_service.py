"""Research service with lightweight RAG + optional LLM synthesis."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.config.settings import get_settings
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


@dataclass
class RetrievedChunk:
    source: str
    title: str
    content: str
    score: float


class RAGResearchService:
    """Performs lexical retrieval and optional LLM grounded synthesis."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._corpus = self._load_corpus()

    def run(
        self,
        *,
        case_context: str,
        jurisdiction: str,
        case_type: str,
        constraints: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        query = f"{case_type} {jurisdiction} {case_context}".strip()
        top_k = int((constraints or {}).get("top_k", 5) or 5)

        retrieved = self._retrieve(query=query, top_k=top_k)
        summary, llm_used = self._synthesize(query=query, chunks=retrieved)

        precedents = [
            {
                "title": chunk.title,
                "citation": f"Source: {chunk.source}",
                "court": jurisdiction,
            }
            for chunk in retrieved
        ]

        return {
            "status": "SUCCESS",
            "summary": summary,
            "issues": self._infer_issues(case_context=case_context, case_type=case_type),
            "precedents": precedents,
            "requires_human_review": True,
            "llm_used": llm_used,
            "retrieved_count": len(retrieved),
        }

    def _infer_issues(self, *, case_context: str, case_type: str) -> list[str]:
        issues = [case_type] if case_type else []
        text = case_context.lower()
        keywords = {
            "limitation": "Limitation and delay",
            "bail": "Bail eligibility",
            "fraud": "Fraud / cheating allegations",
            "contract": "Contractual breach",
            "property": "Property rights and possession",
        }
        for key, label in keywords.items():
            if key in text and label not in issues:
                issues.append(label)
        return issues or ["General legal analysis"]

    def _tokenize(self, text: str) -> set[str]:
        return set(re.findall(r"[a-zA-Z]{3,}", text.lower()))

    def _retrieve(self, *, query: str, top_k: int) -> list[RetrievedChunk]:
        query_tokens = self._tokenize(query)
        ranked: list[RetrievedChunk] = []

        for source, title, content in self._corpus:
            tokens = self._tokenize(content)
            if not tokens:
                continue
            overlap = len(query_tokens & tokens)
            score = overlap / max(1, len(query_tokens))
            if score <= 0:
                continue
            ranked.append(
                RetrievedChunk(
                    source=source,
                    title=title,
                    content=content[:2500],
                    score=score,
                )
            )

        ranked.sort(key=lambda item: item.score, reverse=True)
        return ranked[:top_k]

    def _synthesize(self, *, query: str, chunks: list[RetrievedChunk]) -> tuple[str, bool]:
        context_blocks = [f"[{idx+1}] {c.title}\n{c.content}" for idx, c in enumerate(chunks)]
        context = "\n\n".join(context_blocks) if context_blocks else "No retrieved corpus context available."

        if self.settings.OPENAI_API_KEY:
            try:
                from openai import OpenAI

                client = OpenAI(api_key=self.settings.OPENAI_API_KEY)
                response = client.chat.completions.create(
                    model=self.settings.OPENAI_MODEL,
                    temperature=0.1,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a legal research assistant. Answer only from provided context. "
                                "If uncertain, say uncertain. End with 'Human review required.'"
                            ),
                        },
                        {
                            "role": "user",
                            "content": (
                                f"Question: {query}\n\nContext:\n{context}\n\n"
                                "Provide a concise summary with citation markers like [1], [2]."
                            ),
                        },
                    ],
                )
                answer = response.choices[0].message.content or ""
                return answer.strip(), True
            except Exception:
                logger.exception("OpenAI synthesis failed, falling back to deterministic summary")

        if not chunks:
            return (
                "No indexed context matched this query. Add legal documents to corpus and retry. "
                "Human review required.",
                False,
            )

        bullets = [f"- [{i+1}] {chunk.title}" for i, chunk in enumerate(chunks[:3])]
        return (
            "Retrieved relevant materials and generated a grounded summary from indexed corpus:\n"
            + "\n".join(bullets)
            + "\nHuman review required.",
            False,
        )

    def _load_corpus(self) -> list[tuple[str, str, str]]:
        """Load lightweight corpus from repository docs/data for retrieval."""
        root = Path(__file__).resolve().parents[2]
        candidate_paths = [root / "docs", root / "data", root / "outputs"]
        corpus: list[tuple[str, str, str]] = []

        for base in candidate_paths:
            if not base.exists():
                continue
            for path in base.rglob("*"):
                if not path.is_file() or path.suffix.lower() not in {".md", ".txt", ".json"}:
                    continue
                try:
                    raw = path.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue
                content = self._normalize_content(path=path, raw=raw)
                if not content.strip():
                    continue
                rel = str(path.relative_to(root))
                corpus.append((rel, path.stem.replace("_", " "), content[:5000]))

        logger.info("Loaded RAG corpus documents=%s", len(corpus))
        return corpus

    def _normalize_content(self, *, path: Path, raw: str) -> str:
        if path.suffix.lower() != ".json":
            return raw
        try:
            parsed = json.loads(raw)
            return json.dumps(parsed, ensure_ascii=False)
        except Exception:
            return raw
