from __future__ import annotations

import asyncio
import time
import uuid
from threading import Lock
from typing import Any, Awaitable, Callable, Dict


class InMemoryTaskQueue:
    """Simple in-process async queue abstraction for background jobs."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._tasks: Dict[str, asyncio.Task[None]] = {}
        self._submitted = 0
        self._completed = 0
        self._failed = 0

    def submit(self, name: str, coro_factory: Callable[[], Awaitable[None]]) -> str:
        job_id = f"{name}:{uuid.uuid4().hex[:12]}"

        async def _runner() -> None:
            try:
                await coro_factory()
                with self._lock:
                    self._completed += 1
            except Exception:
                with self._lock:
                    self._failed += 1
            finally:
                with self._lock:
                    self._tasks.pop(job_id, None)

        with self._lock:
            self._submitted += 1
            task = asyncio.create_task(_runner())
            self._tasks[job_id] = task

        return job_id

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "submitted": self._submitted,
                "active": len(self._tasks),
                "completed": self._completed,
                "failed": self._failed,
            }
