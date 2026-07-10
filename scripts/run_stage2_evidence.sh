#!/usr/bin/env bash
set -euo pipefail

# Unified Stage 2 runbook: end-to-end evidence capture.
# Owner: 23120180 - Tran Le Trung Truc
#
# This script orchestrates the full Stage 2 workflow in one shot.
# Prerequisites: Docker Desktop must be running.
#
# Usage:
#   bash scripts/run_stage2_evidence.sh

echo "============================================================"
echo " Lab04 Stage 2: Core Streaming Path â€” Full Evidence Capture"
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
# --------------------------------------------------------------------------
echo ""
echo ">>> Step 4: Apply Neo4j constraints"
docker compose exec -T neo4j cypher-shell -u neo4j -p password \
  < neo4j/constraints.cypher
echo "Neo4j constraints applied."

docker compose exec -T neo4j cypher-shell -u neo4j -p password \
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
echo ""
echo ">>> Step 7: Run parser (sample mode â€” 5 files)"
docker compose run --rm parser \
  python -m parser_service.main --repo data/datasets --mode sample

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
# --------------------------------------------------------------------------
echo ""
echo ">>> Step 10: Neo4j store verification"
docker compose exec -T neo4j cypher-shell -u neo4j -p password \
  "MATCH (n:CPGNode) RETURN count(n) AS node_count;" \
  | tee screenshots/neo4j/node_count.txt

docker compose exec -T neo4j cypher-shell -u neo4j -p password \
  "MATCH ()-[r:CPG_EDGE]->() RETURN count(r) AS edge_count;" \
  | tee screenshots/neo4j/edge_count.txt

docker compose exec -T neo4j cypher-shell -u neo4j -p password \
  "MATCH (n:CPGNode {placeholder: true}) RETURN count(n) AS placeholder_count;" \
  | tee screenshots/neo4j/placeholder_count.txt

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
wait $SPARK_PID 2>/dev/null || true

# --------------------------------------------------------------------------
# Summary
# --------------------------------------------------------------------------
echo ""
echo "============================================================"
echo " Stage 2 evidence capture complete!"
echo "============================================================"
echo ""
echo "Evidence files:"
echo "  screenshots/kafka/    â€” topic list, sample messages, connector evidence"
echo "  screenshots/spark/    â€” checkpoint, MongoDB metadata check"
echo "  screenshots/neo4j/    â€” node/edge/placeholder counts"
echo "  screenshots/mongodb/  â€” metadata count, sample doc, duplicate check"
echo ""
echo "Next steps:"
echo "  1. Review evidence files"
echo "  2. Update docs/team/kafka-spark.md with results"
echo "  3. Commit and push to feature branch"
echo "  4. Open PR to dev"
