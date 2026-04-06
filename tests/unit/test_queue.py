import asyncio

from backend.app.queue import InMemoryTaskQueue


async def _noop() -> None:
    return None


async def _fail() -> None:
    raise RuntimeError("boom")


def test_in_memory_queue_tracks_completed_and_failed_jobs() -> None:
    queue = InMemoryTaskQueue()

    async def run() -> None:
        queue.submit("ok", _noop)
        queue.submit("fail", _fail)
        await asyncio.sleep(0.05)

    asyncio.run(run())

    snapshot = queue.snapshot()
    assert snapshot["submitted"] == 2
    assert snapshot["active"] == 0
    assert snapshot["completed"] == 1
    assert snapshot["failed"] == 1
