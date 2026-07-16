#!/usr/bin/env bash
set -euo pipefail

: "${NEO4J_PASSWORD:?Set NEO4J_PASSWORD before running Stage 2 evidence capture}"
: "${RESET_DOCKER_STATE:?Set RESET_DOCKER_STATE=1 before starting Stage 2}"
if [ "$RESET_DOCKER_STATE" != "1" ]; then
  echo "ERROR: RESET_DOCKER_STATE must be exactly 1 for a clean Stage 2 run" >&2
  exit 1
fi
COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-lab04-datasets-cpg}"
export COMPOSE_PROJECT_NAME
EXPECTED_REPO_NAME="huggingface/datasets"
CONNECT_URL="${CONNECT_URL:-http://localhost:8083}"
CONNECT_WAIT_SECONDS="${CONNECT_WAIT_SECONDS:-120}"

if [[ -x ".venv/Scripts/python.exe" ]]; then
  PYTHON=".venv/Scripts/python.exe"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON="python3"
else
  PYTHON="python"
fi

# Unified Stage 2 runbook: end-to-end evidence capture.
# Owner: 23120180 - Tran Le Trung Truc
#
# This script orchestrates the full Stage 2 workflow in one shot.
# Prerequisites: Docker Desktop must be running.
#
# Usage:
#   bash scripts/run_stage2_evidence.sh

echo "============================================================"
echo " Lab04 Stage 2: Core Streaming Path - Full Evidence Capture"
echo "============================================================"
echo ""

echo ">>> Resetting local Docker state for a clean Stage 2 run"
docker compose down -v --remove-orphans

# --------------------------------------------------------------------------
# Step 1: Start infrastructure
# --------------------------------------------------------------------------
echo ">>> Step 1: Starting Docker Compose infrastructure"
# Do not start the one-shot parser service here. It is invoked exactly once in
# Step 7 after the topics, connector, and Spark capture are ready.
docker compose up -d broker neo4j mongo connect spark
echo "Waiting 15s for services to become healthy..."
sleep 15

# Quick health check
docker compose ps

# --------------------------------------------------------------------------
# Step 2: Clone repository (if not already cloned)
# --------------------------------------------------------------------------
echo ""
echo ">>> Step 2: Clone repository"
bash scripts/clone_repo.sh

DATASET_COMMIT_SHA="$(git -C data/datasets rev-parse HEAD)"
if ! [[ "$DATASET_COMMIT_SHA" =~ ^[0-9a-f]{40}$ ]]; then
  echo "ERROR: invalid dataset commit SHA: $DATASET_COMMIT_SHA" >&2
  exit 1
fi
export EXPECTED_COMMIT_SHA="$DATASET_COMMIT_SHA"
echo "Dataset commit SHA verified: $DATASET_COMMIT_SHA"

echo ">>> Verifying parser repository identity"
ACTUAL_REPO_NAME="$(
  docker compose run --rm parser printenv REPO_NAME | tr -d '\r'
)"
if [ "$ACTUAL_REPO_NAME" != "$EXPECTED_REPO_NAME" ]; then
  echo "ERROR: parser REPO_NAME must be $EXPECTED_REPO_NAME, got $ACTUAL_REPO_NAME" >&2
  exit 1
fi
echo "Parser repository identity verified: $ACTUAL_REPO_NAME"

# --------------------------------------------------------------------------
# Step 3: Create Kafka topics explicitly
# --------------------------------------------------------------------------
echo ""
echo ">>> Step 3: Create Kafka topics"
bash scripts/init_kafka_topics.sh

# --------------------------------------------------------------------------
# Step 4: Apply Neo4j constraints
# NOTE: Neo4j constraints are part of Thanh's scope (task 2.3).
# Included here for end-to-end runbook completeness with Tri's approval.
# --------------------------------------------------------------------------
echo ""
echo ">>> Step 4: Apply Neo4j constraints (cross-scope: Thanh task 2.3)"
docker compose exec -T neo4j cypher-shell -u neo4j -p "$NEO4J_PASSWORD" \
  < neo4j/constraints.cypher
echo "Neo4j constraints applied."

docker compose exec -T neo4j cypher-shell -u neo4j -p "$NEO4J_PASSWORD" \
  "SHOW CONSTRAINTS;"

