#!/usr/bin/env bash
set -euo pipefail

# Lightweight checks for scaffold and local Python logic.

echo "==> Codex config"
if [[ -f ".codex/scripts/doctor.sh" ]]; then
  bash .codex/scripts/doctor.sh
else
  echo "Skipping .codex doctor; agent-local files are not required in public clones."
fi
echo

PYTHON=""
for candidate in ".venv/bin/python" ".venv/Scripts/python.exe" python python3 /usr/bin/python; do
  if [[ "$candidate" == */* && ! -x "$candidate" ]]; then
    continue
  fi
  if ! command -v "$candidate" >/dev/null 2>&1 && [[ ! -x "$candidate" ]]; then
    continue
  fi
  if "$candidate" -c 'import pytest' >/dev/null 2>&1; then
    PYTHON="$candidate"
    break
  fi
done
: "${PYTHON:?Install pytest in one of the project Python environments before running checks}"

echo "==> Python tests"
"$PYTHON" -m pytest

echo
echo "==> Docker Compose syntax"
if docker compose version >/dev/null 2>&1; then
  docker compose config >/dev/null
elif command -v docker-compose >/dev/null 2>&1; then
  docker-compose config >/dev/null
else
  echo "Docker Compose is not installed" >&2
  exit 1
fi

echo
echo "==> JSON connector config"
"$PYTHON" -m json.tool neo4j/sink_connector.json >/dev/null

echo
echo "Scaffold checks passed."
