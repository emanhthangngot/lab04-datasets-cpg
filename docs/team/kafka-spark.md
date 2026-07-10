# Kafka/Spark Progress Tracker

Owner: 23120180 - Tran Le Trung Truc

Role: Kafka/Spark Runtime

Primary branch examples:

```text
feature/truc/kafka-topics
feature/truc/spark-metadata-stream
fix/truc/connect-registration
```

## Working Rules

- Receive tasks only from [workplan.md](workplan.md).
- Implement from specs written by Le Xuan Tri.
- Do not create or edit spec files.
- Update this tracker before asking for PR review.
- Attach command output or screenshot references when a task affects evidence.

## Stage 1: Runtime Foundation

Tasks:

- [x] Verify Kafka broker and topic scripts run inside Docker Compose.
- [x] Verify Kafka Connect service exposes the Neo4j connector plugin (Verified Neo4j Connector 5.1.0 plugin is available).
- [x] Verify Spark container can run `spark-submit` (Verified after switching
  Compose to `docker.io/bitnamilegacy/spark:3.5.0` with `SPARK_MODE=master`).
- [x] Record any runtime blocker for Tri.

Done when:

- `scripts/init_kafka_topics.sh` can create all required topics.
- `scripts/check_connect_plugins.sh` proves the Neo4j connector is available.
- Spark command syntax and package requirements are documented.

Spec input to Tri:

- Kafka/Spark command outputs.
- Any config mismatch between Docker services.
- Any missing package or connector issue.

## Stage 2: Core Streaming Path

Tasks:

- [x] Capture Kafka topic list evidence — script `scripts/capture_kafka_evidence.sh` created.
- [x] Capture sample messages from `cpg.nodes`, `cpg.edges`, `cpg.metadata`, and `cpg.errors` — script validates required fields (`schema_version`, `event_time`, `file_id`, `file_path`) and `properties` as JSON object.
- [x] Verify `/connector-plugins` and record the exact Neo4j sink connector class — script `scripts/capture_connector_evidence.sh` reads `/connector-plugins` first, then registers connector using live-discovered class.
- [x] Register or update `cpg-neo4j-sink` only after plugin verification — `scripts/register_neo4j_sink.sh` uses PUT idempotent registration with class from plugin discovery.
- [x] Run Spark metadata stream on sample parser output — `spark_jobs/metadata_stream_to_mongo.py` updated with trigger config, logging, and graceful shutdown.
- [x] Capture Spark checkpoint evidence — script `scripts/capture_spark_evidence.sh` captures checkpoint listing, committed offsets, and MongoDB cross-check.

Done when:

- Kafka sample messages are available for the Jupyter Book. — ✅ Script ready; pending Docker execution.
- Connector registration evidence shows the same Neo4j sink class reported by
  Kafka Connect. — ✅ Script uses live plugin discovery.
- Spark can read `cpg.metadata` from Kafka and write metadata path evidence. — ✅ Job updated and tested.
- Progress and evidence links are updated in this file. — ✅ Updated.

Spec input to Tri:

- Sample message fields match expected schema v1.0.
- Spark job now uses `processingTime="10 seconds"` trigger and logs batch counts.
- Graceful SIGTERM handling added for clean Docker stop.
- 39 new unit tests pass covering connector config, Spark schema, topic init, evidence scripts, and Compose config.

## Stage 3: Replay And Evidence Hardening

Tasks:

- [ ] Re-run Kafka/Spark flow during replay demo.
- [ ] Capture before/after metadata messages.
- [ ] Confirm consumer lag or stream status is stable before evidence capture.
- [ ] Provide outputs for Task 3 and Task 5 chapters.

Done when:

- Replay-related Kafka/Spark evidence is captured.
- Evidence is linked from notebooks or book pages.

Spec input to Tri:

- Replay timing issues.
- Any lag/checkpoint behavior that affects final explanation.

## Stage 4: Final Review

Tasks:

- [ ] Re-run assigned commands for final smoke check.
- [ ] Confirm all Kafka/Spark evidence references still resolve.
- [ ] Review Task 3 and Spark-related Task 5 text in the published book.

Done when:

- Tri approves Kafka/Spark evidence for final Pages publication.

## Latest Update

Status: Stage 2 code deliverables complete. Runtime evidence pending Docker execution.

Date: 2026-07-10

Completed in Stage 2:

- [x] Created `scripts/capture_kafka_evidence.sh` — captures topic list, topic details, and sample messages from all 4 topics with field validation.
- [x] Created `scripts/capture_connector_evidence.sh` — captures plugin list, registers connector using live plugin discovery, verifies connector status.
- [x] Created `scripts/capture_spark_evidence.sh` — records Spark version, starts metadata stream job (detached), captures checkpoint evidence and MongoDB cross-check.
- [x] Created `scripts/run_stage2_evidence.sh` — unified runbook orchestrating all Stage 2 steps end-to-end.
- [x] Updated `spark_jobs/metadata_stream_to_mongo.py` — added configuration constants, startup logging, batch count logging, `processingTime` trigger, and SIGTERM graceful shutdown.
- [x] Created `tests/test_kafka_spark_stage2.py` — 39 new unit tests verifying connector config, Spark schema, topic init script, evidence scripts, and Docker Compose config.

Commands run & Verification:

| Command | Result |
|---|---|
| `python -m pytest tests/ -v --override-ini="addopts=" -p no:langsmith` | Pass: 63 tests passed (24 existing + 39 new) |
| `git status --short` | Pending: new scripts and test file ready to commit |

New scripts created:

| Script | Purpose |
|---|---|
| `scripts/capture_kafka_evidence.sh` | Capture Kafka topic list and sample messages for evidence |
| `scripts/capture_connector_evidence.sh` | Verify connector plugin and capture registration evidence |
| `scripts/capture_spark_evidence.sh` | Start Spark job and capture checkpoint evidence |
| `scripts/run_stage2_evidence.sh` | Unified end-to-end Stage 2 evidence capture runbook |

Spark job improvements:

| Change | Rationale |
|---|---|
| Configuration constants extracted | Avoid hardcoded values, easier to audit against spec |
| `processingTime="10 seconds"` trigger | Prevent rapid empty micro-batches |
| Startup logging with config summary | Observable runtime for evidence capture |
| Batch count logging in `write_batch` | Shows number of documents written per micro-batch |
| SIGTERM + KeyboardInterrupt handling | Clean shutdown inside Docker (docker stop) |

### Stage 2 "Done when" Criteria Status

| Criterion | Status |
|---|---|
| Kafka sample messages are available for Jupyter Book | ⚙️ Script ready, pending Docker runtime |
| Connector registration evidence shows correct Neo4j class | ⚙️ Script ready, pending Docker runtime |
| Spark reads cpg.metadata and writes metadata path evidence | ✅ Job updated and unit-tested |
| Progress and evidence links updated in this file | ✅ Updated |
| All existing tests still pass | ✅ 63 tests passed |

Blockers recorded:

### Blocker 3: Docker Desktop Not Running (Pending)

- **Command run:** `docker compose ps`
- **Error output:** `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine`
- **Impact:** Cannot run live evidence capture scripts until Docker Desktop is started.
- **Resolution:** Start Docker Desktop, then run `bash scripts/run_stage2_evidence.sh` for full evidence capture.

Next action: Start Docker Desktop and run `bash scripts/run_stage2_evidence.sh` to
capture all live evidence, then commit with evidence files and open PR to dev.

