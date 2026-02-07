#!/bin/bash
set -e

echo "======================================="
echo " Vidhi Document Ingestion Pipeline"
echo "======================================="

if [ -f ".env" ]; then
  echo "Loading environment variables from .env"
  export $(grep -v '^#' .env | xargs)
fi

source .venv/bin/activate

python -m src.ingestion.ingest_documents \
  --input_dir data/raw \
  --output_dir data/processed
