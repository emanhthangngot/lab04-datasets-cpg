# Lab04 CPG Streaming Context

## Project Goal

Build the Lab04 Spark Streaming assignment for an incremental Code Property
Graph pipeline over `huggingface/datasets`. The final submission is a public
GitHub Pages Jupyter Book with executed evidence for each task.

## Source Repository

- Upstream repository: `https://github.com/huggingface/datasets`
- Parse scope: `src/datasets/**/*.py`
- Exclude: `tests/**`, `docs/**`, `notebooks/**`, `benchmarks/**`,
  `templates/**`, `__pycache__/**`, and `setup.py`
- Do not exclude `src/datasets/utils/`; it is core library code.

## Architecture

```txt
Repository clone
  -> file discovery
  -> Python ast parser service
  -> Kafka topics
      cpg.nodes      -> Neo4j Kafka Connector Sink -> Neo4j
      cpg.edges      -> Neo4j Kafka Connector Sink -> Neo4j
      cpg.metadata   -> Spark Structured Streaming -> MongoDB
      cpg.errors     -> logs / notebook evidence
```

Spark must not sit between Kafka and Neo4j.

## Required Topics

- `cpg.nodes`
- `cpg.edges`
- `cpg.metadata`
- `cpg.errors`

Create topics explicitly inside the Kafka container with `docker compose exec`.

## Common Event Fields

Every emitted event should include:

- `schema_version`
- `event_time`
- `repo`
- `commit_sha`
- `run_id`
- `file_id`
- `file_path`

Node and edge events must include `op: "upsert"` and `properties` as a map.
Use `{}` when no properties exist.

## Metadata Counts

Metadata must include:

- `num_ast_nodes`
- `num_cfg_edges`
- `num_dfg_edges`
- `num_call_edges`
- `num_total_edges`

Compute `num_total_edges = num_cfg_edges + num_dfg_edges + num_call_edges`
explicitly in the parser process, not as a downstream guess.

## Stable IDs

- `file_id`: stable hash of repository name plus normalized relative path.
- Named nodes: include `file_id`, `scope_path`, node type, and name.
- Assignments: include assignment target and line number.
- Anonymous nodes: include type, line, and column.
- Edges: hash `source_id`, `target_id`, and `edge_type`.

Anonymous node IDs may change after large edits. Replay cleanup handles stale
entities with `file_id + run_id`.

## Docker-Safe Run Order

```bash
docker compose up -d
bash scripts/clone_repo.sh
bash scripts/init_kafka_topics.sh
bash scripts/check_connect_plugins.sh
docker compose exec -T neo4j cypher-shell -u neo4j -p password < neo4j/constraints.cypher
bash scripts/register_neo4j_sink.sh
docker compose exec spark spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.mongodb.spark:mongo-spark-connector_2.12:10.3.0 /app/spark_jobs/metadata_stream_to_mongo.py
python -m parser_service.main --repo data/datasets --mode full
bash scripts/run_replay_demo.sh
jupyter-book build book/
```

Use the exact Spark package version that matches the Spark container version
when the container is not Spark 3.5.0.

## Neo4j Guardrails

- Create only a node uniqueness constraint by default:
  `FOR (n:CPGNode) REQUIRE n.id IS UNIQUE`
- Do not create a relationship uniqueness constraint by default.
- Use `MERGE` for nodes and relationships.
- Use `coalesce(event.properties, {})` in Cypher.
- Wait for the connector consumer group lag to reach zero before stale cleanup.

## MongoDB Guardrails

- Spark consumes only `cpg.metadata`.
- Use a persistent checkpoint path.
- Write metadata with replace/upsert semantics by `file_id`.
- Replay should update a document rather than append duplicates.

## Replay Evidence

Replay must capture:

- modified source file path
- before/after `content_hash`
- before/after `run_id`
- Neo4j node and edge counts for the file
- duplicate node and edge checks
- MongoDB duplicate `file_id` check
- Spark checkpoint existence or resume evidence

## Evidence Checklist

Kafka:

- topic list
- sample messages from each topic
- parser flush behavior

Neo4j:

- node and relationship counts
- duplicate node ID query
- duplicate edge ID query
- placeholder node count

MongoDB:

- metadata count
- duplicate `file_id` aggregation
- updated replay document

Book:

- task chapters 1 through 6
- architecture diagram
- screenshots under `screenshots/`
- reflections on failures and fixes

## Known Runtime-Blocking Fixes

- Run Kafka, Neo4j, and Spark CLI tools through Docker Compose service context.
- Include both Spark Kafka source and MongoDB connector packages.
- Call `producer.flush()` after each file.
- Explicitly create Kafka topics.
- Keep `properties` as `{}` instead of `null`.
- Compute `num_total_edges` explicitly.
- Use `file_id + run_id` for stale replay cleanup.
