#!/usr/bin/env bash
set -euo pipefail

# Demonstrate idempotent replay for one modified Python file.
# TODO: Complete this script after parser emits real events and Neo4j/MongoDB
# verification commands are finalized.

TARGET_FILE="${TARGET_FILE:-data/datasets/src/datasets/config.py}"
MARKER='LAB04_REPLAY_MARKER = "replay_v2"'

if [ ! -f "$TARGET_FILE" ]; then
  echo "Replay target missing: $TARGET_FILE" >&2
  echo "Run scripts/clone_repo.sh first or set TARGET_FILE." >&2
  exit 1
fi

echo "TODO replay workflow:"
echo "1. Record current content_hash/run_id and Neo4j/MongoDB counts."
echo "2. Append marker if absent: $MARKER"
echo "3. Run parser for only $TARGET_FILE inside docker compose parser service."
echo "4. Wait for connector idle."
echo "5. Run neo4j/cleanup_stale.cypher with file_id and run_id."
echo "6. Capture duplicate checks for notebook 06."

if ! grep -q 'LAB04_REPLAY_MARKER' "$TARGET_FILE"; then
  printf '\n%s\n' "$MARKER" >> "$TARGET_FILE"
  echo "Marker appended to $TARGET_FILE"
else
  echo "Marker already present in $TARGET_FILE"
fi

docker compose run --rm parser python -m parser_service.main --repo data/datasets --mode file --file "$TARGET_FILE"
bash scripts/wait_neo4j_connector_idle.sh
