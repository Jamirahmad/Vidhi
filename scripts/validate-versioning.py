#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEMVER_PATTERN = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")


def fail(message: str) -> None:
    print(f"❌ {message}")
    sys.exit(1)


version_file = ROOT / "VERSION"
if not version_file.exists():
    fail("VERSION file is missing at repository root")

version = version_file.read_text(encoding="utf-8").strip()
if not SEMVER_PATTERN.match(version):
    fail(f"VERSION must follow semantic versioning (got: {version!r})")

package_json = ROOT / "package.json"
if not package_json.exists():
    fail("package.json is missing at repository root")

package_version = json.loads(package_json.read_text(encoding="utf-8")).get("version", "").strip()
if package_version != version:
    fail(f"Version mismatch: VERSION={version!r}, package.json={package_version!r}")

print(f"✅ Versioning check passed ({version})")
