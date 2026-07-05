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

if [[ -x ".venv/Scripts/python.exe" ]]; then
  PYTHON=".venv/Scripts/python.exe"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON="python3"
else
  PYTHON="python"
fi

echo "==> Python tests"
"$PYTHON" -m pytest

echo
echo "==> Docker Compose syntax"
docker compose config >/dev/null

echo
echo "==> JSON connector config"
"$PYTHON" -m json.tool neo4j/sink_connector.json >/dev/null

echo
echo "Scaffold checks passed."
