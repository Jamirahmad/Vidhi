#!/bin/bash
set -e

echo "======================================="
echo " Running Vidhi Test Suite"
echo "======================================="

source .venv/bin/activate

pytest -v tests/
