# Kafka/Spark Specification

## Purpose

Define the runtime behavior owned by Truc: Kafka topics, Kafka Connect plugin
readiness, Kafka sample evidence, and Spark metadata streaming into MongoDB.

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
