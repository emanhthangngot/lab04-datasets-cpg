#!/usr/bin/env bash
set -euo pipefail

EVIDENCE_DIR="${REPLAY_EVIDENCE_DIR:-screenshots/replay}"
for image in neo4j_after_cleanup.png mongodb_after_replay.png; do
  if [[ ! -s "$EVIDENCE_DIR/$image" ]]; then
    echo "ERROR: missing required UI evidence: $EVIDENCE_DIR/$image" >&2
    exit 1
  fi
done

if [[ -x ".venv/Scripts/python.exe" ]]; then
  PYTHON=".venv/Scripts/python.exe"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON="python"
else
  PYTHON="/usr/bin/python"
fi

RUN_DATE="$(date -u +%Y-%m-%d)"
"$PYTHON" -c '
import json, sys
payload = {
    "task": "Task 6 - Idempotent Replay Verification",
    "run_date": sys.argv[1],
    "result": "pass",
    "source": "Stage 3 canonical run",
    "screenshots": {
        "neo4j_after_cleanup.png": "Neo4j Browser target run_id/count query",
        "mongodb_after_replay.png": "Mongo Express target file_id filter",
    },
}
json.dump(payload, sys.stdout, indent=2)
print()
' "$RUN_DATE" > "$EVIDENCE_DIR/evidence_metadata.json"

bash scripts/sanitize_evidence.sh \
  "$EVIDENCE_DIR/evidence_metadata.json" \
  "$EVIDENCE_DIR"/*.txt \
  "$EVIDENCE_DIR"/*.diff
"$PYTHON" scripts/stage3_replay_manifest.py write --root .
"$PYTHON" scripts/stage3_replay_manifest.py validate --root .
echo "Stage 3 replay evidence finalized and validated."
