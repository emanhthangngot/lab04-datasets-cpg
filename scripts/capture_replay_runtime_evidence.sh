#!/usr/bin/env bash
set -euo pipefail

PHASE="${1:-}"
EVIDENCE_DIR="${REPLAY_EVIDENCE_DIR:-screenshots/replay}"
CHECKPOINT_PATH="/mnt/checkpoints/cpg_metadata"
EXPECTED_METADATA_OFFSET="${EXPECTED_METADATA_OFFSET:-}"
WAIT_SECONDS="${REPLAY_WAIT_SECONDS:-180}"
mkdir -p "$EVIDENCE_DIR"

case "$PHASE" in
  before|after-restart|after-replay) ;;
  *)
    echo "Usage: $0 {before|after-restart|after-replay}" >&2
    exit 2
    ;;
esac

if [[ -x ".venv/Scripts/python.exe" ]]; then
  PYTHON=".venv/Scripts/python.exe"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON="python"
else
  PYTHON="/usr/bin/python"
fi

docker_compose() {
  MSYS_NO_PATHCONV=1 docker compose "$@"
}

topic_count() {
  local topic="$1"
  docker compose exec -T broker kafka-run-class kafka.tools.GetOffsetShell \
    --broker-list broker:9092 --topic "$topic" --time -1 \
    | awk -F: '{sum += $3} END {print sum+0}' | tr -d '\r'
}

unique_ids() {
  local topic="$1"
  local count="$2"
  docker compose exec -T broker kafka-console-consumer \
    --bootstrap-server broker:9092 --topic "$topic" --from-beginning \
    --max-messages "$count" --timeout-ms 10000 2>/dev/null \
    | "$PYTHON" -c '
import json, sys
print(len({json.loads(line)["id"] for line in sys.stdin if line.strip()}))
'
}

capture_kafka() {
  local output="$1"
  local nodes edges metadata errors unique_nodes unique_edges
  nodes="$(topic_count cpg.nodes)"
  edges="$(topic_count cpg.edges)"
  metadata="$(topic_count cpg.metadata)"
  errors="$(topic_count cpg.errors)"
  unique_nodes="$(unique_ids cpg.nodes "$nodes")"
  unique_edges="$(unique_ids cpg.edges "$edges")"
  "$PYTHON" -c '
import json, sys
values = [int(value) for value in sys.argv[1:]]
keys = ("cpg.nodes", "cpg.edges", "cpg.metadata", "cpg.errors", "unique_node_ids", "unique_edge_ids")
json.dump(dict(zip(keys, values)), sys.stdout, indent=2)
print()
' "$nodes" "$edges" "$metadata" "$errors" "$unique_nodes" "$unique_edges" > "$output"
}

checkpoint_values() {
  local latest_offset latest_commit metadata_offset
  latest_offset="$(docker_compose exec -T spark sh -lc \
    "ls -1 '$CHECKPOINT_PATH/offsets' 2>/dev/null | grep -E '^[0-9]+$' | sort -n | tail -1" \
    | tr -d '\r')"
  latest_commit="$(docker_compose exec -T spark sh -lc \
    "ls -1 '$CHECKPOINT_PATH/commits' 2>/dev/null | grep -E '^[0-9]+$' | sort -n | tail -1" \
    | tr -d '\r')"
  if ! [[ "$latest_offset" =~ ^[0-9]+$ && "$latest_commit" =~ ^[0-9]+$ ]]; then
    return 1
  fi
  metadata_offset="$(docker_compose exec -T spark cat "$CHECKPOINT_PATH/offsets/$latest_offset" \
    | "$PYTHON" -c '
import json, sys
lines = [line.strip() for line in sys.stdin if line.strip()]
payload = json.loads(lines[-1])
print(sum(int(value) for value in payload.get("cpg.metadata", {}).values()))
' | tr -d '\r')"
  printf '%s %s\n' "$metadata_offset" "$latest_commit"
}

capture_checkpoint() {
  local output="$1"
  local deadline values metadata_offset completed_batch
  deadline=$((SECONDS + WAIT_SECONDS))
  while true; do
    values="$(checkpoint_values 2>/dev/null || true)"
    read -r metadata_offset completed_batch <<< "$values"
    if [[ "$metadata_offset" =~ ^[0-9]+$ && "$completed_batch" =~ ^[0-9]+$ ]]; then
      if [[ -z "$EXPECTED_METADATA_OFFSET" || "$metadata_offset" == "$EXPECTED_METADATA_OFFSET" ]]; then
        break
      fi
    fi
    if ((SECONDS >= deadline)); then
      echo "ERROR: Spark checkpoint did not reach metadata offset ${EXPECTED_METADATA_OFFSET:-any}" >&2
      exit 1
    fi
    sleep 2
  done
  "$PYTHON" -c '
import json, sys
json.dump({"metadata_offset": int(sys.argv[1]), "completed_batch": int(sys.argv[2])}, sys.stdout, indent=2)
print()
' "$metadata_offset" "$completed_batch" > "$output"
}

case "$PHASE" in
  before)
    capture_kafka "$EVIDENCE_DIR/kafka_offsets_before.json"
    capture_checkpoint "$EVIDENCE_DIR/spark_checkpoint_before.json"
    ;;
  after-restart)
    capture_checkpoint "$EVIDENCE_DIR/spark_checkpoint_after_restart.json"
    ;;
  after-replay)
    capture_kafka "$EVIDENCE_DIR/kafka_offsets_after.json"
    capture_checkpoint "$EVIDENCE_DIR/spark_checkpoint_after_replay.json"
    ;;
esac

echo "Captured replay runtime evidence phase: $PHASE"
