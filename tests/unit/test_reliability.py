from backend.app.reliability import build_fallback_task_prompt, compute_backoff_seconds, is_retryable_status, should_retry_with_fallback


def test_is_retryable_status_for_common_transients() -> None:
    assert is_retryable_status(429)
    assert is_retryable_status(503)
    assert not is_retryable_status(400)


def test_compute_backoff_seconds_increases_per_attempt() -> None:
    first = compute_backoff_seconds(0, 300)
    second = compute_backoff_seconds(1, 300)

    assert second > first


def test_build_fallback_task_prompt_appends_fallback_instruction() -> None:
    prompt = build_fallback_task_prompt("Return legal analysis")

    assert "FALLBACK MODE" in prompt
    assert "Return legal analysis" in prompt


def test_should_retry_with_fallback_only_for_supported_errors() -> None:
    assert should_retry_with_fallback("INVALID_PROVIDER_RESPONSE")
    assert should_retry_with_fallback("INVALID_LLM_SCHEMA")
    assert not should_retry_with_fallback("SAFETY_FILTER_BLOCKED")
