#!/usr/bin/env bash
set -euo pipefail

# Wait until the Kafka Connect consumer group has no lag.
# TODO: Run this before stale cleanup in replay verification.

KAFKA_SERVICE="${KAFKA_SERVICE:-broker}"
BOOTSTRAP="${KAFKA_BOOTSTRAP_INTERNAL:-broker:9092}"
CONNECTOR_NAME="${CONNECTOR_NAME:-cpg-neo4j-sink}"
GROUP="connect-${CONNECTOR_NAME}"
STORE_WAIT_SECONDS="${NEO4J_STORE_WAIT_SECONDS:-300}"
EXPECTED_REPO_NAME="${EXPECTED_REPO_NAME:-huggingface/datasets}"
EXPECTED_COMMIT_SHA="${EXPECTED_COMMIT_SHA:-}"
REQUIRE_UNIQUE_EVENT_IDS="${REQUIRE_UNIQUE_EVENT_IDS:-true}"
: "${NEO4J_PASSWORD:?Set NEO4J_PASSWORD before waiting for Neo4j persistence}"

if [[ -x ".venv/Scripts/python.exe" ]]; then
  PYTHON=".venv/Scripts/python.exe"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON="python3"
else
  PYTHON="python"
fi

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

# A zero committed-offset lag can briefly precede completion of an in-flight
# Neo4j transaction. Count unique emitted IDs from Kafka and wait for those
# exact persisted totals rather than capturing a partial graph.
topic_event_count() {
  local topic="$1"
  docker compose exec -T "$KAFKA_SERVICE" kafka-run-class kafka.tools.GetOffsetShell \
    --broker-list "$BOOTSTRAP" --topic "$topic" --time -1 \
    | awk -F: '{sum += $3} END {print sum+0}' \
    | tr -d '\r'
}

topic_id_counts() {
  local topic="$1"
  local event_count
  event_count="$(topic_event_count "$topic")"
  if ! [[ "$event_count" =~ ^[1-9][0-9]*$ ]]; then
    echo "ERROR: $topic has no events; cannot verify persisted graph counts" >&2
    return 1
  fi

  docker compose exec -T "$KAFKA_SERVICE" kafka-console-consumer \
    --bootstrap-server "$BOOTSTRAP" \
    --topic "$topic" \
    --from-beginning \
    --max-messages "$event_count" \
    --timeout-ms 10000 2>/dev/null \
  | "$PYTHON" -c '
import json
import sys

topic = sys.argv[1]
expected_repo = sys.argv[2]
expected_commit = sys.argv[3]
event_count = 0
ids = set()
repos = set()
commit_shas = set()
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    event = json.loads(line)
    event_count += 1
    ids.add(event["id"])
    repos.add(event.get("repo"))
    commit_shas.add(event.get("commit_sha"))
if repos != {expected_repo}:
    raise SystemExit(f"ERROR: {topic} contains unexpected repo values: {sorted(repr(repo) for repo in repos)}")
if expected_commit and commit_shas != {expected_commit}:
    raise SystemExit(
        f"ERROR: {topic} contains unexpected commit_sha values: "
        f"{sorted(repr(commit_sha) for commit_sha in commit_shas)}"
    )
print(event_count, len(ids))
' "$topic" "$EXPECTED_REPO_NAME" "$EXPECTED_COMMIT_SHA"
}

read -r NODE_EVENTS EXPECTED_NODES <<< "$(topic_id_counts cpg.nodes)"
read -r EDGE_EVENTS EXPECTED_EDGES <<< "$(topic_id_counts cpg.edges)"
if ! [[ "$EXPECTED_NODES" =~ ^[1-9][0-9]*$ ]] || ! [[ "$EXPECTED_EDGES" =~ ^[1-9][0-9]*$ ]]; then
  echo "ERROR: invalid unique graph totals derived from Kafka" >&2
  exit 1
fi
if [ "$REQUIRE_UNIQUE_EVENT_IDS" = "true" ] && {
  [ "$NODE_EVENTS" != "$EXPECTED_NODES" ] || [ "$EDGE_EVENTS" != "$EXPECTED_EDGES" ];
}; then
  echo "ERROR: duplicate emitted IDs detected: nodes $NODE_EVENTS/$EXPECTED_NODES, edges $EDGE_EVENTS/$EXPECTED_EDGES" >&2
  exit 1
fi

GRAPH_COUNTS_FILE="screenshots/kafka/graph_event_counts.json"
mkdir -p "$(dirname "$GRAPH_COUNTS_FILE")"
"$PYTHON" -c '
import json
import sys

keys = ("node_events", "unique_node_ids", "edge_events", "unique_edge_ids")
values = [int(value) for value in sys.argv[1:]]
json.dump(dict(zip(keys, values)), sys.stdout, indent=2)
print()
' "$NODE_EVENTS" "$EXPECTED_NODES" "$EDGE_EVENTS" "$EXPECTED_EDGES" \
  > "$GRAPH_COUNTS_FILE"

echo "Kafka graph IDs: $NODE_EVENTS node events/$EXPECTED_NODES unique, $EDGE_EVENTS edge events/$EXPECTED_EDGES unique."
echo "Waiting for Neo4j persistence: $EXPECTED_NODES explicit nodes, $EXPECTED_EDGES edges..."
DEADLINE=$((SECONDS + STORE_WAIT_SECONDS))
while true; do
  CURRENT_NODES="$(
    docker compose exec -T neo4j cypher-shell --format plain \
      -u neo4j -p "$NEO4J_PASSWORD" \
      'MATCH (n:CPGNode) WHERE coalesce(n.placeholder, false) = false RETURN count(n);' \
      | tail -1 | tr -d '\r[:space:]'
  )"
  CURRENT_EDGES="$(
    docker compose exec -T neo4j cypher-shell --format plain \
      -u neo4j -p "$NEO4J_PASSWORD" \
      'MATCH ()-[r:CPG_EDGE]->() RETURN count(r);' \
      | tail -1 | tr -d '\r[:space:]'
  )"

  echo "Persisted graph: ${CURRENT_NODES:-unknown} explicit nodes, ${CURRENT_EDGES:-unknown} edges"
  if [ "$CURRENT_NODES" = "$EXPECTED_NODES" ] && [ "$CURRENT_EDGES" = "$EXPECTED_EDGES" ]; then
    break
  fi
  if (( SECONDS >= DEADLINE )); then
    echo "ERROR: Neo4j did not reach expected persisted counts within ${STORE_WAIT_SECONDS}s" >&2
    exit 1
  fi
  sleep 2
done

echo "Neo4j persisted graph matches unique emitted Kafka IDs."
