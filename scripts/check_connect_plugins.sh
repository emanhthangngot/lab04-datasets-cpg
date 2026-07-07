#!/usr/bin/env bash
set -euo pipefail

# Verify that the Neo4j Kafka Connector is installed in Kafka Connect.
# TODO: If no Neo4j class is printed, rebuild `connect` from kafka-connect/Dockerfile.

CONNECT_URL="${CONNECT_URL:-http://localhost:8083}"
EXPECTED_NEO4J_CLASS="${EXPECTED_NEO4J_CLASS:-org.neo4j.connectors.kafka.sink.Neo4jConnector}"

if [[ -x ".venv/Scripts/python.exe" ]]; then
  PYTHON=".venv/Scripts/python.exe"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON="python3"
else
  PYTHON="python"
fi

echo "Available Kafka Connect plugins:"
PLUGINS_JSON="$(curl -fsS "$CONNECT_URL/connector-plugins")"
printf '%s\n' "$PLUGINS_JSON" | "$PYTHON" -m json.tool

echo
echo "Neo4j connector classes:"
printf '%s\n' "$PLUGINS_JSON" | "$PYTHON" -m json.tool | grep -i neo4j

"$PYTHON" -c '
import json
import sys

expected = sys.argv[2]
plugins = json.loads(sys.argv[1])
matches = [
    plugin for plugin in plugins
    if plugin.get("type") == "sink" and "neo4j" in plugin.get("class", "").lower()
]
if not matches:
    print("Missing required Neo4j sink connector class from /connector-plugins", file=sys.stderr)
    sys.exit(1)
selected = next((plugin for plugin in matches if plugin.get("class") == expected), matches[0])
klass = selected.get("class")
version = selected.get("version", "unknown")
print(f"Verified Neo4j sink connector class: {klass} ({version})")
' "$PLUGINS_JSON" "$EXPECTED_NEO4J_CLASS"
