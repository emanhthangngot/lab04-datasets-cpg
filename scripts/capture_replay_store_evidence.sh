#!/usr/bin/env bash
set -euo pipefail

: "${NEO4J_PASSWORD:?Set NEO4J_PASSWORD before capturing replay store evidence}"

PHASE="${1:-}"
FILE_ID="${FILE_ID:-6c39568a6a11c430}"
BASELINE_RUN_ID="${BASELINE_RUN_ID:-}"
REPLAY_RUN_ID="${REPLAY_RUN_ID:-}"
EVIDENCE_DIR="${REPLAY_EVIDENCE_DIR:-screenshots/replay}"
mkdir -p "$EVIDENCE_DIR"

case "$PHASE" in
  before|after-restart|pre-cleanup|after) ;;
  *)
    echo "Usage: $0 {before|after-restart|pre-cleanup|after}" >&2
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

neo4j_scalar() {
  local query="$1"
  docker compose exec -T neo4j cypher-shell --format plain \
    -u neo4j -p "$NEO4J_PASSWORD" "$query" \
    | tail -1 | tr -d '\r[:space:]'
}

capture_neo4j() {
  local output="$1"
  local include_stale="$2"
  local explicit_nodes placeholders edges target_nodes target_edges
  local duplicate_node_groups duplicate_edge_groups stale_nodes stale_edges old_run_entities

  explicit_nodes="$(neo4j_scalar 'MATCH (n:CPGNode) WHERE coalesce(n.placeholder, false) = false RETURN count(n);')"
  placeholders="$(neo4j_scalar 'MATCH (n:CPGNode {placeholder: true}) RETURN count(n);')"
  edges="$(neo4j_scalar 'MATCH ()-[r:CPG_EDGE]->() RETURN count(r);')"
  target_nodes="$(neo4j_scalar "MATCH (n:CPGNode {file_id: '$FILE_ID'}) RETURN count(n);")"
  target_edges="$(neo4j_scalar "MATCH ()-[r:CPG_EDGE {file_id: '$FILE_ID'}]->() RETURN count(r);")"
  duplicate_node_groups="$(neo4j_scalar 'MATCH (n:CPGNode) WITH n.id AS id, count(*) AS c WHERE c > 1 RETURN count(*);')"
  duplicate_edge_groups="$(neo4j_scalar 'MATCH ()-[r:CPG_EDGE]->() WITH r.id AS id, count(*) AS c WHERE c > 1 RETURN count(*);')"

  stale_nodes=0
  stale_edges=0
  old_run_entities=0
  if [[ "$include_stale" == "pre" ]]; then
    : "${REPLAY_RUN_ID:?Set REPLAY_RUN_ID for pre-cleanup capture}"
    stale_nodes="$(neo4j_scalar "MATCH (n:CPGNode {file_id: '$FILE_ID'}) WHERE n.run_id <> '$REPLAY_RUN_ID' RETURN count(n);")"
    stale_edges="$(neo4j_scalar "MATCH ()-[r:CPG_EDGE {file_id: '$FILE_ID'}]->() WHERE r.run_id <> '$REPLAY_RUN_ID' RETURN count(r);")"
  elif [[ "$include_stale" == "after" ]]; then
    : "${BASELINE_RUN_ID:?Set BASELINE_RUN_ID for final capture}"
    old_nodes="$(neo4j_scalar "MATCH (n:CPGNode {file_id: '$FILE_ID', run_id: '$BASELINE_RUN_ID'}) RETURN count(n);")"
    old_edges="$(neo4j_scalar "MATCH ()-[r:CPG_EDGE {file_id: '$FILE_ID', run_id: '$BASELINE_RUN_ID'}]->() RETURN count(r);")"
    old_run_entities=$((old_nodes + old_edges))
  fi

  local keys
  local values
  if [[ "$include_stale" == "before" ]]; then
    keys="explicit_nodes,placeholders,edges,target_nodes,target_edges,duplicate_node_groups,duplicate_edge_groups"
    values="$explicit_nodes $placeholders $edges $target_nodes $target_edges $duplicate_node_groups $duplicate_edge_groups"
  elif [[ "$include_stale" == "pre" ]]; then
    keys="explicit_nodes,placeholders,edges,target_nodes,target_edges,stale_nodes,stale_edges"
    values="$explicit_nodes $placeholders $edges $target_nodes $target_edges $stale_nodes $stale_edges"
  else
    keys="explicit_nodes,placeholders,edges,target_nodes,target_edges,stale_nodes,stale_edges,old_run_entities,duplicate_node_groups,duplicate_edge_groups"
    values="$explicit_nodes $placeholders $edges $target_nodes $target_edges $stale_nodes $stale_edges $old_run_entities $duplicate_node_groups $duplicate_edge_groups"
  fi

  # All values are numeric scalars returned by cypher-shell; word splitting is
  # intentional here so the Python normalizer receives one argument per key.
  # shellcheck disable=SC2086
  "$PYTHON" -c '
import json, sys
keys = sys.argv[1].split(",")
values = [int(value) for value in sys.argv[2:]]
json.dump(dict(zip(keys, values)), sys.stdout, indent=2)
print()
' "$keys" $values > "$output"
}

capture_mongodb() {
  local output="$1"
  docker compose exec -T mongo mongosh --quiet --eval '
    db = db.getSiblingDB("cpg");
    const docs = db.file_metadata.find(
      {},
      {_id: 0, file_id: 1, run_id: 1, content_hash: 1}
    ).sort({file_id: 1}).toArray();
    const duplicates = db.file_metadata.aggregate([
      {$group: {_id: "$file_id", count: {$sum: 1}}},
      {$match: {count: {$gt: 1}}}
    ]).toArray();
    const byId = {};
    docs.forEach(doc => { byId[doc.file_id] = {run_id: doc.run_id, content_hash: doc.content_hash}; });
    print(JSON.stringify({
      documents: db.file_metadata.countDocuments(),
      duplicate_file_id_groups: duplicates.length,
      documents_by_file_id: byId
    }));
  ' | tr -d '\r' | "$PYTHON" -m json.tool > "$output"
}

case "$PHASE" in
  before)
    capture_neo4j "$EVIDENCE_DIR/neo4j_before.json" before
    capture_mongodb "$EVIDENCE_DIR/mongodb_before.json"
    ;;
  after-restart)
    capture_mongodb "$EVIDENCE_DIR/mongodb_after_restart.json"
    ;;
  pre-cleanup)
    capture_neo4j "$EVIDENCE_DIR/neo4j_pre_cleanup.json" pre
    ;;
  after)
    capture_neo4j "$EVIDENCE_DIR/neo4j_after.json" after
    capture_mongodb "$EVIDENCE_DIR/mongodb_after_replay.json"
    ;;
esac

echo "Captured replay store evidence phase: $PHASE"
