from __future__ import annotations

import hashlib
import math
import os
import re
from collections import OrderedDict
from threading import Lock
from typing import List

from langchain_core.embeddings import Embeddings


class HashEmbeddings(Embeddings):
    """Lightweight deterministic embeddings with no external model dependency."""

    def __init__(self, dimensions: int = 384):
        self._dimensions = max(64, dimensions)
        self._cache_max_entries = max(128, int(os.getenv("VIDHI_EMBED_CACHE_MAX_ENTRIES", "2048")))
        self._cache: "OrderedDict[str, List[float]]" = OrderedDict()
        self._cache_lock = Lock()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed(text)

    def _embed(self, text: str) -> List[float]:
        cache_key = f"{self._dimensions}:{(text or '').strip().lower()}"
        with self._cache_lock:
            cached = self._cache.get(cache_key)
            if cached is not None:
                self._cache.move_to_end(cache_key)
                return list(cached)

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
        normalized = [value / norm for value in vector]
        with self._cache_lock:
            self._cache[cache_key] = normalized
            self._cache.move_to_end(cache_key)
            if len(self._cache) > self._cache_max_entries:
                self._cache.popitem(last=False)
        return list(normalized)
