from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from threading import Lock
from typing import Iterable, List

from .models import KnowledgeDocument, KnowledgeSearchResult


class KnowledgeRepository:
    def __init__(self, db_path: Path, seed_dir: Path):
        self._db_path = db_path
        self._seed_dir = seed_dir
        self._lock = Lock()
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize(self) -> None:
        with self._lock:
            conn = self._connect()
            try:
                conn.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS knowledge_documents (
                      id TEXT PRIMARY KEY,
                      title TEXT NOT NULL,
                      category TEXT NOT NULL,
                      summary TEXT NOT NULL,
                      text TEXT NOT NULL,
                      source_name TEXT NOT NULL,
                      source_url TEXT NOT NULL,
                      authority TEXT NOT NULL,
                      jurisdiction TEXT NOT NULL,
                      tags TEXT NOT NULL,
                      updated_at TEXT NOT NULL
                    );

                    CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_documents_fts
                    USING fts5(title, text, tags, content='knowledge_documents', content_rowid='rowid');

                    CREATE TRIGGER IF NOT EXISTS knowledge_documents_ai AFTER INSERT ON knowledge_documents BEGIN
                      INSERT INTO knowledge_documents_fts(rowid, title, text, tags)
                      VALUES (new.rowid, new.title, new.text, new.tags);
                    END;

                    CREATE TRIGGER IF NOT EXISTS knowledge_documents_ad AFTER DELETE ON knowledge_documents BEGIN
                      INSERT INTO knowledge_documents_fts(knowledge_documents_fts, rowid, title, text, tags)
                      VALUES('delete', old.rowid, old.title, old.text, old.tags);
                    END;

                    CREATE TRIGGER IF NOT EXISTS knowledge_documents_au AFTER UPDATE ON knowledge_documents BEGIN
                      INSERT INTO knowledge_documents_fts(knowledge_documents_fts, rowid, title, text, tags)
                      VALUES('delete', old.rowid, old.title, old.text, old.tags);
                      INSERT INTO knowledge_documents_fts(rowid, title, text, tags)
                      VALUES (new.rowid, new.title, new.text, new.tags);
                    END;
                    """
                )

                count = conn.execute("SELECT COUNT(1) as c FROM knowledge_documents").fetchone()["c"]
                if count == 0:
                    self._seed(conn)

                conn.commit()
            finally:
                conn.close()

    def _seed(self, conn: sqlite3.Connection) -> None:
        seed_files = sorted(self._seed_dir.glob("*.json"))
        docs = []
        for path in seed_files:
            raw = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(raw, list):
                docs.extend(raw)

        for doc in docs:
            tags = doc.get("tags") or []
            if not isinstance(tags, list):
                tags = []
            conn.execute(
                """
                INSERT OR REPLACE INTO knowledge_documents (
                  id, title, category, summary, text, source_name, source_url,
                  authority, jurisdiction, tags, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    doc["id"],
                    doc["title"],
                    doc["category"],
                    doc["summary"],
                    doc["text"],
                    doc["source_name"],
                    doc["source_url"],
                    doc["authority"],
                    doc.get("jurisdiction", "India"),
                    ", ".join([str(tag) for tag in tags]),
                    doc.get("updated_at", "2026-01-01"),
                ),
            )

    @staticmethod
    def _to_match_query(query: str) -> str:
        tokens = [token.strip() for token in query.replace("\n", " ").split(" ") if token.strip()]
        if not tokens:
            return ""

        quoted = ["\"" + token.replace(chr(34), "") + "\"*" for token in tokens]
        return " OR ".join(quoted)

    def search(self, query: str, limit: int = 12) -> List[KnowledgeSearchResult]:
        clean_query = query.strip()
        if not clean_query:
            return []

        with self._lock:
            conn = self._connect()
            try:
                match_query = self._to_match_query(clean_query)
                rows: Iterable[sqlite3.Row]
                if match_query:
                    rows = conn.execute(
                        """
                        SELECT
                          d.id,
                          d.title,
                          d.category,
                          d.summary,
                          d.text,
                          d.source_name,
                          d.source_url,
                          d.authority,
                          d.jurisdiction,
                          d.tags,
                          d.updated_at,
                          bm25(knowledge_documents_fts) as rank
                        FROM knowledge_documents_fts f
                        JOIN knowledge_documents d ON d.rowid = f.rowid
                        WHERE knowledge_documents_fts MATCH ?
                        ORDER BY rank ASC
                        LIMIT ?
                        """,
                        (match_query, limit),
                    ).fetchall()
                else:
                    rows = []

                if not rows:
                    like_query = f"%{clean_query}%"
                    rows = conn.execute(
                        """
                        SELECT
                          id,
                          title,
                          category,
                          summary,
                          text,
                          source_name,
                          source_url,
                          authority,
                          jurisdiction,
                          tags,
                          updated_at,
                          999.0 as rank
                        FROM knowledge_documents
                        WHERE title LIKE ? OR summary LIKE ? OR text LIKE ? OR tags LIKE ?
                        LIMIT ?
                        """,
                        (like_query, like_query, like_query, like_query, limit),
                    ).fetchall()

                query_tokens = {token.lower() for token in clean_query.split() if token.strip()}
                results: List[KnowledgeSearchResult] = []
                for row in rows:
                    text = f"{row['title']} {row['summary']} {row['text']} {row['tags']}".lower()
                    matched = sorted([token for token in query_tokens if token in text])
                    rank = float(row["rank"]) if row["rank"] is not None else 999.0
                    score = 1.0 / (1.0 + max(rank, 0.0))
                    document = KnowledgeDocument(
                        id=row["id"],
                        title=row["title"],
                        category=row["category"],
                        summary=row["summary"],
                        text=row["text"],
                        source_name=row["source_name"],
                        source_url=row["source_url"],
                        authority=row["authority"],
                        jurisdiction=row["jurisdiction"],
                        tags=[tag.strip() for tag in row["tags"].split(",") if tag.strip()],
                        updated_at=row["updated_at"],
                    )
                    results.append(
                        KnowledgeSearchResult(
                            document=document,
                            relevance_score=score,
                            matched_terms=matched,
                        )
                    )

                return results
            finally:
                conn.close()
