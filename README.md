# Lab04 CPG Streaming

This project implements the Lab04 Spark Streaming assignment: build an
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

## Implementation Status

The parser, streaming routes, graph and metadata stores, replay workflow, and
six executed evidence chapters are complete. Stage 3 evidence is protected by a
strict hash-validated manifest. Stage 4 publishes the final Jupyter Book from
`main` to GitHub Pages through the repository workflow. Whole-assignment
completion also requires a student to submit this exact root URL to Moodle:

```text
https://emanhthangngot.github.io/lab04-datasets-cpg/
```

Key implementation decisions are encoded in the repository:

- Kafka Connect uses `kafka-connect/Dockerfile` to install the Neo4j connector.
- Spark uses `docker.io/bitnamilegacy/spark:3.5.0` because
  `bitnami/spark:3.5.0` no longer resolves from Docker Hub.
- The Spark Compose service uses `SPARK_MODE=master`; the legacy image rejects
  the old `client` mode.
- The parser runs inside Docker Compose as `parser`, using `broker:9092`.
- `register_neo4j_sink.sh` uses idempotent `PUT /connectors/{name}/config`.
- Connector registration checks `/connector-plugins` and submits the exact
  reported Neo4j sink connector class.
- Schema tests require `properties` to be `{}` instead of `null`.
- Metadata tests require `num_total_edges = cfg + dfg + call`.
- Discovery tests keep `src/datasets/utils` in scope.
- Neo4j constraints include node uniqueness only.

## Quickstart

```bash
# 1. Validate the repository
bash scripts/run_checks.sh
python scripts/stage3_replay_manifest.py validate --root .

# 2. Build the committed evidence book offline
jupyter-book clean book/
jupyter-book build book/
test -f book/_build/html/index.html
```

The publication build consumes committed notebook outputs and screenshots; it
does not require Docker, Kafka, Spark, Neo4j, MongoDB, or a dataset clone.

To reproduce the runtime intentionally, provide the Neo4j password through the
local environment and then start the infrastructure:

```bash
export NEO4J_PASSWORD=<local-lab-password>
docker compose up -d

# 1. Clone the selected repository
bash scripts/clone_repo.sh

# 2. Create Kafka topics
bash scripts/init_kafka_topics.sh

# 3. Check and register Neo4j connector
bash scripts/check_connect_plugins.sh
docker compose exec -T neo4j cypher-shell -u neo4j -p "$NEO4J_PASSWORD" < neo4j/constraints.cypher
bash scripts/register_neo4j_sink.sh

# 4. Start Spark metadata stream
docker compose exec spark spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.mongodb.spark:mongo-spark-connector_2.12:10.3.0 \
  /app/spark_jobs/metadata_stream_to_mongo.py

# 5. Run parser inside Docker network
COMMIT_SHA="$(git -C data/datasets rev-parse HEAD)"
docker compose run --rm -e COMMIT_SHA="$COMMIT_SHA" parser \
  python -m parser_service.main --repo data/datasets --mode full
```

The canonical Stage 3 evidence runner resets Docker state and regenerates
hash-protected artifacts. Do not run it during normal book publication; use it
only when a deliberate new canonical evidence run is required.

On Windows, run the same canonical Bash workflow through the PowerShell
wrapper so Docker Desktop and Git Bash use one implementation:

```powershell
.\scripts\run_stage3_evidence.ps1 `
  -ResetDockerState `
  -Neo4jPassword (Read-Host -AsSecureString)
```

## Evidence Targets

- Task 1: repository clone and Python file discovery counts.
- Task 2: parser service event counts and sample events.
- Task 3: Kafka topic layout and sample messages.
- Task 4: Neo4j node/edge ingestion and duplicate checks.
- Task 5: MongoDB metadata ingestion and checkpoint evidence.
- Task 6: modified-file replay, Spark checkpoint resume, stale cleanup, store
  duplicate checks, and strict manifest evidence.
- Architecture diagram: full parser -> Kafka -> Neo4j/Spark/MongoDB flow.

## Team Workflow

Team workflow, branch rules, commit rules, and evidence requirements are in
`docs/CONTRIBUTING.md`.

## Specs And Release Checklist

Accepted capability specifications live under `openspec/specs/`. The Stage 4
technical publication record is prepared under `openspec/changes/archive/`;
whole-assignment completion still requires the manual Moodle record. Before
changing published content, run:

```bash
git status --short
bash scripts/run_checks.sh
docker compose config
python scripts/stage3_replay_manifest.py validate --root .
```

Then read the accepted specs:

```bash
sed -n '1,220p' openspec/specs/parser-core/spec.md
sed -n '1,220p' openspec/specs/kafka-spark/spec.md
sed -n '1,220p' openspec/specs/graph-stores/spec.md
sed -n '1,220p' openspec/specs/evidence-book/spec.md
sed -n '1,220p' openspec/specs/final-publication/spec.md
```

Stage 4 uses one sequential executor for local checks, final publication, and
live acceptance. Earlier ownership records in `docs/team/` are retained as
Stage 1-3 history. The Moodle submission value is only the verified Pages root
URL.

Use a short-lived branch from `dev` for any post-release fix:

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
bash scripts/register_neo4j_sink.sh
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

The only value to submit on Moodle is the GitHub Pages root URL:

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
