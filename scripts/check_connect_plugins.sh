#!/usr/bin/env bash
set -euo pipefail

# Verify that the Neo4j Kafka Connector is installed in Kafka Connect.
# TODO: If no Neo4j class is printed, rebuild `connect` from kafka-connect/Dockerfile.

CONNECT_URL="${CONNECT_URL:-http://localhost:8083}"

echo "Available Kafka Connect plugins:"
curl -fsS "$CONNECT_URL/connector-plugins" | python3 -m json.tool

echo
echo "Neo4j connector classes:"
curl -fsS "$CONNECT_URL/connector-plugins" | python3 -m json.tool | grep -i neo4j || true
