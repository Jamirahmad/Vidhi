#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_PATH="${1:-${ROOT_DIR}/vidhi-clean-$(date +%Y%m%d-%H%M%S).zip}"

if ! command -v git >/dev/null 2>&1; then
  echo "[export-clean-repo] git is required but not installed." >&2
  exit 1
fi

cd "$ROOT_DIR"

echo "[export-clean-repo] Creating clean archive at: ${OUTPUT_PATH}"
git archive --format=zip --output "$OUTPUT_PATH" HEAD

echo "[export-clean-repo] Done. Archive excludes .git metadata by design."
