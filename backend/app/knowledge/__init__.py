try:
    from .service import KnowledgeService
except Exception:  # pragma: no cover - optional runtime dependency/runtime version mismatch
    KnowledgeService = None  # type: ignore[assignment]

__all__ = ["KnowledgeService"]
