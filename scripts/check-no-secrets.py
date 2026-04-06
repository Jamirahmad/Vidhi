#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXCLUDED_DIRS = {
    ".git",
    "node_modules",
    ".pytest_cache",
    "__pycache__",
    "dist",
    "build",
}
EXCLUDED_FILES = {
    ".env.example",
    "package-lock.json",
    "frontend/package-lock.json",
}

PATTERNS = [
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*[\"']?[A-Za-z0-9_\-]{16,}[\"']?"),
]


def iter_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if any(part in EXCLUDED_DIRS for part in rel.parts):
            continue
        if str(rel) in EXCLUDED_FILES:
            continue
        files.append(path)
    return files


def main() -> int:
    violations: list[str] = []

    for file_path in iter_files():
        rel = file_path.relative_to(ROOT)
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        for idx, line in enumerate(content.splitlines(), start=1):
            for pattern in PATTERNS:
                if pattern.search(line):
                    violations.append(f"{rel}:{idx}: potential secret detected")
                    break

    if violations:
        print("Secret scan failed. Potential secrets found:")
        for violation in violations:
            print(f" - {violation}")
        return 1

    print("Secret scan passed: no hardcoded secrets detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
