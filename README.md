# Lab04 CPG Streaming

This project scaffolds the Lab04 Spark Streaming assignment: build an
incremental Code Property Graph (CPG) from `huggingface/datasets`, stream graph
and metadata events through Kafka, persist graph topology in Neo4j, persist file
metadata in MongoDB, and publish evidence as a Jupyter Book.

## Architecture

```text
huggingface/datasets clone
  -> parser_service Python ast parser
  -> Kafka topics
      cpg.nodes, cpg.edges -> Neo4j Kafka Connector -> Neo4j
      cpg.metadata         -> Spark Structured Streaming -> MongoDB
      cpg.errors           -> logs / notebook evidence
```

Spark must not sit between Kafka and Neo4j.

## Scaffold Status

This scaffold intentionally contains TODO comments in each implementation file.
The core runtime and test structure is present so the team can complete one lab
task at a time without losing required evidence.

Key required fixes are encoded in the scaffold:

- Kafka Connect uses `kafka-connect/Dockerfile` to install the Neo4j connector.
- The parser runs inside Docker Compose as `parser`, using `broker:9092`.
- `register_neo4j_sink.sh` uses idempotent `PUT /connectors/{name}/config`.
- Schema tests require `properties` to be `{}` instead of `null`.
- Metadata tests require `num_total_edges = cfg + dfg + call`.
- Discovery tests keep `src/datasets/utils` in scope.
- Neo4j constraints include node uniqueness only.

## Quickstart

```bash
# 1. Validate scaffold
bash .codex/scripts/doctor.sh
bash scripts/run_checks.sh

# 2. Start infrastructure
docker compose up -d

# 3. Clone the selected repository
bash scripts/clone_repo.sh

# 4. Create Kafka topics
bash scripts/init_kafka_topics.sh

# 5. Check and register Neo4j connector
bash scripts/check_connect_plugins.sh
docker compose exec -T neo4j cypher-shell -u neo4j -p password < neo4j/constraints.cypher
bash scripts/register_neo4j_sink.sh

# 6. Start Spark metadata stream
docker compose exec spark spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.mongodb.spark:mongo-spark-connector_2.12:10.3.0 \
  /app/spark_jobs/metadata_stream_to_mongo.py

# 7. Run parser inside Docker network
docker compose run --rm parser python -m parser_service.main --repo data/datasets --mode full

# 8. Capture evidence and build book
jupyter notebook notebooks/
bash scripts/run_replay_demo.sh
jupyter-book build book/
```

## Evidence Targets

- Task 1: repository clone and Python file discovery counts.
- Task 2: parser service event counts and sample events.
- Task 3: Kafka topic layout and sample messages.
- Task 4: Neo4j node/edge ingestion and duplicate checks.
- Task 5: MongoDB metadata ingestion and checkpoint evidence.
- Task 6: idempotent replay evidence.
- Architecture diagram: full parser -> Kafka -> Neo4j/Spark/MongoDB flow.

## Limitations To State In The Report

- Parser is lab-level, not Joern-equivalent.
- CFG is limited to common Python statement flow.
- DFG is intra-procedural and local-variable focused.
- Call resolution is local-file based and does not fully resolve imports,
  aliases, inheritance, or dynamic dispatch.
- Replay is file-granularity, not function-level incremental diffing.
