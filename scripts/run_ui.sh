#!/bin/bash
set -e

echo "======================================="
echo " Starting Vidhi Streamlit UI"
echo "======================================="

if [ -f ".env" ]; then
  echo "Loading environment variables from .env"
  export $(grep -v '^#' .env | xargs)
fi

source .venv/bin/activate

streamlit run src/ui/app.py --server.port 8501
