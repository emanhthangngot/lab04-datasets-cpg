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

- Kafka sample messages are available for the Jupyter Book. — ✅ Evidence: [sample_cpg_nodes.json](../../screenshots/kafka/sample_cpg_nodes.json), [sample_cpg_edges.json](../../screenshots/kafka/sample_cpg_edges.json), [sample_cpg_metadata.json](../../screenshots/kafka/sample_cpg_metadata.json), [sample_cpg_errors.json](../../screenshots/kafka/sample_cpg_errors.json).
- Connector registration evidence shows the same Neo4j sink class reported by
  Kafka Connect. — ✅ Evidence: [connector_plugins.json](../../screenshots/kafka/connector_plugins.json), [connector_status.json](../../screenshots/kafka/connector_status.json).
- Spark can read `cpg.metadata` from Kafka and write metadata path evidence. — ✅ Evidence: [checkpoint_listing.txt](../../screenshots/spark/checkpoint_listing.txt), [checkpoint_offsets.txt](../../screenshots/spark/checkpoint_offsets.txt), [mongodb_metadata_check.txt](../../screenshots/spark/mongodb_metadata_check.txt).
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

Stage 3 adds these exact gates:

- [ ] Rebuild the five-file baseline with metadata offset 5.
- [ ] Restart Spark with the same checkpoint and prove the offset remains 5.
- [ ] Replay only `src/datasets/__init__.py` and prove metadata advances to 6.
- [ ] Record Kafka deltas of 23 node, 16 edge, 1 metadata, and 0 error events.
- [ ] Run the PowerShell wrapper smoke check on Windows with Docker Desktop and
  Git Bash.

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

Status: Stage 2 clean-run implementation, store acceptance, and notebook evidence complete.

Date: 2026-07-16

Completed in Stage 2:

- [x] Created `scripts/capture_kafka_evidence.sh` — captures topic list, topic details, and sample messages from all 4 topics with field validation.
- [x] Created `scripts/capture_connector_evidence.sh` — captures plugin list, registers connector using live plugin discovery, verifies connector status.
- [x] Created `scripts/capture_spark_evidence.sh` — records Spark version, starts metadata stream job (detached), captures checkpoint evidence and MongoDB cross-check.
- [x] Created `scripts/run_stage2_evidence.sh` — unified runbook orchestrating all Stage 2 steps end-to-end.
- [x] Updated `spark_jobs/metadata_stream_to_mongo.py` — added configuration constants, startup logging, batch count logging, `processingTime` trigger, and SIGTERM graceful shutdown.
- [x] Created `tests/test_kafka_spark_stage2.py` — 39 new unit tests verifying connector config, Spark schema, topic init script, evidence scripts, and Docker Compose config.
- [x] Created `data/invalid_syntax.py` — intentional SyntaxError file for generating `cpg.errors` evidence events.

### Stage 2 "Done when" Criteria Status

| Criterion | Status |
|---|---|
| Kafka sample messages are available for Jupyter Book | ✅ Evidence captured: [screenshots/kafka/](../../screenshots/kafka/) |
| Connector registration evidence shows correct Neo4j class | ✅ Evidence captured: [connector_plugins.json](../../screenshots/kafka/connector_plugins.json) |
| Spark reads cpg.metadata and writes metadata path evidence | ✅ Checkpoint offset committed and MongoDB contains 5 metadata documents |
| Progress and evidence links updated in this file | ✅ Updated |
| All existing tests still pass | ✅ Full verification recorded in the Stage 2 PR |

### Latest Runtime Recheck

The clean Docker run used `RESET_DOCKER_STATE=1` and verified Kafka sample
contracts, a RUNNING Neo4j connector, Neo4j ingestion (22,628 nodes, 21,415
non-placeholder nodes, 7,968 edges, 1,213 placeholders, no duplicate
nodes/edges), a committed Spark checkpoint at metadata offset 5, and 5 MongoDB
metadata documents with no duplicate `file_id`. All sampled events carry the
real dataset commit `41adfd0f9ee9ba3a6b4f719d5b551c5b19ae45e2`; the validated
manifest is [stage2_manifest.json](../../screenshots/stage2_manifest.json).

