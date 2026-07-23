#!/usr/bin/env bash
set -euo pipefail

# Clone the selected public repository for Lab04 evidence.
# The caller records the printed commit SHA in the Task 1 evidence chapter.

REPO_URL="${REPO_URL:-https://github.com/huggingface/datasets.git}"
REPO_DIR="${REPO_DIR:-data/datasets}"
DATASET_COMMIT="${DATASET_COMMIT:-41adfd0f9ee9ba3a6b4f719d5b551c5b19ae45e2}"

mkdir -p "$(dirname "$REPO_DIR")"

if [ ! -d "$REPO_DIR/.git" ]; then
  git clone --depth 1 "$REPO_URL" "$REPO_DIR"
else
  echo "Repository already cloned: $REPO_DIR"
fi

cd "$REPO_DIR"
CURRENT_COMMIT="$(git rev-parse HEAD)"
if [ -n "$DATASET_COMMIT" ] && [ "$CURRENT_COMMIT" != "$DATASET_COMMIT" ]; then
  git fetch --depth 1 origin "$DATASET_COMMIT"
  git checkout --detach FETCH_HEAD
fi
echo "Commit SHA:"
git rev-parse HEAD
