# Stage 1 Schema Contract Baseline

Owner: 23120099 - Le Xuan Tri

This is the Stage 1 baseline spec after the schema-first review. The canonical
source of truth is `schemas/cpg-events.schema.json`; this document explains how
downstream work must consume it.

## Locked Contract

- Schema version is `1.0`.
- Kafka topics are `cpg.nodes`, `cpg.edges`, `cpg.metadata`, and `cpg.errors`.
- Kafka key for every event type is `file_id`.
- Every event carries `schema_version`, `event_time`, `repo`, `commit_sha`,
  `run_id`, `file_id`, and `file_path`.
- Node and edge events use `op = "upsert"` and always emit `properties` as a
  JSON object.
- Metadata events use `status = "success"` and compute `num_total_edges` in
  the parser as CFG + DFG + CALL edge counts.
- Error events use `status = "failed"` and include `lineno` plus zero-based
  `col_offset`; unknown location values are `null`.

## Unresolved Calls

`CALL_UNRESOLVED` is a normal edge event. Its `source_id` points to the internal
call-site node and its `target_id` is a deterministic external placeholder ID
in the form `external:<normalized_callee_name>`, for example
`external:numpy.array`.

The parser does not emit an `ExternalSymbol` node. Neo4j may create the target
placeholder through the edge MERGE path, and referential integrity tests must
treat that target as intentional.

## Runtime Locks

- Kafka Connect plugin discovery must call `/connector-plugins`.
- The verified Neo4j sink connector class is
  `org.neo4j.connectors.kafka.sink.Neo4jConnector` from version `5.1.0`.
- Neo4j receives only graph topology from Kafka Connect.
- Spark consumes only `cpg.metadata` and writes MongoDB metadata.
- MongoDB Spark Connector 10.3.0 uses replace/upsert semantics by `file_id`
  through `spark.mongodb.write.operationType = replace` and
  `spark.mongodb.write.idFieldList = file_id`.
- Replay cleanup must wait for the Neo4j connector consumer group lag to reach
  zero before deleting stale nodes or edges for the same `file_id`.

## Stage 2 Handoff

Truc owns Kafka/Spark runtime readiness, Thanh owns Neo4j/MongoDB validation,
and Tuan owns notebook/Jupyter Book evidence. They should not redefine schema
fields, connector class names, ID semantics, or unresolved-call behavior.