### Baseline Checks (task 1.2)

> **Note**: `git status --short`, `bash scripts/run_checks.sh`, and
> `docker compose config` were not captured before initial editing (missed step).
> They have been re-run below to verify current state passes all checks.

| Command | Result |
|---|---|
| `git status --short` | Clean working tree (all changes committed) |
| `bash scripts/run_checks.sh` | Pass: pytest 96 passed; Docker Compose syntax valid; JSON connector config valid |
| `docker compose config --quiet` | Pass: no errors |
| `pytest tests/ -q --override-ini="addopts=" -p no:langsmith` | Pass: 96 tests passed after remediation contracts |

### Scripts Created

| Script | Purpose |
|---|---|
| [capture_kafka_evidence.sh](../../scripts/capture_kafka_evidence.sh) | Capture Kafka topic list and sample messages for evidence |
| [capture_connector_evidence.sh](../../scripts/capture_connector_evidence.sh) | Verify connector plugin and capture registration evidence |
| [capture_spark_evidence.sh](../../scripts/capture_spark_evidence.sh) | Start Spark job and capture checkpoint evidence |
| [run_stage2_evidence.sh](../../scripts/run_stage2_evidence.sh) | Unified end-to-end Stage 2 evidence capture runbook |

### Spark Job Improvements

| Change | Rationale |
|---|---|
| Configuration constants extracted | Avoid hardcoded values, easier to audit against spec |
| `processingTime="10 seconds"` trigger | Prevent rapid empty micro-batches |
| Startup logging with config summary | Observable runtime for evidence capture |
| Batch count logging in `write_batch` | Shows number of documents written per micro-batch |
| SIGTERM + KeyboardInterrupt handling | Clean shutdown inside Docker (docker stop) |

### Evidence Artifacts

| Artifact | Location |
|---|---|
| Kafka topic list | [topic_list.txt](../../screenshots/kafka/topic_list.txt) |
| Kafka topic details | [topic_details.txt](../../screenshots/kafka/topic_details.txt) |
| Sample cpg.nodes | [sample_cpg_nodes.json](../../screenshots/kafka/sample_cpg_nodes.json) |
| Sample cpg.edges | [sample_cpg_edges.json](../../screenshots/kafka/sample_cpg_edges.json) |
| Sample cpg.metadata | [sample_cpg_metadata.json](../../screenshots/kafka/sample_cpg_metadata.json) |
| Sample cpg.errors | [sample_cpg_errors.json](../../screenshots/kafka/sample_cpg_errors.json) |
| Connector plugins | [connector_plugins.json](../../screenshots/kafka/connector_plugins.json) |
| Connector status | [connector_status.json](../../screenshots/kafka/connector_status.json) |
| Neo4j sink class | [neo4j_sink_class.txt](../../screenshots/kafka/neo4j_sink_class.txt) |
| Spark version | [spark_version.txt](../../screenshots/spark/spark_version.txt) |
| Spark checkpoint listing | [checkpoint_listing.txt](../../screenshots/spark/checkpoint_listing.txt) |
| Spark committed offsets | [checkpoint_offsets.txt](../../screenshots/spark/checkpoint_offsets.txt) |
| MongoDB metadata check | [mongodb_metadata_check.txt](../../screenshots/spark/mongodb_metadata_check.txt) |

### Scope Note

Steps 4 (Neo4j constraints) and 10 (Neo4j/MongoDB store verification) in
`run_stage2_evidence.sh` overlap with Thanh's scope (tasks 2.3-2.6). They are
included for shared end-to-end runbook completeness. Truc executes the checks;
Thanh rechecks and accepts the resulting Graph Stores evidence before Tri's
merge approval. This execution does not transfer Graph Stores ownership.
