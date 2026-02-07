#!/bin/bash
set -e

echo "======================================="
echo " Starting Vidhi Full Stack (API + UI)"
echo "======================================="

if [ -f ".env" ]; then
  echo "Loading environment variables from .env"
  export $(grep -v '^#' .env | xargs)
fi

source .venv/bin/activate

echo "Starting FastAPI in background..."
nohup uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload > logs/api.log 2>&1 &

sleep 3

echo "Starting Streamlit UI..."
streamlit run src/ui/app.py --server.port 8501
