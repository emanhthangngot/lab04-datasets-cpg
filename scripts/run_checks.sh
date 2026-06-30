#!/usr/bin/env bash
set -euo pipefail

# Lightweight checks for scaffold and local Python logic.

if [[ -x ".codex/scripts/doctor.sh" ]]; then
  echo "==> Codex config"
  bash .codex/scripts/doctor.sh
  echo
else
  echo "==> Codex config"
  echo "Skipping .codex doctor; agent-local files are not required in public clones."
  echo
fi

echo "==> Python tests"
python -m pytest

echo
echo "==> Docker Compose syntax"
docker compose config >/dev/null

echo
echo "==> JSON connector config"
python3 -m json.tool neo4j/sink_connector.json >/dev/null

echo
echo "Scaffold checks passed."
