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

# --------------------------------------------------------------------------
# 4. Capture checkpoint evidence
# --------------------------------------------------------------------------
echo ""
echo "=== Checkpoint evidence ==="

# List checkpoint directory contents
echo "--- Checkpoint directory listing ---"
docker compose exec "$SPARK_SERVICE" ls -laR "$CHECKPOINT_PATH" 2>/dev/null \
  | tee "$EVIDENCE_DIR/checkpoint_listing.txt" || {
  echo "  (checkpoint directory not yet created - no metadata messages processed)"
  echo "  (checkpoint directory not yet created)" > "$EVIDENCE_DIR/checkpoint_listing.txt"
}

# Show the latest committed offset metadata if available
echo ""
echo "--- Committed offsets ---"
docker compose exec "$SPARK_SERVICE" \
  cat "$CHECKPOINT_PATH/offsets/0" 2>/dev/null \
  | tee "$EVIDENCE_DIR/checkpoint_offsets.txt" || {
  echo "  (no committed offsets yet)"
  echo "  (no committed offsets yet)" > "$EVIDENCE_DIR/checkpoint_offsets.txt"
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
  echo "  (MongoDB check skipped Ã¢â‚¬â€ mongo service may not be running)"
}

# --------------------------------------------------------------------------
# 6. Summary
# --------------------------------------------------------------------------
echo ""
echo "=== Spark evidence capture complete ==="
echo "Evidence files saved to $EVIDENCE_DIR/:"
ls -1 "$EVIDENCE_DIR/"
