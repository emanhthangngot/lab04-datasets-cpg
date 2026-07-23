#!/usr/bin/env bash
set -euo pipefail

# Capture Kafka evidence for Stage 2: topic list and sample messages.
# Owner: 23120180 - Tran Le Trung Truc
# Spec: openspec/specs/kafka-spark/spec.md - "Kafka Evidence Is Reproducible"
#
# Usage:
#   bash scripts/capture_kafka_evidence.sh
#
# Output files are saved under screenshots/kafka/ for Jupyter Book evidence.

KAFKA_SERVICE="${KAFKA_SERVICE:-broker}"
BOOTSTRAP="${KAFKA_BOOTSTRAP_INTERNAL:-broker:9092}"
EVIDENCE_DIR="screenshots/kafka"
SAMPLE_COUNT="${SAMPLE_COUNT:-3}"
: "${METADATA_CAPTURE_COUNT:?Set METADATA_CAPTURE_COUNT to the discovered source-file count}"
: "${EXPECTED_COMMIT_SHA:?Set EXPECTED_COMMIT_SHA to the cloned dataset Git SHA}"

if [[ -x ".venv/Scripts/python.exe" ]]; then
  PYTHON=".venv/Scripts/python.exe"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON="python3"
else
  PYTHON="python"
fi

mkdir -p "$EVIDENCE_DIR"

# --------------------------------------------------------------------------
# 1. Topic list
# --------------------------------------------------------------------------
echo "=== Capturing Kafka topic list ==="
docker compose exec "$KAFKA_SERVICE" kafka-topics \
  --bootstrap-server "$BOOTSTRAP" \
  --list | tee "$EVIDENCE_DIR/topic_list.txt"

echo ""
echo "=== Capturing Kafka topic details ==="
docker compose exec "$KAFKA_SERVICE" kafka-topics \
  --bootstrap-server "$BOOTSTRAP" \
  --describe | tee "$EVIDENCE_DIR/topic_details.txt"

# --------------------------------------------------------------------------
# 2. Sample messages from each topic
# --------------------------------------------------------------------------
capture_samples() {
  local topic="$1"
  local sample_count="$2"
  local output_file="$EVIDENCE_DIR/sample_${topic//\./_}.json"

  echo ""
  echo "=== Capturing $sample_count sample messages from $topic ==="
  docker compose exec "$KAFKA_SERVICE" kafka-console-consumer \
    --bootstrap-server "$BOOTSTRAP" \
    --topic "$topic" \
    --from-beginning \
    --max-messages "$sample_count" \
    --timeout-ms 10000 \
    2>/dev/null | tee "$output_file"

  # Validate required fields in each message
  if [ -s "$output_file" ]; then
    echo ""
    echo "--- Validating $topic sample fields ---"
    "$PYTHON" -c '
import json
import sys

output_file = sys.argv[1]
topic = sys.argv[2]
expected_commit = sys.argv[3]
required = ["schema_version", "event_time", "file_id", "file_path"]
extra_map_fields = ["properties"] if topic in ("cpg.nodes", "cpg.edges") else []
errors = []
commit_shas = set()

with open(output_file) as f:
    for i, line in enumerate(f, 1):
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            errors.append(f"  Line {i}: invalid JSON")
            continue
        commit_shas.add(msg.get("commit_sha"))
        for field in required:
            if field not in msg:
                errors.append(f"  Line {i}: missing {field}")
        for field in extra_map_fields:
            val = msg.get(field)
            if not isinstance(val, dict):
                errors.append(f"  Line {i}: {field} is not a map: {type(val).__name__}")
        if topic == "cpg.errors" and msg.get("status") != "failed":
            errors.append(f"  Line {i}: cpg.errors status must be 'failed'")

if "unknown" in commit_shas or commit_shas != {expected_commit}:
    errors.append(
        f"  unexpected commit_sha values: {sorted(repr(value) for value in commit_shas)}; "
        f"expected {expected_commit!r}"
    )

if errors:
    print(f"VALIDATION FAILED for {topic}:", file=sys.stderr)
    for e in errors:
        print(e, file=sys.stderr)
    sys.exit(1)
else:
    print(f"VALIDATION OK: all samples from {topic} contain required fields")
' "$output_file" "$topic" "$EXPECTED_COMMIT_SHA"
  else
    echo "No messages available in $topic" >&2
    return 1
  fi
}

capture_samples cpg.nodes "$SAMPLE_COUNT"
capture_samples cpg.edges "$SAMPLE_COUNT"
capture_samples cpg.metadata "$METADATA_CAPTURE_COUNT"
capture_samples cpg.errors 1

# --------------------------------------------------------------------------
# 3. Summary
# --------------------------------------------------------------------------
echo ""
echo "=== Kafka evidence capture complete ==="
echo "Evidence files saved to $EVIDENCE_DIR/:"
ls -1 "$EVIDENCE_DIR/"
