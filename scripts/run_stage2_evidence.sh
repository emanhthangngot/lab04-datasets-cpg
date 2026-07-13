#!/usr/bin/env bash
set -euo pipefail

: "${NEO4J_PASSWORD:?Set NEO4J_PASSWORD before running Stage 2 evidence capture}"

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

# --------------------------------------------------------------------------
# Step 1: Start infrastructure
# --------------------------------------------------------------------------
echo ">>> Step 1: Starting Docker Compose infrastructure"
docker compose up -d
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
docker compose run --rm parser \
  python -m parser_service.main --repo data/datasets --mode sample

# --------------------------------------------------------------------------
# Step 7b: Parse intentionally broken file to generate cpg.errors event
# --------------------------------------------------------------------------
echo ""
echo ">>> Step 7b: Parse invalid_syntax.py to generate error event"
docker compose run --rm parser \
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
# NOTE: Neo4j counts/duplicate checks are part of Thanh's scope (tasks 2.4-2.5).
# MongoDB verification is Thanh's scope (task 2.6).
# Included here for end-to-end runbook completeness with Tri's approval.
# --------------------------------------------------------------------------
echo ""
echo ">>> Step 10: Neo4j store verification"
docker compose exec -T neo4j cypher-shell -u neo4j -p "$NEO4J_PASSWORD" \
  "MATCH (n:CPGNode) RETURN count(n) AS node_count;" \
  | tee screenshots/neo4j/node_count.txt

docker compose exec -T neo4j cypher-shell -u neo4j -p "$NEO4J_PASSWORD" \
  "MATCH ()-[r:CPG_EDGE]->() RETURN count(r) AS edge_count;" \
  | tee screenshots/neo4j/edge_count.txt

docker compose exec -T neo4j cypher-shell -u neo4j -p "$NEO4J_PASSWORD" \
  "MATCH (n:CPGNode {placeholder: true}) RETURN count(n) AS placeholder_count;" \
  | tee screenshots/neo4j/placeholder_count.txt

echo ">>> Neo4j duplicate node check"
docker compose exec -T neo4j cypher-shell -u neo4j -p "$NEO4J_PASSWORD" \
  "MATCH (n:CPGNode) WITH n.id AS id, count(*) AS c WHERE c > 1 RETURN id, c;" \
  | tee screenshots/neo4j/duplicate_nodes.txt
if [ ! -s screenshots/neo4j/duplicate_nodes.txt ]; then
  echo "No duplicate nodes found" > screenshots/neo4j/duplicate_nodes.txt
fi

echo ">>> Neo4j duplicate edge check"
docker compose exec -T neo4j cypher-shell -u neo4j -p "$NEO4J_PASSWORD" \
  "MATCH ()-[r:CPG_EDGE]->() WITH r.id AS id, count(*) AS c WHERE c > 1 RETURN id, c;" \
  | tee screenshots/neo4j/duplicate_edges.txt
if [ ! -s screenshots/neo4j/duplicate_edges.txt ]; then
  echo "No duplicate edges found" > screenshots/neo4j/duplicate_edges.txt
fi

echo ""
echo ">>> MongoDB store verification"
docker compose exec -T mongo mongosh --quiet --eval '
  db = db.getSiblingDB("cpg");
  print("file_metadata count: " + db.file_metadata.countDocuments());
  print("--- sample document ---");
  printjson(db.file_metadata.findOne());
  print("--- duplicate file_id check ---");
  printjson(db.file_metadata.aggregate([
    { $group: { _id: "$file_id", count: { $sum: 1 } } },
    { $match: { count: { $gt: 1 } } }
  ]).toArray());
' | tee screenshots/mongodb/metadata_evidence.txt

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
python3 -m json.tool screenshots/kafka/connector_plugins.json >/dev/null
python3 -m json.tool screenshots/kafka/connector_registration.json >/dev/null
echo "Credential sanitization and JSON validation complete."

echo ""
echo "Next steps:"
echo "  1. Review evidence files"
echo "  2. Ask Thanh to recheck Neo4j/MongoDB evidence"
echo "  3. Update the Kafka/Spark and Graph Stores trackers"
