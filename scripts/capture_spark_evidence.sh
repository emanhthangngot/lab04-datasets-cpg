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

if [[ -x ".venv/Scripts/python.exe" ]]; then
  PYTHON=".venv/Scripts/python.exe"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON="python3"
else
  PYTHON="python"
fi

mkdir -p "$EVIDENCE_DIR"

# --------------------------------------------------------------------------
# 1. Record Spark version
# --------------------------------------------------------------------------
echo "=== Spark version ==="
docker compose exec "$SPARK_SERVICE" spark-submit --version 2>&1 \
  | tee "$EVIDENCE_DIR/spark_version.txt"

# --------------------------------------------------------------------------
# 2. Start Spark metadata stream job (detached)
# --------------------------------------------------------------------------
echo ""
echo "=== Starting Spark metadata stream job ==="
echo "Command:"
echo "  docker compose exec -d $SPARK_SERVICE spark-submit \\"
echo "    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.mongodb.spark:mongo-spark-connector_2.12:10.3.0 \\"
echo "    /app/spark_jobs/metadata_stream_to_mongo.py"

docker compose exec -d "$SPARK_SERVICE" spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.mongodb.spark:mongo-spark-connector_2.12:10.3.0 \
  /app/spark_jobs/metadata_stream_to_mongo.py

echo "Spark job started in detached mode."

# --------------------------------------------------------------------------
# 3. Wait for initial processing
# --------------------------------------------------------------------------
echo ""
echo "=== Waiting ${WAIT_SECONDS}s for Spark to process initial messages ==="
sleep "$WAIT_SECONDS"

# A detached spark-submit can fail after the exec command itself succeeds.
# Treat an exited stream as a hard evidence failure instead of publishing
# empty checkpoint/MongoDB artifacts as if the pipeline had run.
if ! docker compose exec -T "$SPARK_SERVICE" sh -lc \
  "pgrep -f 'metadata_stream_to_mongo.py' >/dev/null"; then
  echo "ERROR: Spark metadata stream is not running after ${WAIT_SECONDS}s" >&2
  exit 1
fi

# --------------------------------------------------------------------------
# 4. Capture checkpoint evidence
# --------------------------------------------------------------------------
echo ""
echo "=== Checkpoint evidence ==="

# List checkpoint directory contents
echo "--- Checkpoint directory listing ---"
docker compose exec "$SPARK_SERVICE" ls -laR "$CHECKPOINT_PATH" 2>/dev/null \
  | tee "$EVIDENCE_DIR/checkpoint_listing.txt" || {
  echo "ERROR: checkpoint directory was not created; no metadata was processed" >&2
  exit 1
}

# Wait until Spark records both an offset and a completed batch commit, and
# require the metadata source offset to catch up with Kafka.
echo ""
echo "--- Waiting for committed metadata offset ---"
DEADLINE=$((SECONDS + COMMIT_WAIT_SECONDS))
while true; do
  LATEST_OFFSET="$(
    docker compose exec -T "$SPARK_SERVICE" sh -lc \
      "ls -1 '$CHECKPOINT_PATH/offsets' 2>/dev/null | grep -E '^[0-9]+$' | sort -n | tail -1" \
      | tr -d '\r'
  )"
  LATEST_COMMIT="$(
    docker compose exec -T "$SPARK_SERVICE" sh -lc \
      "ls -1 '$CHECKPOINT_PATH/commits' 2>/dev/null | grep -E '^[0-9]+$' | sort -n | tail -1" \
      | tr -d '\r'
  )"

  if [[ "$LATEST_OFFSET" =~ ^[0-9]+$ ]] && [[ "$LATEST_COMMIT" =~ ^[0-9]+$ ]]; then
    CHECKPOINT_KAFKA_OFFSET="$(
      docker compose exec -T "$SPARK_SERVICE" \
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
      docker compose exec -T broker kafka-run-class kafka.tools.GetOffsetShell \
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
echo "--- Committed offsets ---"
docker compose exec "$SPARK_SERVICE" \
  cat "$CHECKPOINT_PATH/offsets/$LATEST_OFFSET" 2>/dev/null \
  | tee "$EVIDENCE_DIR/checkpoint_offsets.txt" || {
  echo "ERROR: failed to read Spark checkpoint offset $LATEST_OFFSET" >&2
  exit 1
}

echo ""
echo "--- Completed batch commit ---"
docker compose exec "$SPARK_SERVICE" \
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
docker compose exec -T mongo mongosh --quiet --eval '
  db = db.getSiblingDB("cpg");
  print("file_metadata count: " + db.file_metadata.countDocuments());
  print("sample document:");
  printjson(db.file_metadata.findOne());
' 2>/dev/null | tee "$EVIDENCE_DIR/mongodb_metadata_check.txt" || {
  echo "ERROR: MongoDB metadata verification failed" >&2
  exit 1
}

MONGO_COUNT="$(docker compose exec -T mongo mongosh --quiet --eval \
  'db = db.getSiblingDB("cpg"); print(db.file_metadata.countDocuments());' \
  | tr -d '\r')"
if ! [[ "$MONGO_COUNT" =~ ^[0-9]+$ ]] || (( MONGO_COUNT == 0 )); then
  echo "ERROR: MongoDB file_metadata count is ${MONGO_COUNT:-unknown}; expected at least one metadata document" >&2
  exit 1
fi

# --------------------------------------------------------------------------
# 6. Summary
# --------------------------------------------------------------------------
echo ""
echo "=== Spark evidence capture complete ==="
echo "Evidence files saved to $EVIDENCE_DIR/:"
ls -1 "$EVIDENCE_DIR/"
