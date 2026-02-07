#!/bin/bash
set -e

echo "======================================="
echo " Running Vidhi Evaluation Pipeline"
echo "======================================="

if [ -f ".env" ]; then
  echo "Loading environment variables from .env"
  export $(grep -v '^#' .env | xargs)
fi

source .venv/bin/activate

python -m src.evaluation.run_evaluation \
  --test_cases tests/test_cases.json \
  --output_dir outputs/evaluation_results
