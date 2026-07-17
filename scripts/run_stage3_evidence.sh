#!/usr/bin/env bash
set -Eeuo pipefail

COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-lab04-datasets-cpg}"
export COMPOSE_PROJECT_NAME

: "${RESET_DOCKER_STATE:?Set RESET_DOCKER_STATE=1 for the canonical Stage 3 run}"
: "${NEO4J_PASSWORD:?Set NEO4J_PASSWORD for the local Neo4j container}"
if [[ "$RESET_DOCKER_STATE" != "1" ]]; then
  echo "ERROR: RESET_DOCKER_STATE must be exactly 1" >&2
  exit 1
fi

TARGET_RELATIVE="src/datasets/__init__.py"
TARGET_FILE="data/datasets/$TARGET_RELATIVE"
FILE_ID="6c39568a6a11c430"
EXPECTED_DATASET_COMMIT="41adfd0f9ee9ba3a6b4f719d5b551c5b19ae45e2"
EVIDENCE_DIR="screenshots/replay"
PIPELINE_COMMIT="$(git rev-parse HEAD)"
CAPTURED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
REPLAY_RUN_ID="stage3-replay-$(date -u +%Y%m%dT%H%M%SZ)"
ORIGINAL_TARGET=""
TARGET_SAVED=0
TARGET_RESTORED=0

restore_target() {
  if [[ "$TARGET_SAVED" == "1" && -n "$ORIGINAL_TARGET" && -f "$ORIGINAL_TARGET" ]]; then
    cp "$ORIGINAL_TARGET" "$TARGET_FILE"
    TARGET_RESTORED=1
  fi
}
trap restore_target EXIT

if [[ -n "$(git status --porcelain)" ]]; then
  echo "ERROR: pipeline worktree must be clean before canonical evidence capture" >&2
  exit 1
fi
if [[ -d data/datasets/.git && -n "$(git -C data/datasets status --porcelain)" ]]; then
  echo "ERROR: dataset clone must be clean before canonical evidence capture" >&2
  exit 1
fi

if [[ -x ".venv/Scripts/python.exe" ]]; then
  PYTHON=".venv/Scripts/python.exe"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON="python"
else
  PYTHON="/usr/bin/python"
fi

mkdir -p "$EVIDENCE_DIR"
rm -f \
  "$EVIDENCE_DIR/run_metadata.json" \
  "$EVIDENCE_DIR/source_patch.diff" \
  "$EVIDENCE_DIR/kafka_offsets_before.json" \
  "$EVIDENCE_DIR/kafka_offsets_after.json" \
  "$EVIDENCE_DIR/kafka_graph_counts_after.json" \
  "$EVIDENCE_DIR/spark_checkpoint_before.json" \
  "$EVIDENCE_DIR/spark_checkpoint_after_restart.json" \
  "$EVIDENCE_DIR/spark_checkpoint_after_replay.json" \
  "$EVIDENCE_DIR/neo4j_before.json" \
  "$EVIDENCE_DIR/neo4j_pre_cleanup.json" \
  "$EVIDENCE_DIR/neo4j_cleanup.txt" \
  "$EVIDENCE_DIR/neo4j_after.json" \
  "$EVIDENCE_DIR/mongodb_before.json" \
  "$EVIDENCE_DIR/mongodb_after_restart.json" \
  "$EVIDENCE_DIR/mongodb_after_replay.json" \
  "$EVIDENCE_DIR/evidence_metadata.json" \
  "$EVIDENCE_DIR/neo4j_after_cleanup.png" \
  "$EVIDENCE_DIR/mongodb_after_replay.png" \
  "$EVIDENCE_DIR/stage3_replay_manifest.json"

echo "=== Stage 3: rebuild clean Stage 2 baseline ==="
export RESET_DOCKER_STATE NEO4J_PASSWORD
bash scripts/run_stage2_evidence.sh

DATASET_COMMIT="$(git -C data/datasets rev-parse HEAD)"
if [[ "$DATASET_COMMIT" != "$EXPECTED_DATASET_COMMIT" ]]; then
  echo "ERROR: expected dataset commit $EXPECTED_DATASET_COMMIT, got $DATASET_COMMIT" >&2
  exit 1
fi
if [[ -n "$(git -C data/datasets status --porcelain)" ]]; then
  echo "ERROR: Stage 2 baseline left the dataset clone dirty" >&2
  exit 1
fi
"$PYTHON" scripts/stage2_evidence_manifest.py validate --root .

ORIGINAL_TARGET="$(mktemp)"
cp "$TARGET_FILE" "$ORIGINAL_TARGET"
TARGET_SAVED=1

read -r BASELINE_RUN_ID BEFORE_CONTENT_HASH <<< "$(
  "$PYTHON" -c '
import json, sys
target = sys.argv[1]
events = [json.loads(line) for line in open(sys.argv[2], encoding="utf-8") if line.strip()]
matches = [event for event in events if event.get("file_path") == target]
if len(matches) != 1:
    raise SystemExit(f"expected one baseline metadata event for {target}, got {len(matches)}")
print(matches[0]["run_id"], matches[0]["content_hash"])
' "$TARGET_RELATIVE" screenshots/kafka/sample_cpg_metadata.json
)"

export FILE_ID BASELINE_RUN_ID REPLAY_RUN_ID
echo "=== Capture baseline runtime and stores ==="
EXPECTED_METADATA_OFFSET=5 bash scripts/capture_replay_runtime_evidence.sh before
bash scripts/capture_replay_store_evidence.sh before

