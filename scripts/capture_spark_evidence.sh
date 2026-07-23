#!/usr/bin/env bash
set -euo pipefail

# Capture Spark Structured Streaming evidence for Stage 2.
# Owner: 23120180 - Tran Le Trung Truc
# Spec: openspec/specs/kafka-spark/spec.md - "Spark Consumes Metadata Only"
#
# Usage:
#   bash scripts/capture_spark_evidence.sh
#
# This script starts the Spark metadata stream job, waits for initial
# processing, then captures checkpoint evidence. The Spark job runs in
# detached mode so it can continue streaming while evidence is captured.

SPARK_SERVICE="${SPARK_SERVICE:-spark}"
EVIDENCE_DIR="screenshots/spark"
CHECKPOINT_PATH="/mnt/checkpoints/cpg_metadata"
WAIT_SECONDS="${SPARK_WAIT_SECONDS:-30}"
COMMIT_WAIT_SECONDS="${SPARK_COMMIT_WAIT_SECONDS:-60}"
MONGO_WAIT_SECONDS="${SPARK_MONGO_WAIT_SECONDS:-60}"
: "${EXPECTED_MONGO_COUNT:?Set EXPECTED_MONGO_COUNT to the discovered source-file count}"

if [[ -x ".venv/Scripts/python.exe" ]]; then
  PYTHON=".venv/Scripts/python.exe"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON="python3"
else
  PYTHON="python"
fi

# Git Bash rewrites container paths such as /mnt/checkpoints to Windows paths.
# Scope path-conversion disabling to Docker CLI calls in this script only, so
# host-side paths used by other runbook scripts (for example /tmp) still work.
docker_compose() {
  MSYS_NO_PATHCONV=1 docker compose "$@"
}

mkdir -p "$EVIDENCE_DIR"

# --------------------------------------------------------------------------
# 1. Record Spark version
# --------------------------------------------------------------------------
echo "=== Spark version ==="
docker_compose exec "$SPARK_SERVICE" spark-submit --version 2>&1 \
  | tee "$EVIDENCE_DIR/spark_version.txt"

# --------------------------------------------------------------------------
# 2. Start Spark metadata stream job (detached)
# --------------------------------------------------------------------------
echo ""
echo "=== Starting Spark metadata stream job ==="
echo "Command:"
echo "  docker compose exec -d $SPARK_SERVICE spark-submit \\"
echo "    --driver-memory 512m \\"
echo "    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.mongodb.spark:mongo-spark-connector_2.12:10.3.0 \\"
echo "    /app/spark_jobs/metadata_stream_to_mongo.py"

if docker_compose exec -T "$SPARK_SERVICE" sh -lc \
  "pgrep -f '[m]etadata_stream_to_mongo.py' >/dev/null"; then
  echo "Spark metadata stream is already running; reusing it for evidence capture."
else
  docker_compose exec -d "$SPARK_SERVICE" sh -c \
    "exec /opt/bitnami/spark/bin/spark-submit --driver-memory 512m \
      --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.mongodb.spark:mongo-spark-connector_2.12:10.3.0 \
      /app/spark_jobs/metadata_stream_to_mongo.py \
      > /tmp/cpg_metadata_stream.log 2>&1"
  echo "Spark job started in detached mode."
fi

# --------------------------------------------------------------------------
# 3. Wait for initial processing
# --------------------------------------------------------------------------
echo ""
echo "=== Waiting ${WAIT_SECONDS}s for Spark to process initial messages ==="
sleep "$WAIT_SECONDS"

# A detached spark-submit can fail after the exec command itself succeeds.
# Treat an exited stream as a hard evidence failure instead of publishing
# empty checkpoint/MongoDB artifacts as if the pipeline had run.
if ! docker_compose exec -T "$SPARK_SERVICE" sh -lc \
  "pgrep -f '[m]etadata_stream_to_mongo.py' >/dev/null"; then
  docker_compose exec -T "$SPARK_SERVICE" sh -lc \
    "tail -200 /tmp/cpg_metadata_stream.log 2>/dev/null || true" \
    | tee "$EVIDENCE_DIR/spark_stream.log" >&2
  echo "ERROR: Spark metadata stream is not running after ${WAIT_SECONDS}s" >&2
  exit 1
fi

docker_compose exec -T "$SPARK_SERVICE" sh -lc \
  "tail -200 /tmp/cpg_metadata_stream.log 2>/dev/null || true" \
  > "$EVIDENCE_DIR/spark_stream.log"

# --------------------------------------------------------------------------
# 4. Capture checkpoint evidence
# --------------------------------------------------------------------------
echo ""
echo "=== Checkpoint evidence ==="

