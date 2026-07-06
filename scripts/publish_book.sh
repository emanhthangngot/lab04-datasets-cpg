#!/usr/bin/env bash
set -euo pipefail

# Build the Jupyter Book locally before merging final evidence to main.
# GitHub Pages publication is handled by .github/workflows/publish-book.yml
# on push to main when book/notebooks/screenshots change.

if ! command -v jupyter-book >/dev/null 2>&1; then
  echo "jupyter-book is not installed. Install dependencies first:"
  echo "  pip install -r requirements.txt"
  exit 1
fi

echo "Building Jupyter Book..."
jupyter-book build book/

echo
echo "Local build complete: book/_build/html/index.html"
echo "Final publication happens automatically after merging to main and pushing."
