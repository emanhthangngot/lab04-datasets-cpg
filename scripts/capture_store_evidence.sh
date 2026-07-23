#!/usr/bin/env bash
set -euo pipefail

: "${NEO4J_PASSWORD:?Set NEO4J_PASSWORD before capturing store evidence}"

NEO4J_EVIDENCE_DIR="screenshots/neo4j"
MONGO_EVIDENCE_DIR="screenshots/mongodb"
EXPECTED_REPO_NAME="huggingface/datasets"
: "${EXPECTED_MONGO_COUNT:?Set EXPECTED_MONGO_COUNT to the discovered source-file count}"
mkdir -p "$NEO4J_EVIDENCE_DIR" "$MONGO_EVIDENCE_DIR"

docker compose exec -T neo4j cypher-shell -u neo4j -p "$NEO4J_PASSWORD" \
  "MATCH (n:CPGNode) RETURN count(n) AS node_count;" \
  | tee "$NEO4J_EVIDENCE_DIR/node_count.txt"

docker compose exec -T neo4j cypher-shell -u neo4j -p "$NEO4J_PASSWORD" \
  "MATCH (n:CPGNode) WHERE coalesce(n.placeholder, false) = false RETURN count(n) AS non_placeholder_count;" \
  | tee "$NEO4J_EVIDENCE_DIR/non_placeholder_count.txt"

docker compose exec -T neo4j cypher-shell -u neo4j -p "$NEO4J_PASSWORD" \
  "MATCH ()-[r:CPG_EDGE]->() RETURN count(r) AS edge_count;" \
  | tee "$NEO4J_EVIDENCE_DIR/edge_count.txt"

docker compose exec -T neo4j cypher-shell -u neo4j -p "$NEO4J_PASSWORD" \
  "MATCH (n:CPGNode {placeholder: true}) RETURN count(n) AS placeholder_count;" \
  | tee "$NEO4J_EVIDENCE_DIR/placeholder_count.txt"

docker compose exec -T neo4j cypher-shell -u neo4j -p "$NEO4J_PASSWORD" \
  "MATCH (n:CPGNode) WITH n.id AS id, count(*) AS c WHERE c > 1 RETURN id, c;" \
  | tee "$NEO4J_EVIDENCE_DIR/duplicate_nodes.txt"
if [ ! -s "$NEO4J_EVIDENCE_DIR/duplicate_nodes.txt" ]; then
  echo "No duplicate nodes found" > "$NEO4J_EVIDENCE_DIR/duplicate_nodes.txt"
fi

docker compose exec -T neo4j cypher-shell -u neo4j -p "$NEO4J_PASSWORD" \
  "MATCH ()-[r:CPG_EDGE]->() WITH r.id AS id, count(*) AS c WHERE c > 1 RETURN id, c;" \
  | tee "$NEO4J_EVIDENCE_DIR/duplicate_edges.txt"
if [ ! -s "$NEO4J_EVIDENCE_DIR/duplicate_edges.txt" ]; then
  echo "No duplicate edges found" > "$NEO4J_EVIDENCE_DIR/duplicate_edges.txt"
fi

docker compose exec -T mongo mongosh --quiet --eval '
  db = db.getSiblingDB("cpg");
  print("file_metadata count: " + db.file_metadata.countDocuments());
  print("unique file_id count: " + db.file_metadata.distinct("file_id").length);
  print("unique file_path count: " + db.file_metadata.distinct("file_path").length);
  print("repo values: " + JSON.stringify(db.file_metadata.distinct("repo")));
  print("--- sample document ---");
  printjson(db.file_metadata.findOne());
  print("--- duplicate file_id check ---");
  printjson(db.file_metadata.aggregate([
    { $group: { _id: "$file_id", count: { $sum: 1 } } },
    { $match: { count: { $gt: 1 } } }
  ]).toArray());
' | tee "$MONGO_EVIDENCE_DIR/metadata_evidence.txt"

MONGO_ACCEPTANCE="$(docker compose exec -T mongo mongosh --quiet --eval '
  db = db.getSiblingDB("cpg");
  print([
    db.file_metadata.countDocuments(),
    db.file_metadata.distinct("file_id").length,
    db.file_metadata.distinct("file_path").length,
    db.file_metadata.distinct("repo").join(",")
  ].join(" "));
' | tr -d '\r')"
read -r MONGO_COUNT UNIQUE_FILE_IDS UNIQUE_FILE_PATHS REPO_VALUES <<< "$MONGO_ACCEPTANCE"
if [ "$MONGO_COUNT" != "$EXPECTED_MONGO_COUNT" ] || \
   [ "$UNIQUE_FILE_IDS" != "$EXPECTED_MONGO_COUNT" ] || \
   [ "$UNIQUE_FILE_PATHS" != "$EXPECTED_MONGO_COUNT" ] || \
   [ "$REPO_VALUES" != "$EXPECTED_REPO_NAME" ]; then
  echo "ERROR: MongoDB acceptance failed: $MONGO_ACCEPTANCE" >&2
  exit 1
fi

echo "Store evidence acceptance passed."