echo "=== Restart Spark with the Stage 2 checkpoint ==="
docker compose restart spark
docker compose exec -d spark sh -c \
  "exec /opt/bitnami/spark/bin/spark-submit --driver-memory 512m \
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.mongodb.spark:mongo-spark-connector_2.12:10.3.0 \
    /app/spark_jobs/metadata_stream_to_mongo.py \
    > /tmp/stage3_metadata_stream.log 2>&1"
EXPECTED_METADATA_OFFSET=5 bash scripts/capture_replay_runtime_evidence.sh after-restart
bash scripts/capture_replay_store_evidence.sh after-restart

echo "=== Apply deterministic replay mutation ==="
"$PYTHON" -c '
from pathlib import Path
import sys
path = Path(sys.argv[1])
old = "__version__ = \"5.0.1.dev0\""
new = "__version__: str = \"5.0.1.dev0+lab04-replay\"\nLAB04_REPLAY_MARKER = \"replay_v2\""
source = path.read_text(encoding="utf-8")
if source.count(old) != 1:
    raise SystemExit(f"expected exactly one canonical version assignment, got {source.count(old)}")
path.write_text(source.replace(old, new, 1), encoding="utf-8")
' "$TARGET_FILE"

AFTER_CONTENT_HASH="$("$PYTHON" -c '
from pathlib import Path
import hashlib, sys
source = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace")
print(hashlib.sha256(source.encode("utf-8")).hexdigest())
' "$TARGET_FILE")"
if [[ "$AFTER_CONTENT_HASH" == "$BEFORE_CONTENT_HASH" ]]; then
  echo "ERROR: canonical source mutation did not change content_hash" >&2
  exit 1
fi

diff_status=0
diff -u -U0 --label "a/$TARGET_RELATIVE" --label "b/$TARGET_RELATIVE" \
  "$ORIGINAL_TARGET" "$TARGET_FILE" > "$EVIDENCE_DIR/source_patch.diff" || diff_status=$?
if [[ "$diff_status" != "1" ]]; then
  echo "ERROR: source patch capture returned unexpected status $diff_status" >&2
  exit 1
fi

docker compose run --rm \
  -e REPO_NAME=huggingface/datasets \
  -e COMMIT_SHA="$DATASET_COMMIT" \
  -e RUN_ID="$REPLAY_RUN_ID" \
  parser python -m parser_service.main \
  --repo data/datasets --mode file --file "$TARGET_FILE"

echo "=== Wait for graph and metadata consumers ==="
REQUIRE_UNIQUE_EVENT_IDS=false \
GRAPH_COUNTS_FILE="screenshots/replay/kafka_graph_counts_after.json" \
EXPECTED_COMMIT_SHA="$DATASET_COMMIT" \
bash scripts/wait_neo4j_connector_idle.sh
EXPECTED_METADATA_OFFSET=6 bash scripts/capture_replay_runtime_evidence.sh after-replay

bash scripts/capture_replay_store_evidence.sh pre-cleanup
read -r STALE_NODES STALE_EDGES <<< "$(
  "$PYTHON" -c '
import json, sys
value = json.load(open(sys.argv[1], encoding="utf-8"))
print(value["stale_nodes"], value["stale_edges"])
' "$EVIDENCE_DIR/neo4j_pre_cleanup.json"
)"

echo "=== Delete stale target graph entities ==="
docker compose exec -T neo4j cypher-shell --format plain \
  -u neo4j -p "$NEO4J_PASSWORD" \
  -P "{file_id: '$FILE_ID', run_id: '$REPLAY_RUN_ID'}" \
  < neo4j/cleanup_stale.cypher
printf 'stale_edges_deleted=%s\nstale_nodes_deleted=%s\n' \
  "$STALE_EDGES" "$STALE_NODES" > "$EVIDENCE_DIR/neo4j_cleanup.txt"
bash scripts/capture_replay_store_evidence.sh after

restore_target
if ! cmp -s "$ORIGINAL_TARGET" "$TARGET_FILE"; then
  echo "ERROR: failed to restore replay target" >&2
  exit 1
fi

"$PYTHON" -c '
import json, sys
keys = (
    "captured_at", "pipeline_commit", "dataset_commit", "dataset_repo",
    "target_file", "file_id", "baseline_run_id", "replay_run_id",
    "before_content_hash", "after_content_hash",
)
payload = dict(zip(keys, sys.argv[1:]))
payload["source_restored"] = True
json.dump(payload, sys.stdout, indent=2)
print()
' \
  "$CAPTURED_AT" "$PIPELINE_COMMIT" "$DATASET_COMMIT" "huggingface/datasets" \
  "$TARGET_RELATIVE" "$FILE_ID" "$BASELINE_RUN_ID" "$REPLAY_RUN_ID" \
  "$BEFORE_CONTENT_HASH" "$AFTER_CONTENT_HASH" \
  > "$EVIDENCE_DIR/run_metadata.json"

for pattern in "$EVIDENCE_DIR"/*.json "$EVIDENCE_DIR"/*.txt "$EVIDENCE_DIR"/*.diff; do
  [[ -e "$pattern" ]] || continue
  bash scripts/sanitize_evidence.sh "$pattern"
done

echo "Machine replay evidence captured successfully."
echo "Keep the services running and capture:"
echo "  $EVIDENCE_DIR/neo4j_after_cleanup.png"
echo "  $EVIDENCE_DIR/mongodb_after_replay.png"
echo "Then run: bash scripts/finalize_stage3_evidence.sh"
