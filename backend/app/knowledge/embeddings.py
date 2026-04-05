from __future__ import annotations

import hashlib
import math
import re
from typing import List

from langchain_core.embeddings import Embeddings


class HashEmbeddings(Embeddings):
    """Lightweight deterministic embeddings with no external model dependency."""

    def __init__(self, dimensions: int = 384):
        self._dimensions = max(64, dimensions)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed(text)

    def _embed(self, text: str) -> List[float]:
        vector = [0.0] * self._dimensions
        tokens = re.findall(r"[a-zA-Z0-9_]+", (text or "").lower())
        if not tokens:
            return vector

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self._dimensions
            sign = 1.0 if (digest[4] & 1) == 0 else -1.0
            vector[index] += sign

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]
