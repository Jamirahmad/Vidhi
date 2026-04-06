import json
from pathlib import Path

from backend.app.config import load_app_config


def test_load_app_config_from_json_file(tmp_path: Path, monkeypatch) -> None:
    config_path = tmp_path / "vidhi-config.json"
    config_path.write_text(
        json.dumps(
            {
                "port": 9100,
                "model": "openai/gpt-4.1",
                "rate_limit_enabled": False,
                "rate_limit_bypass_paths": ["/api/v1/health", "/api/v1/metrics"],
                "prewarm_queries": ["bail", "ipc 420"],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("VIDHI_CONFIG_FILE", str(config_path))
    monkeypatch.delenv("PORT", raising=False)
    monkeypatch.delenv("VIDHI_LLM_MODEL", raising=False)

    config = load_app_config(tmp_path)

    assert config.port == 9100
    assert config.model == "openai/gpt-4.1"
    assert config.rate_limit_enabled is False
    assert "/api/v1/metrics" in config.rate_limit_bypass_paths
    assert config.prewarm_queries == ["bail", "ipc 420"]


def test_env_overrides_file_values(tmp_path: Path, monkeypatch) -> None:
    config_path = tmp_path / "vidhi-config.json"
    config_path.write_text(json.dumps({"port": 9100}), encoding="utf-8")

    monkeypatch.setenv("VIDHI_CONFIG_FILE", str(config_path))
    monkeypatch.setenv("PORT", "9200")

    config = load_app_config(tmp_path)

    assert config.port == 9200
