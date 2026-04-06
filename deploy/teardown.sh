#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v docker >/dev/null 2>&1; then
  echo "[teardown] docker is required but not installed." >&2
  exit 1
fi

cd "$PROJECT_ROOT"

echo "[teardown] Stopping Vidhi services..."
docker compose down --remove-orphans

echo "[teardown] Services stopped."
