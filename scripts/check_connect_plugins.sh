#!/usr/bin/env bash
set -euo pipefail

# Verify that the Neo4j Kafka Connector is installed in Kafka Connect.
# TODO: If no Neo4j class is printed, rebuild `connect` from kafka-connect/Dockerfile.

CONNECT_URL="${CONNECT_URL:-http://localhost:8083}"

echo "Available Kafka Connect plugins:"
PLUGINS_JSON="$(curl -fsS "$CONNECT_URL/connector-plugins")"
printf '%s\n' "$PLUGINS_JSON" | python3 -m json.tool

echo
echo "Neo4j connector classes:"
printf '%s\n' "$PLUGINS_JSON" | python3 -m json.tool | grep -i neo4j

python3 -c '
import json
import sys

expected = "org.neo4j.connectors.kafka.sink.Neo4jConnector"
plugins = json.loads(sys.argv[1])
matches = [
    plugin for plugin in plugins
    if plugin.get("class") == expected and plugin.get("type") == "sink"
]
if not matches:
    print(f"Missing required Neo4j sink connector class: {expected}", file=sys.stderr)
    sys.exit(1)
version = matches[0].get("version", "unknown")
print(f"Verified Neo4j sink connector class: {expected} ({version})")
' "$PLUGINS_JSON"
