#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v docker >/dev/null 2>&1; then
  echo "[deploy] docker is required but not installed." >&2
  exit 1
fi

cd "$PROJECT_ROOT"

echo "[deploy] Building and starting Vidhi services..."
docker compose up -d --build

echo "[deploy] Services started."
