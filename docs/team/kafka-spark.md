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

- Receive tasks only from `docs/team/workplan.md`.
- Implement from specs written by Le Xuan Tri.
- Do not create or edit spec files.
- Update this tracker before asking for PR review.
- Attach command output or screenshot references when a task affects evidence.

## Stage 1: Runtime Foundation

Tasks:

- [x] Verify Kafka broker and topic scripts run inside Docker Compose.
- [x] Verify Kafka Connect service exposes the Neo4j connector plugin (Verified Neo4j Connector 5.1.0 plugin is available).
- [x] Verify Spark container can run `spark-submit` (Resolved by replacing missing `bitnami/spark:3.5.0` with `bitnamilegacy/spark:3.5.0` and running Spark as a client container).
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

- [ ] Capture Kafka topic list evidence.
- [ ] Capture sample messages from `cpg.nodes`, `cpg.edges`, `cpg.metadata`, and `cpg.errors`.
- [ ] Run Spark metadata stream on sample parser output.
- [ ] Capture Spark checkpoint evidence.

Done when:

- Kafka sample messages are available for the Jupyter Book.
- Spark can read `cpg.metadata` from Kafka and write metadata path evidence.
- Progress and evidence links are updated in this file.

Spec input to Tri:

- Sample message fields that differ from expected schema.
- Spark failure modes or checkpoint behavior.

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

Status: Stage 1 foundation complete; Spark image blocker resolved on `fix/truc/spark-image-runtime`.

Date: 2026-07-06

Completed in Stage 1:

- [x] Verified Kafka broker starts and is healthy under Docker Compose.
- [x] Resolved CRLF line endings on scripts, and verified `scripts/init_kafka_topics.sh` successfully creates topics `cpg.nodes`, `cpg.edges`, `cpg.metadata`, `cpg.errors` inside the broker.
- [x] Verified Kafka Connect starts successfully and exposes `org.neo4j.connectors.kafka.sink.Neo4jConnector` (version 5.1.0).
- [x] Documented Spark Structured Streaming submit command syntax and package dependencies.
- [x] Resolved runtime blocker regarding Spark image availability.

Commands run & Verification:

| Command | Result |
|---|---|
| `git status --short --branch` | Pass: on `fix/truc/spark-image-runtime` with Spark runtime fixes only |
| `python -m pytest -q --override-ini="addopts=" -p no:langsmith` | Pass: 17 tests passed |
| `docker compose up -d broker neo4j mongo connect` | Pass: containers started and are healthy |
| `docker compose up -d spark` | Pass: pulled `bitnamilegacy/spark:3.5.0` and started `lab04-spark` |
| `docker compose exec -T spark which spark-submit` | Pass: returned `/opt/bitnami/spark/bin/spark-submit` |
| `docker compose exec -T spark spark-submit --version` | Pass: Spark 3.5.0, Scala 2.12.18, OpenJDK 17.0.10 |
| `docker compose up -d` | Pass: full Docker Compose command completes after Spark image replacement |
| `bash scripts/init_kafka_topics.sh` | Pass: successfully created all four topics inside broker |
| `docker compose exec broker kafka-topics --bootstrap-server broker:9092 --list` | Pass: returned `cpg.edges`, `cpg.errors`, `cpg.metadata`, `cpg.nodes` |
| `bash scripts/check_connect_plugins.sh` | Pass: verified Neo4j sink connector class `org.neo4j.connectors.kafka.sink.Neo4jConnector` (5.1.0) |

### Spark Command Syntax & Package Requirements
The Structured Streaming metadata ingestion job will be submitted using:
```bash
docker compose exec spark spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.mongodb.spark:mongo-spark-connector_2.12:10.3.0 \
  /app/spark_jobs/metadata_stream_to_mongo.py
```
- **Spark Kafka integration**: `org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0` (matching Spark 3.5.0 and Scala 2.12).
- **MongoDB connector**: `org.mongodb.spark:mongo-spark-connector_2.12:10.3.0` (matching Spark 3.5.0 and Scala 2.12).
- **Upsert policy**: Uses `replace` operation on `file_id` (not `_id`) to ensure replay updates existing metadata rather than duplicating.
- **Checkpointing**: Checkpoint path is `/mnt/checkpoints/cpg_metadata` to guarantee replay durability.

Blockers recorded:

### Blocker 1: Spark Docker Image Missing (Resolved)

Per Blocker Policy (`docs/team/workplan.md`):

- **Command run:**
  ```bash
  docker compose pull spark
  ```
- **Error output:**
  ```text
  Image bitnami/spark:3.5.0 Pulling
  Image bitnami/spark:3.5.0 Error
  failed to resolve reference "docker.io/bitnami/spark:3.5.0":
  docker.io/bitnami/spark:3.5.0: not found
  ```
- **Files affected:** `docker-compose.yml` line 94 now uses `image: bitnamilegacy/spark:3.5.0`.
- **What was tried:**
  1. `docker compose pull spark` — fails because `bitnami/spark:3.5.0` no longer exists on Docker Hub.
  2. Verified `docker.io/bitnamilegacy/spark:3.5.0` exists on Docker Hub (manifest confirmed).
  3. Verified `apache/spark:3.5.0` exists on Docker Hub (manifest confirmed).
- **Resolution:** Replaced the missing image with `docker.io/bitnamilegacy/spark:3.5.0`,
  the closest drop-in replacement for the existing Bitnami Spark layout. The
  Spark service now overrides the Bitnami entrypoint with `sleep infinity` so
  the container can be used as a client shell for
  `docker compose exec spark spark-submit ...`.

### Blocker 2: CRLF Line Endings (Resolved locally)

- **Command run:** `bash scripts/init_kafka_topics.sh` on Windows-cloned repo.
- **Error output:** `set: pipefail: invalid option name` (due to CRLF line endings).
- **Files affected:** All `scripts/*.sh` files (local working copies only).
- **What was tried:** Converted all `scripts/*.sh` to LF line endings locally.
- **Resolution:** Scripts already stored as LF in Git index (`git ls-files --eol` confirmed `i/lf`). The CRLF conversion is caused by `core.autocrlf=true` on Windows. No commit needed — local-only fix.

### Stage 1 "Done when" Criteria Status

| Criterion | Status |
|---|---|
| `scripts/init_kafka_topics.sh` can create all required topics | ✅ Verified |
| `scripts/check_connect_plugins.sh` proves Neo4j connector available | ✅ Verified |
| Spark command syntax and package requirements documented | ✅ Documented (see above) |
| Spark Docker runtime functional | Verified with `docker compose up -d spark` and `docker compose exec -T spark spark-submit --version` |

Next action: Proceed to Stage 2 streaming path.
