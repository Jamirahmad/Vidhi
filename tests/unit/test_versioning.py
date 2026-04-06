from pathlib import Path

from backend.app.versioning import resolve_app_version


def test_resolve_app_version_from_file(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("VIDHI_APP_VERSION", raising=False)
    (tmp_path / "VERSION").write_text("1.2.3\n", encoding="utf-8")

    assert resolve_app_version(tmp_path) == "1.2.3"


def test_resolve_app_version_prefers_env(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("VIDHI_APP_VERSION", "2.0.0")
    (tmp_path / "VERSION").write_text("1.2.3\n", encoding="utf-8")

    assert resolve_app_version(tmp_path) == "2.0.0"
