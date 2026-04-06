from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class AppConfig:
    port: int
    model: str
    openrouter_api_key: Optional[str]
    openrouter_site_url: str
    openrouter_app_name: str
    openrouter_chat_url: str
    openrouter_max_tokens: int
    llm_max_retries: int
    llm_retry_backoff_ms: int
    llm_fallback_enabled: bool
    rate_limit_enabled: bool
    rate_limit_window_s: int
    rate_limit_max_requests: int
    rate_limit_bypass_paths: set[str]
    response_cache_ttl_s: int
    response_cache_max_entries: int
    response_stale_ttl_s: int
    prewarm_queries: list[str]
    prewarm_enabled: bool
    prewarm_provision_enabled: bool
    provision_url_warm_limit: int


def _to_bool(value: Any, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _to_int(value: Any, default: int) -> int:
    try:
        if value is None or value == "":
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def _load_file_config(root_dir: Path) -> Dict[str, Any]:
    config_path = os.getenv("VIDHI_CONFIG_FILE", "").strip()
    if not config_path:
        return {}

    path = Path(config_path)
    if not path.is_absolute():
        path = root_dir / config_path

    if not path.exists() or not path.is_file():
        return {}

    if path.suffix.lower() == ".json":
        return json.loads(path.read_text(encoding="utf-8"))

    if path.suffix.lower() in {".yml", ".yaml"}:
        try:
            import yaml  # type: ignore
        except Exception:
            return {}
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        return loaded if isinstance(loaded, dict) else {}

    return {}


def _get(source: Dict[str, Any], key: str, env_key: str, default: Any = None) -> Any:
    env_value = os.getenv(env_key)
    if env_value is not None:
        return env_value
    if key in source:
        return source[key]
    return default


def load_app_config(root_dir: Path) -> AppConfig:
    source = _load_file_config(root_dir)

    prewarm_queries_raw = _get(
        source,
        "prewarm_queries",
        "VIDHI_PREWARM_QUERIES",
        "bail,anticipatory bail,section 420,cheque bounce",
    )
    if isinstance(prewarm_queries_raw, list):
        prewarm_queries = [str(q).strip() for q in prewarm_queries_raw if str(q).strip()]
    else:
        prewarm_queries = [q.strip() for q in str(prewarm_queries_raw).split(",") if q.strip()]

    bypass_paths_raw = _get(source, "rate_limit_bypass_paths", "VIDHI_RATE_LIMIT_BYPASS_PATHS", "/api/v1/health")
    if isinstance(bypass_paths_raw, list):
        bypass_paths = {str(p).strip() for p in bypass_paths_raw if str(p).strip()}
    else:
        bypass_paths = {p.strip() for p in str(bypass_paths_raw).split(",") if p.strip()}

    return AppConfig(
        port=_to_int(_get(source, "port", "PORT", 8000), 8000),
        model=str(_get(source, "model", "VIDHI_LLM_MODEL", os.getenv("VIDHI_OPENAI_MODEL") or "openai/gpt-4.1-mini")),
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY") or source.get("openrouter_api_key"),
        openrouter_site_url=str(_get(source, "openrouter_site_url", "OPENROUTER_SITE_URL", "http://localhost:5173")),
        openrouter_app_name=str(_get(source, "openrouter_app_name", "OPENROUTER_APP_NAME", "Vidhi")),
        openrouter_chat_url=str(_get(source, "openrouter_chat_url", "OPENROUTER_CHAT_URL", "https://openrouter.ai/api/v1/chat/completions")),
        openrouter_max_tokens=max(1, _to_int(_get(source, "openrouter_max_tokens", "OPENROUTER_MAX_TOKENS", 1800), 1800)),
        llm_max_retries=max(0, _to_int(_get(source, "llm_max_retries", "VIDHI_LLM_MAX_RETRIES", 2), 2)),
        llm_retry_backoff_ms=max(50, _to_int(_get(source, "llm_retry_backoff_ms", "VIDHI_LLM_RETRY_BACKOFF_MS", 300), 300)),
        llm_fallback_enabled=_to_bool(_get(source, "llm_fallback_enabled", "VIDHI_LLM_FALLBACK_ENABLED", True), True),
        rate_limit_enabled=_to_bool(_get(source, "rate_limit_enabled", "VIDHI_RATE_LIMIT_ENABLED", True), True),
        rate_limit_window_s=max(1, _to_int(_get(source, "rate_limit_window_s", "VIDHI_RATE_LIMIT_WINDOW_S", 60), 60)),
        rate_limit_max_requests=max(1, _to_int(_get(source, "rate_limit_max_requests", "VIDHI_RATE_LIMIT_MAX_REQUESTS", 120), 120)),
        rate_limit_bypass_paths=bypass_paths,
        response_cache_ttl_s=max(1, _to_int(_get(source, "response_cache_ttl_s", "VIDHI_RESPONSE_CACHE_TTL_S", 300), 300)),
        response_cache_max_entries=max(32, _to_int(_get(source, "response_cache_max_entries", "VIDHI_RESPONSE_CACHE_MAX_ENTRIES", 256), 256)),
        response_stale_ttl_s=max(1, _to_int(_get(source, "response_stale_ttl_s", "VIDHI_RESPONSE_STALE_TTL_S", 900), 900)),
        prewarm_queries=prewarm_queries,
        prewarm_enabled=_to_bool(_get(source, "prewarm_enabled", "VIDHI_PREWARM_ENABLED", False), False),
        prewarm_provision_enabled=_to_bool(_get(source, "prewarm_provision_enabled", "VIDHI_PREWARM_PROVISION_ENABLED", False), False),
        provision_url_warm_limit=max(1, _to_int(_get(source, "provision_url_warm_limit", "VIDHI_PROVISION_URL_WARM_LIMIT", 4), 4)),
    )
