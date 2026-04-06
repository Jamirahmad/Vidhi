from __future__ import annotations

import os
from pathlib import Path

DEFAULT_APP_VERSION = "0.1.0"


def resolve_app_version(root_dir: Path) -> str:
    """Resolve application version from env override or repository VERSION file."""
    env_version = os.getenv("VIDHI_APP_VERSION", "").strip()
    if env_version:
        return env_version

    version_file = root_dir / "VERSION"
    if version_file.exists():
        file_version = version_file.read_text(encoding="utf-8").strip()
        if file_version:
            return file_version

    return DEFAULT_APP_VERSION
