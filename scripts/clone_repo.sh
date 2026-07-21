#!/usr/bin/env bash
set -euo pipefail

# Clone the selected public repository for Lab04 evidence.
# The caller records the printed commit SHA in the Task 1 evidence chapter.

REPO_URL="${REPO_URL:-https://github.com/huggingface/datasets.git}"
REPO_DIR="${REPO_DIR:-data/datasets}"

mkdir -p "$(dirname "$REPO_DIR")"

if [ ! -d "$REPO_DIR/.git" ]; then
  git clone --depth 1 "$REPO_URL" "$REPO_DIR"
else
  echo "Repository already cloned: $REPO_DIR"
fi

cd "$REPO_DIR"
echo "Commit SHA:"
git rev-parse HEAD
