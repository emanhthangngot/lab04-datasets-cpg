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

## Team Workflow

Team workflow, branch rules, commit rules, and evidence requirements are in
`docs/CONTRIBUTING.md`.

## SDD Task Intake

Stage 2 work follows a lightweight OpenSpec-style SDD workflow. The OpenSpec
CLI is not required; use the files under `openspec/` as the source of truth.

Before starting any assigned task:

```bash
git status --short
bash scripts/run_checks.sh
docker compose config
```

Then read the assigned spec and task checklist:

```bash
# Truc: Kafka/Spark
sed -n '1,220p' openspec/specs/kafka-spark/spec.md
sed -n '1,120p' openspec/changes/stage2-team-handoff/tasks.md

# Thanh: Neo4j/MongoDB
sed -n '1,220p' openspec/specs/graph-stores/spec.md
sed -n '1,180p' openspec/changes/stage2-team-handoff/tasks.md

# Tuan: Evidence/Jupyter Book
sed -n '1,220p' openspec/specs/evidence-book/spec.md
sed -n '1,220p' openspec/changes/stage2-team-handoff/tasks.md
```

Use a short-lived branch from `dev`:

```bash
git switch dev
git pull --ff-only
git switch -c feature/<owner>/<task-name>
```

Domain checks before PR:

```bash
# Kafka/Spark owner
bash scripts/init_kafka_topics.sh
bash scripts/check_connect_plugins.sh
docker compose exec spark spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.mongodb.spark:mongo-spark-connector_2.12:10.3.0 \
  /app/spark_jobs/metadata_stream_to_mongo.py

# Neo4j/MongoDB owner
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=<local-lab-password>
docker compose exec -T neo4j cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" < neo4j/constraints.cypher
bash scripts/wait_neo4j_connector_idle.sh

# Evidence owner
jupyter-book build book/
```

If a domain check needs local credentials or a running service, use the local
lab configuration and record the exact command and output in the matching
tracker. Do not commit credentials, local machine details, or screenshots that
show private information.

PR flow:

1. Read the spec and tasks before coding.
2. Implement only the assigned task slice.
3. Run baseline and domain checks.
4. Update the matching tracker in `docs/team/`.
5. Attach command output, query output, notebook output, or screenshot paths.
6. Open a PR to `dev` for Tri review.

Progress is tracked in:

- `docs/team/workplan.md` for lead/spec ownership and overall status.
- `docs/team/kafka-spark.md` for Kafka/Spark runtime work.
- `docs/team/graph-stores.md` for Neo4j/MongoDB store work.
- `docs/team/evidence-book.md` for notebooks, screenshots, and Jupyter Book work.

The final Moodle submission is the GitHub Pages root URL:

```text
https://emanhthangngot.github.io/lab04-datasets-cpg/
```

## Limitations To State In The Report

- Parser is lab-level, not Joern-equivalent.
- CFG is limited to common Python statement flow.
- DFG is intra-procedural and local-variable focused.
- Call resolution is local-file based and does not fully resolve imports,
  aliases, inheritance, or dynamic dispatch.
- Replay is file-granularity, not function-level incremental diffing.
