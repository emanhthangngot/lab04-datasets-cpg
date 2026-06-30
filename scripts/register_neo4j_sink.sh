#!/usr/bin/env bash
set -euo pipefail

# Idempotently register or update the Neo4j sink connector.
# Important: use PUT /connectors/{name}/config, not POST /connectors, so the
# script works after changing Cypher or connector settings.

CONNECT_URL="${CONNECT_URL:-http://localhost:8083}"
CONNECTOR_NAME="${CONNECTOR_NAME:-cpg-neo4j-sink}"
CONFIG_FILE="${CONFIG_FILE:-neo4j/sink_connector.json}"

python3 - <<'PY' "$CONFIG_FILE" >/tmp/lab04-connector-config.json
import json
import sys
from pathlib import Path

raw = json.loads(Path(sys.argv[1]).read_text())
config = raw.get("config", raw)
print(json.dumps(config))
PY

curl -fsS -X PUT \
  -H "Content-Type: application/json" \
  --data @/tmp/lab04-connector-config.json \
  "$CONNECT_URL/connectors/$CONNECTOR_NAME/config" \
  | python3 -m json.tool

echo "Connector registered or updated: $CONNECTOR_NAME"
