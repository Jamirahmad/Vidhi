# Configuration Management

Item 22 introduces a **config-driven runtime layer** for backend behavior.

## Priority order

Configuration is resolved in this order (highest first):

1. Environment variables (`.env` / deployment env)
2. Optional config file referenced by `VIDHI_CONFIG_FILE`
3. Safe defaults in `backend/app/config.py`

## Supported config file formats

- JSON (`.json`) — always supported
- YAML (`.yml`, `.yaml`) — supported when `PyYAML` is installed

Example:

```bash
export VIDHI_CONFIG_FILE=backend/config/runtime.json
```

Starter template: `backend/config/runtime.example.json`.

## Key settings

- `port` (`PORT`)
- `model` (`VIDHI_LLM_MODEL`, fallback `VIDHI_OPENAI_MODEL`)
- `openrouter_*` provider settings
- LLM reliability settings (`llm_max_retries`, `llm_retry_backoff_ms`, `llm_fallback_enabled`)
- rate limiting controls (`rate_limit_*`)
- cache settings (`response_cache_*`)
- embedding cache settings (`VIDHI_EMBED_CACHE_MAX_ENTRIES`)
- prewarm settings (`prewarm_*`)
- `provision_url_warm_limit`

## Recommended usage

- Keep secrets in environment variables only (`OPENROUTER_API_KEY`, etc.).
- Use config files for non-secret, environment-specific knobs (rate limits, cache, prewarm queries).
- Keep production/staging/development config files separate and version-controlled where safe.
