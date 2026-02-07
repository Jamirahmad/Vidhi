#!/bin/bash
set -e

echo "======================================="
echo " Starting Vidhi FastAPI Server"
echo "======================================="

if [ -f ".env" ]; then
  echo "Loading environment variables from .env"
  export $(grep -v '^#' .env | xargs)
fi

source .venv/bin/activate

uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
