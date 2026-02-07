#!/bin/bash
set -e

echo "======================================="
echo " Exporting Vidhi Results Bundle"
echo "======================================="

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
EXPORT_DIR="exports"
EXPORT_FILE="$EXPORT_DIR/vidhi_results_$TIMESTAMP.tar.gz"

mkdir -p $EXPORT_DIR

echo "Creating export package: $EXPORT_FILE"

tar -czf $EXPORT_FILE \
  outputs/ \
  logs/ \
  docs/ \
  CHANGELOG.md \
  README.md

echo "======================================="
echo " Export complete!"
echo "File created: $EXPORT_FILE"
echo "======================================="
