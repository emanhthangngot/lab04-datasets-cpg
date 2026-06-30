#!/usr/bin/env bash
set -euo pipefail

# Create all required Kafka topics explicitly inside the Kafka service.
# TODO: Capture topic list output for notebook Task 3.

KAFKA_SERVICE="${KAFKA_SERVICE:-broker}"
BOOTSTRAP="${KAFKA_BOOTSTRAP_INTERNAL:-broker:9092}"

create_topic() {
  local topic="$1"
  local partitions="$2"
  docker compose exec "$KAFKA_SERVICE" kafka-topics \
    --bootstrap-server "$BOOTSTRAP" \
    --create --if-not-exists \
    --topic "$topic" \
    --partitions "$partitions" \
    --replication-factor 1 \
    --config retention.ms=86400000
}

create_topic cpg.nodes 4
create_topic cpg.edges 4
create_topic cpg.metadata 1
create_topic cpg.errors 1

echo "Kafka topics:"
docker compose exec "$KAFKA_SERVICE" kafka-topics --bootstrap-server "$BOOTSTRAP" --list
