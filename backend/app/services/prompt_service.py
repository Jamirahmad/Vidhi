from __future__ import annotations

from backend.app.prompts.builder import build_system_prompt
from backend.app.prompts.registry import has_task_prompt, read_task_prompt


def resolve_system_prompt() -> str:
    return build_system_prompt()


def resolve_task_prompt(task_or_prompt: str) -> str:
    text = (task_or_prompt or "").strip()
    if not text:
        return ""
    if has_task_prompt(text):
        return read_task_prompt(text)  # type: ignore[arg-type]
    return text
