#!/bin/bash
set -e

echo "======================================="
echo " Vidhi Vectorstore Build Script"
echo "======================================="

if [ -f ".env" ]; then
  echo "Loading environment variables from .env"
  export $(grep -v '^#' .env | xargs)
fi

source .venv/bin/activate

python -m src.vectorstore.build_vectorstore \
  --input_dir data/processed \
  --vectorstore_dir vectorstore
