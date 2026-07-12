#!/usr/bin/env bash
set -euo pipefail

# Capture connector registration evidence for Stage 2.
# Owner: 23120180 - Tran Le Trung Truc
# Spec: openspec/specs/kafka-spark/spec.md - "Kafka Connect Plugin Gate"
#       and "Connector Registration Uses Live Plugin Discovery"
#
# Usage:
#   bash scripts/capture_connector_evidence.sh
#
# Output files are saved under screenshots/kafka/ for Jupyter Book evidence.

CONNECT_URL="${CONNECT_URL:-http://localhost:8083}"
CONNECTOR_NAME="${CONNECTOR_NAME:-cpg-neo4j-sink}"
EVIDENCE_DIR="screenshots/kafka"

if [[ -x ".venv/Scripts/python.exe" ]]; then
  PYTHON=".venv/Scripts/python.exe"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON="python3"
else
  PYTHON="python"
fi

mkdir -p "$EVIDENCE_DIR"

# --------------------------------------------------------------------------
# 1. Capture connector plugin list (verifies Neo4j sink class)
# --------------------------------------------------------------------------
echo "=== Verifying Kafka Connect plugins ==="
PLUGINS_JSON="$(curl -fsS "$CONNECT_URL/connector-plugins")"
printf '%s\n' "$PLUGINS_JSON" | "$PYTHON" -m json.tool \
  | tee "$EVIDENCE_DIR/connector_plugins.json"

echo ""
echo "--- Neo4j connector classes ---"
printf '%s\n' "$PLUGINS_JSON" | "$PYTHON" -m json.tool | grep -i neo4j \
  | tee "$EVIDENCE_DIR/neo4j_connector_classes.txt"

"$PYTHON" -c "
import json, sys
plugins = json.loads(sys.argv[1])
matches = [p for p in plugins if p.get('type') == 'sink' and 'neo4j' in p.get('class', '').lower()]
if not matches:
    print('ERROR: No Neo4j sink connector found!', file=sys.stderr)
    sys.exit(1)
for m in matches:
    print('  Class: ' + m.get('class', '') + '  Version: ' + m.get('version', 'unknown'))
" "$PLUGINS_JSON" | tee "$EVIDENCE_DIR/neo4j_sink_class.txt"

# --------------------------------------------------------------------------
# 2. Register or update the connector
# --------------------------------------------------------------------------
echo ""
echo "=== Registering Neo4j sink connector ==="
bash scripts/register_neo4j_sink.sh 2>&1 \
  | tee "$EVIDENCE_DIR/connector_registration.txt"

# Extract only the JSON response from registration output.
# register_neo4j_sink.sh prints formatted JSON followed by a log line;
# keep only the valid JSON portion for machine-readable evidence.
"$PYTHON" -c "
import json, sys
lines = open(sys.argv[1]).read()
# Find the last complete JSON object in the output
depth = 0
start = None
end = None
for i, ch in enumerate(lines):
    if ch == '{':
        if depth == 0:
            start = i
        depth += 1
    elif ch == '}':
        depth -= 1
        if depth == 0:
            end = i + 1
if start is not None and end is not None:
    obj = json.loads(lines[start:end])
    print(json.dumps(obj, indent=4))
" "$EVIDENCE_DIR/connector_registration.txt" \
  > "$EVIDENCE_DIR/connector_registration.json"

# --------------------------------------------------------------------------
# 3. Verify connector status
# --------------------------------------------------------------------------
echo ""
echo "=== Connector status ==="
sleep 5
curl -fsS "$CONNECT_URL/connectors/$CONNECTOR_NAME/status" \
  | "$PYTHON" -m json.tool \
  | tee "$EVIDENCE_DIR/connector_status.json"

# --------------------------------------------------------------------------
# 4. Sanitize credentials from evidence artifacts
# --------------------------------------------------------------------------
echo ""
echo "=== Sanitizing credentials from evidence ==="
for f in "$EVIDENCE_DIR"/*.json "$EVIDENCE_DIR"/*.txt; do
  [ -f "$f" ] || continue
  sed -i \
    -e 's/"neo4j\.authentication\.basic\.password"[[:space:]]*:[[:space:]]*"[^"]*"/"neo4j.authentication.basic.password": "***REDACTED***"/g' \
    -e 's/"neo4j\.authentication\.basic\.username"[[:space:]]*:[[:space:]]*"[^"]*"/"neo4j.authentication.basic.username": "***REDACTED***"/g' \
    "$f"
done
echo "Credential sanitization complete."

# --------------------------------------------------------------------------
# 5. Summary
# --------------------------------------------------------------------------
echo ""
echo "=== Connector evidence capture complete ==="
echo "Evidence files saved to $EVIDENCE_DIR/:"
ls -1 "$EVIDENCE_DIR/"connector_* "$EVIDENCE_DIR/"neo4j_*
