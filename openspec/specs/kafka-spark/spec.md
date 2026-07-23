# Kafka/Spark Specification

## Purpose

Define the runtime behavior owned by Truc: Kafka topics, Kafka Connect plugin
readiness, full-repository Kafka evidence, and Spark metadata streaming into MongoDB.
## Requirements
### Requirement: Kafka Topics Are Explicit

The system SHALL create and use exactly these CPG topics: `cpg.nodes`,
`cpg.edges`, `cpg.metadata`, and `cpg.errors`.

#### Scenario: Topic initialization

- GIVEN Docker Compose infrastructure is running
- WHEN Truc runs `bash scripts/init_kafka_topics.sh`
- THEN all four `cpg.*` topics are created idempotently
- AND topic creation runs through the Kafka service context, not host-only CLI

### Requirement: Kafka Connect Plugin Gate

The runtime MUST verify the Neo4j Kafka Connect sink plugin before registering
the Neo4j connector.

#### Scenario: Plugin class verification

- GIVEN Kafka Connect is reachable at the configured `CONNECT_URL`
- WHEN Truc runs `bash scripts/check_connect_plugins.sh`
- THEN `/connector-plugins` reports
  `org.neo4j.connectors.kafka.sink.Neo4jConnector`
- AND the reported plugin type is `sink`
- AND the connector version is recorded in evidence when available

### Requirement: Spark Consumes Metadata Only

Spark SHALL consume only `cpg.metadata` and write metadata documents to MongoDB.

#### Scenario: Spark submit command

- GIVEN the Spark container image is `docker.io/bitnamilegacy/spark:3.5.0`
- WHEN Truc starts the metadata stream
- THEN the command uses `docker compose exec spark spark-submit`
- AND the Compose service uses `SPARK_MODE=master` so the container remains
  available for `docker compose exec`
- AND includes `org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0`
- AND includes `org.mongodb.spark:mongo-spark-connector_2.12:10.3.0`
- AND the checkpoint path is persistent under `/mnt/checkpoints/cpg_metadata`

### Requirement: Connector Registration Uses Live Plugin Discovery

The Neo4j connector registration MUST use the exact Neo4j sink class reported
by Kafka Connect.

#### Scenario: Register connector

- GIVEN Kafka Connect is reachable at the configured `CONNECT_URL`
- WHEN Truc runs `bash scripts/register_neo4j_sink.sh`
- THEN the script first reads `$CONNECT_URL/connector-plugins`
- AND selects a reported Neo4j sink connector class
- AND submits that class in the connector config PUT request

### Requirement: Kafka Evidence Is Reproducible

The runtime SHALL capture evidence that can be copied into the Jupyter Book.

#### Scenario: Sample messages

- GIVEN parser output has reached Kafka
- WHEN Truc samples `cpg.nodes`, `cpg.edges`, `cpg.metadata`, and `cpg.errors`
- THEN each sample shows `schema_version`, `event_time`, `file_id`, and
  `file_path`
- AND node/edge samples show `properties` as a JSON object
- AND the complete metadata capture contains exactly one event per discovered
  source file

### Requirement: Checkpoint Restart Proves Resume

Stage 3 SHALL restart Spark with the persistent Stage 2 checkpoint before
emitting the replay event.

#### Scenario: Unchanged offsets are skipped

- **GIVEN** Kafka metadata end offset and Spark checkpoint offset both equal
  the discovered source-file count
- **WHEN** Spark restarts with `/mnt/checkpoints/cpg_metadata`
- **THEN** its checkpoint remains at that baseline offset before replay
- **AND** all MongoDB documents remain unchanged
- **WHEN** one replay metadata event is emitted
- **THEN** Kafka and Spark metadata offsets both advance by exactly one

### Requirement: Kafka Replay Is Distinguished From Store Duplication

Kafka graph topics SHALL retain append-only replay events while acceptance uses
unique IDs for pre-cleanup persistence and zero duplicate groups in stores.

#### Scenario: Replay topic deltas

- **WHEN** the modified target emits its current node/edge totals and one metadata event
- **THEN** total topic counts advance by exactly those dynamic values
- **AND** `cpg.errors` does not advance
- **AND** repeated graph IDs across runs do not fail the connector wait gate
- **AND** cleanup cannot start before connector lag is zero

### Requirement: Windows Runtime Acceptance Is Independent

After the implementation PR is merged into `dev`, Truc SHALL open
`test/truc/stage3-windows-acceptance` from the updated `origin/dev` and run the
PowerShell wrapper in a disposable clean Windows clone or worktree with Docker
Desktop and Git Bash. The smoke run SHALL NOT replace canonical replay evidence.

#### Scenario: Windows wrapper acceptance PR

- **WHEN** `scripts/run_stage3_evidence.ps1` completes with exit code 0
- **THEN** the acceptance record reports offsets `N -> N -> N+1`
- **AND** Kafka deltas match the replayed file metadata, with 1 metadata and 0 errors
- **AND** the record confirms the password was not printed and the target source was restored
- **AND** Truc opens a tracker-only acceptance PR into `dev` with `APPROVED`
- **AND** a failed run records a blocker without marking the gate complete
