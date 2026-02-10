"""
Cache Manager

Centralized caching abstraction with TTL support.
Designed to be backend-agnostic (in-memory now, Redis later).

Suitable for:
- embedding cache
- retrieval results
- metadata lookups
- expensive parsing outputs
"""

from __future__ import annotations

import time
import threading
from typing import Any, Dict, Optional

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------

class CacheManagerError(RuntimeError):
    pass


# ---------------------------------------------------------------------
# Cache Entry
# ---------------------------------------------------------------------

class _CacheEntry:
    """
    Internal cache entry representation.
    """

    __slots__ = ("value", "expires_at")

    def __init__(self, value: Any, ttl_seconds: Optional[int]) -> None:
        self.value = value
        self.expires_at = (
            time.time() + ttl_seconds if ttl_seconds else None
        )

    def is_expired(self) -> bool:
        return self.expires_at is not None and time.time() > self.expires_at


# ---------------------------------------------------------------------
# Cache Manager
# ---------------------------------------------------------------------

class CacheManager:
    """
    Thread-safe cache manager with TTL support.
    """

    def __init__(
        self,
        *,
        default_ttl_seconds: Optional[int] = None,
        max_entries: Optional[int] = None,
        namespace: str = "default",
    ) -> None:
        self.default_ttl_seconds = default_ttl_seconds
        self.max_entries = max_entries
        self.namespace = namespace

        self._store: Dict[str, _CacheEntry] = {}
        self._lock = threading.RLock()

        logger.info(
            "CacheManager initialized | namespace=%s | ttl=%s | max_entries=%s",
            namespace,
            default_ttl_seconds,
            max_entries,
        )

    # -----------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from cache.
        """
        namespaced_key = self._key(key)

        with self._lock:
            entry = self._store.get(namespaced_key)

            if not entry:
                logger.debug("Cache miss | key=%s", namespaced_key)
                return None

            if entry.is_expired():
                logger.debug("Cache expired | key=%s", namespaced_key)
                self._store.pop(namespaced_key, None)
                return None

            logger.debug("Cache hit | key=%s", namespaced_key)
            return entry.value

    def set(
        self,
        key: str,
        value: Any,
        *,
        ttl_seconds: Optional[int] = None,
    ) -> None:
        """
        Store a value in cache.
        """
        namespaced_key = self._key(key)
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl_seconds

        with self._lock:
            if self.max_entries and len(self._store) >= self.max_entries:
                self._evict_one()

            self._store[namespaced_key] = _CacheEntry(value, ttl)

            logger.debug(
                "Cache set | key=%s | ttl=%s",
                namespaced_key,
                ttl,
            )

    def delete(self, key: str) -> None:
        """
        Remove a value from cache.
        """
        namespaced_key = self._key(key)

        with self._lock:
            removed = self._store.pop(namespaced_key, None)
            if removed:
                logger.debug("Cache delete | key=%s", namespaced_key)

    def clear(self) -> None:
        """
        Clear entire cache namespace.
        """
        with self._lock:
            self._store.clear()
            logger.info("Cache cleared | namespace=%s", self.namespace)

    def stats(self) -> Dict[str, Any]:
        """
        Cache statistics.
        """
        with self._lock:
            expired = sum(
                1 for e in self._store.values() if e.is_expired()
            )

            return {
                "namespace": self.namespace,
                "entries": len(self._store),
                "expired_entries": expired,
                "max_entries": self.max_entries,
                "default_ttl_seconds": self.default_ttl_seconds,
            }

    # -----------------------------------------------------------------
    # Internal Helpers
    # -----------------------------------------------------------------

    def _key(self, key: str) -> str:
        return f"{self.namespace}:{key}"

    def _evict_one(self) -> None:
        """
        Evict one entry (oldest-expiring-first).
        """
        if not self._store:
            return

        # Prefer expired entries
        for k, entry in list(self._store.items()):
            if entry.is_expired():
                self._store.pop(k, None)
                logger.debug("Cache evicted expired | key=%s", k)
                return

        # Otherwise evict earliest expiry or arbitrary
        evict_key = min(
            self._store.items(),
            key=lambda item: item[1].expires_at or float("inf"),
        )[0]

        self._store.pop(evict_key, None)
        logger.debug("Cache evicted | key=%s", evict_key)
