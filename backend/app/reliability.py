from __future__ import annotations

from typing import Optional


RETRYABLE_STATUS_CODES = {408, 409, 425, 429, 500, 502, 503, 504}
FALLBACK_RETRYABLE_ERROR_CODES = {"INVALID_PROVIDER_RESPONSE", "INVALID_LLM_SCHEMA"}


def is_retryable_status(status_code: int) -> bool:
    return status_code in RETRYABLE_STATUS_CODES


def compute_backoff_seconds(attempt_index: int, base_delay_ms: int) -> float:
    # attempt_index is 0-based
    multiplier = 2 ** max(0, attempt_index)
    delay_ms = max(50, base_delay_ms) * multiplier
    return min(delay_ms / 1000.0, 5.0)


def build_fallback_task_prompt(task_prompt: str) -> str:
    return (
        f"{task_prompt}\n\n"
        "FALLBACK MODE: Return strictly valid JSON only. "
        "Do not include explanations, markdown, or additional text. "
        "If uncertain, return the minimum valid JSON shape for this task."
    )


def should_retry_with_fallback(error_code: Optional[str]) -> bool:
    return bool(error_code and error_code in FALLBACK_RETRYABLE_ERROR_CODES)
