#!/usr/bin/env bash
set -euo pipefail

BACKEND_URL="${BACKEND_URL:-http://localhost:8000/api/v1/health}"

if ! command -v curl >/dev/null 2>&1; then
  echo "[healthcheck] curl is required but not installed." >&2
  exit 1
fi

echo "[healthcheck] Checking backend health: ${BACKEND_URL}"
http_code=$(curl -sS -o /tmp/vidhi-health.json -w "%{http_code}" "$BACKEND_URL")

if [[ "$http_code" != "200" ]]; then
  echo "[healthcheck] Unhealthy response (HTTP ${http_code})."
  cat /tmp/vidhi-health.json || true
  exit 1
fi

echo "[healthcheck] Healthy (HTTP 200)."
cat /tmp/vidhi-health.json
