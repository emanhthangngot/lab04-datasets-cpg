#!/usr/bin/env bash
set -euo pipefail

# Idempotently register or update the Neo4j sink connector.
# Important: use PUT /connectors/{name}/config, not POST /connectors, so the
# script works after changing Cypher or connector settings.

CONNECT_URL="${CONNECT_URL:-http://localhost:8083}"
CONNECTOR_NAME="${CONNECTOR_NAME:-cpg-neo4j-sink}"
CONFIG_FILE="${CONFIG_FILE:-neo4j/sink_connector.json}"
EXPECTED_NEO4J_CLASS="${EXPECTED_NEO4J_CLASS:-org.neo4j.connectors.kafka.sink.Neo4jConnector}"
: "${NEO4J_PASSWORD:?Set NEO4J_PASSWORD before registering the Neo4j sink}"

if [[ -x ".venv/Scripts/python.exe" ]]; then
  PYTHON=".venv/Scripts/python.exe"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON="python3"
else
  PYTHON="python"
fi

PLUGINS_JSON="$(curl -fsS "$CONNECT_URL/connector-plugins")"

"$PYTHON" - <<'PY' "$CONFIG_FILE" "$PLUGINS_JSON" "$EXPECTED_NEO4J_CLASS" >/tmp/lab04-connector-config.json
import json
import os
import sys
from pathlib import Path

raw = json.loads(Path(sys.argv[1]).read_text())
plugins = json.loads(sys.argv[2])
expected = sys.argv[3]
neo4j_password = os.environ["NEO4J_PASSWORD"]

matches = [
    plugin for plugin in plugins
    if plugin.get("type") == "sink" and "neo4j" in plugin.get("class", "").lower()
]
if not matches:
    raise SystemExit("Missing Neo4j sink connector class from /connector-plugins")

selected = next((plugin for plugin in matches if plugin.get("class") == expected), matches[0])
config = raw.get("config", raw)
config["connector.class"] = selected["class"]
config["neo4j.authentication.basic.password"] = neo4j_password
print(json.dumps(config))
PY

curl -fsS -X PUT \
  -H "Content-Type: application/json" \
  --data @/tmp/lab04-connector-config.json \
  "$CONNECT_URL/connectors/$CONNECTOR_NAME/config" \
  | "$PYTHON" -m json.tool

echo "Connector registered or updated: $CONNECTOR_NAME"