# --------------------------------------------------------------------------
# Step 5: Verify connector plugin and register Neo4j sink
# --------------------------------------------------------------------------
echo ""
echo ">>> Step 5: Verify connector plugin and register Neo4j sink"
echo "Waiting for Kafka Connect API to become ready..."
CONNECT_DEADLINE=$((SECONDS + CONNECT_WAIT_SECONDS))
until curl -fsS "$CONNECT_URL/connector-plugins" >/dev/null 2>&1; do
  if (( SECONDS >= CONNECT_DEADLINE )); then
    echo "ERROR: Kafka Connect API was not ready within ${CONNECT_WAIT_SECONDS}s" >&2
    exit 1
  fi
  sleep 2
done
echo "Kafka Connect API is ready."
bash scripts/capture_connector_evidence.sh

# --------------------------------------------------------------------------
# Step 6: Start Spark metadata stream
# --------------------------------------------------------------------------
echo ""
echo ">>> Step 6: Start Spark metadata stream"
bash scripts/capture_spark_evidence.sh &
SPARK_PID=$!

# --------------------------------------------------------------------------
# Step 7: Run parser in sample mode
# --------------------------------------------------------------------------
echo ">>> Step 7a: Run parser (sample mode - 5 files)"
docker compose run --rm -e REPO_NAME="$EXPECTED_REPO_NAME" \
  -e COMMIT_SHA="$DATASET_COMMIT_SHA" parser \
  python -m parser_service.main --repo data/datasets --mode sample

# --------------------------------------------------------------------------
# Step 7b: Parse intentionally broken file to generate cpg.errors event
# --------------------------------------------------------------------------
echo ""
echo ">>> Step 7b: Parse invalid_syntax.py to generate error event"
docker compose run --rm -e REPO_NAME="$EXPECTED_REPO_NAME" \
  -e COMMIT_SHA="$DATASET_COMMIT_SHA" parser \
  python -m parser_service.main --repo data --mode file --file data/invalid_syntax.py \
  || echo "(Expected: parser emits error event for SyntaxError)"

# --------------------------------------------------------------------------
# Step 8: Wait for connector to consume all messages
# --------------------------------------------------------------------------
echo ""
echo ">>> Step 8: Wait for Neo4j connector to catch up"
bash scripts/wait_neo4j_connector_idle.sh

# --------------------------------------------------------------------------
# Step 9: Capture Kafka evidence
# --------------------------------------------------------------------------
echo ""
echo ">>> Step 9: Capture Kafka evidence"
bash scripts/capture_kafka_evidence.sh

# --------------------------------------------------------------------------
# Step 10: Capture store verification
# Neo4j/MongoDB evidence and fail-fast acceptance are centralized in the
# reusable store capture script.
# --------------------------------------------------------------------------
echo ""
echo ">>> Step 10: Neo4j store verification"
bash scripts/capture_store_evidence.sh

# Wait for the Spark evidence background task
wait "$SPARK_PID"

# --------------------------------------------------------------------------
# Summary
# --------------------------------------------------------------------------
echo ""
echo "============================================================"
echo " Stage 2 evidence capture complete!"
echo "============================================================"
echo ""
echo "Evidence files:"
echo "  screenshots/kafka/    - topic list, sample messages, connector evidence"
echo "  screenshots/spark/    - checkpoint, MongoDB metadata check"
echo "  screenshots/neo4j/    - node/edge/placeholder counts and duplicate checks"
echo "  screenshots/mongodb/  - metadata count, sample doc, duplicate check"
echo ""
# --------------------------------------------------------------------------
# Step 11: Sanitize and validate evidence
# --------------------------------------------------------------------------
echo ""
echo ">>> Step 11: Sanitizing credentials from evidence artifacts"
for dir in screenshots/kafka screenshots/neo4j screenshots/mongodb screenshots/spark; do
  [ -d "$dir" ] || continue
  bash scripts/sanitize_evidence.sh "$dir"/*.json "$dir"/*.txt
done
"$PYTHON" -m json.tool screenshots/kafka/connector_plugins.json >/dev/null
"$PYTHON" -m json.tool screenshots/kafka/connector_registration.json >/dev/null
echo "Credential sanitization and JSON validation complete."

echo ""
echo "Next steps:"
echo "  1. Review evidence files"
echo "  2. Ask Thanh to recheck Neo4j/MongoDB evidence"
echo "  3. Update the Kafka/Spark and Graph Stores trackers"
