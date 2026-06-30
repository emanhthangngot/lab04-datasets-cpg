#!/usr/bin/env bash
set -euo pipefail

# Wait until the Kafka Connect consumer group has no lag.
# TODO: Run this before stale cleanup in replay verification.

KAFKA_SERVICE="${KAFKA_SERVICE:-broker}"
BOOTSTRAP="${KAFKA_BOOTSTRAP_INTERNAL:-broker:9092}"
CONNECTOR_NAME="${CONNECTOR_NAME:-cpg-neo4j-sink}"
GROUP="connect-${CONNECTOR_NAME}"

echo "Waiting for Neo4j connector consumer group lag to become zero..."

while true; do
  LAG=$(docker compose exec "$KAFKA_SERVICE" kafka-consumer-groups \
    --bootstrap-server "$BOOTSTRAP" \
    --describe \
    --group "$GROUP" 2>/dev/null \
    | awk 'NR>1 && $6 ~ /^[0-9]+$/ {sum += $6} END {print sum+0}')

  echo "Current lag: $LAG"
  if [ "$LAG" -eq 0 ]; then
    break
  fi
  sleep 2
done

echo "Neo4j connector appears caught up."
