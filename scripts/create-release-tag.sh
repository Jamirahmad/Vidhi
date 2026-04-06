#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

VERSION="$(cat VERSION | tr -d '[:space:]')"
TAG="v${VERSION}"

python scripts/validate-versioning.py

git diff --quiet || {
  echo "Working tree has uncommitted changes. Commit before tagging." >&2
  exit 1
}

git rev-parse "$TAG" >/dev/null 2>&1 && {
  echo "Tag $TAG already exists" >&2
  exit 1
}

git tag -a "$TAG" -m "Release $TAG"
echo "Created local tag: $TAG"
echo "Push with: git push origin $TAG"
