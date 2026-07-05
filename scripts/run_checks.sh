#!/usr/bin/env bash
set -euo pipefail

# Lightweight checks for scaffold and local Python logic.

echo "==> Codex config"
bash .codex/scripts/doctor.sh
echo

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