# Package resolution and JVM startup can take longer than WAIT_SECONDS on a
# fresh Docker volume. Wait for the directory, numeric offset, and numeric
# commit together instead of treating a slow startup as an empty stream.
echo "--- Waiting for committed metadata offset ---"
DEADLINE=$((SECONDS + COMMIT_WAIT_SECONDS))
while true; do
  LATEST_OFFSET="$(
    docker_compose exec -T "$SPARK_SERVICE" sh -lc \
      "ls -1 '$CHECKPOINT_PATH/offsets' 2>/dev/null | grep -E '^[0-9]+$' | sort -n | tail -1" \
      | tr -d '\r'
  )"
  LATEST_COMMIT="$(
    docker_compose exec -T "$SPARK_SERVICE" sh -lc \
      "ls -1 '$CHECKPOINT_PATH/commits' 2>/dev/null | grep -E '^[0-9]+$' | sort -n | tail -1" \
      | tr -d '\r'
  )"

  if [[ "$LATEST_OFFSET" =~ ^[0-9]+$ ]] && [[ "$LATEST_COMMIT" =~ ^[0-9]+$ ]]; then
    CHECKPOINT_KAFKA_OFFSET="$(
      docker_compose exec -T "$SPARK_SERVICE" \
        cat "$CHECKPOINT_PATH/offsets/$LATEST_OFFSET" 2>/dev/null \
        | "$PYTHON" -c '
import json
import sys

lines = [line.strip() for line in sys.stdin if line.strip()]
payload = json.loads(lines[-1])
print(sum(int(value) for value in payload.get("cpg.metadata", {}).values()))
' \
        | tr -d '\r'
    )"
    KAFKA_END_OFFSET="$(
      docker_compose exec -T broker kafka-run-class kafka.tools.GetOffsetShell \
        --broker-list broker:9092 --topic cpg.metadata --time -1 \
        | awk -F: '{sum += $3} END {print sum+0}' \
        | tr -d '\r'
    )"
    if [ "$CHECKPOINT_KAFKA_OFFSET" = "$KAFKA_END_OFFSET" ]; then
      break
    fi
  fi

  if (( SECONDS >= DEADLINE )); then
    echo "ERROR: Spark did not commit and catch up with cpg.metadata within ${COMMIT_WAIT_SECONDS}s" >&2
    echo "latest offset=${LATEST_OFFSET:-missing}, latest commit=${LATEST_COMMIT:-missing}, checkpoint Kafka offset=${CHECKPOINT_KAFKA_OFFSET:-missing}, Kafka end offset=${KAFKA_END_OFFSET:-missing}" >&2
    exit 1
  fi
  sleep 2
done

echo "Spark checkpoint caught up at Kafka offset $CHECKPOINT_KAFKA_OFFSET (batch commit $LATEST_COMMIT)."

echo ""
echo "--- Checkpoint directory listing ---"
docker_compose exec "$SPARK_SERVICE" ls -laR "$CHECKPOINT_PATH" 2>/dev/null \
  | tee "$EVIDENCE_DIR/checkpoint_listing.txt" || {
  echo "ERROR: checkpoint directory disappeared after a committed batch" >&2
  exit 1
}

echo ""
echo "--- Committed offsets ---"
docker_compose exec "$SPARK_SERVICE" \
  cat "$CHECKPOINT_PATH/offsets/$LATEST_OFFSET" 2>/dev/null \
  | tee "$EVIDENCE_DIR/checkpoint_offsets.txt" || {
  echo "ERROR: failed to read Spark checkpoint offset $LATEST_OFFSET" >&2
  exit 1
}

echo ""
echo "--- Completed batch commit ---"
docker_compose exec "$SPARK_SERVICE" \
  cat "$CHECKPOINT_PATH/commits/$LATEST_COMMIT" 2>/dev/null \
  | tee "$EVIDENCE_DIR/checkpoint_commits.txt" || {
  echo "ERROR: failed to read Spark batch commit $LATEST_COMMIT" >&2
  exit 1
}

# --------------------------------------------------------------------------
# 5. Capture MongoDB document count (cross-check for metadata ingestion)
# --------------------------------------------------------------------------
echo ""
echo "=== MongoDB metadata count (via mongosh) ==="
MONGO_COUNT=""
MONGO_DEADLINE=$((SECONDS + MONGO_WAIT_SECONDS))
while true; do
  if MONGO_COUNT="$(
    docker_compose exec -T mongo mongosh --quiet --eval \
      'db = db.getSiblingDB("cpg"); print(db.file_metadata.countDocuments());' \
      2>/dev/null | tr -d '\r'
  )" && [ "$MONGO_COUNT" = "$EXPECTED_MONGO_COUNT" ]; then
    break
  fi
  if (( SECONDS >= MONGO_DEADLINE )); then
    echo "ERROR: MongoDB file_metadata count is ${MONGO_COUNT:-unknown}; expected $EXPECTED_MONGO_COUNT" >&2
    exit 1
  fi
  sleep 2
done

docker_compose exec -T mongo mongosh --quiet --eval '
  db = db.getSiblingDB("cpg");
  print("file_metadata count: " + db.file_metadata.countDocuments());
  print("sample document:");
  printjson(db.file_metadata.findOne());
' 2>/dev/null | tee "$EVIDENCE_DIR/mongodb_metadata_check.txt" || {
  echo "ERROR: MongoDB metadata verification failed" >&2
  exit 1
}

# --------------------------------------------------------------------------
# 6. Summary
# --------------------------------------------------------------------------
echo ""
echo "=== Spark evidence capture complete ==="
echo "Evidence files saved to $EVIDENCE_DIR/:"
ls -1 "$EVIDENCE_DIR/"
