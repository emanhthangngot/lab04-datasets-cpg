# Tasks: Stage 2 Team Handoff

## 1. Truc - Kafka/Spark Runtime

- [ ] 1.1 Read `openspec/specs/kafka-spark/spec.md`.
- [ ] 1.2 Run `git status --short`, `bash scripts/run_checks.sh`, and
  `docker compose config` before editing.
- [ ] 1.3 Verify Kafka topics with `bash scripts/init_kafka_topics.sh`.
- [ ] 1.4 Verify Kafka Connect plugin class with
  `bash scripts/check_connect_plugins.sh`.
- [ ] 1.5 Start Spark metadata stream through
  `docker compose exec spark spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.mongodb.spark:mongo-spark-connector_2.12:10.3.0 /app/spark_jobs/metadata_stream_to_mongo.py`.
- [ ] 1.6 Capture Kafka topic list, sample messages, and Spark checkpoint
  evidence.
- [ ] 1.7 Update `docs/team/kafka-spark.md` with commands, outputs, evidence
  links, and blockers.

## 2. Thanh - Neo4j/MongoDB Stores

- [ ] 2.1 Read `openspec/specs/graph-stores/spec.md`.
- [ ] 2.2 Run `git status --short`, `bash scripts/run_checks.sh`, and
  `docker compose config` before editing.
- [ ] 2.3 Apply Neo4j constraints using the local lab credentials configured in
  `docker-compose.yml`.
- [ ] 2.4 Verify Neo4j node and relationship counts after sample ingestion.
- [ ] 2.5 Verify Neo4j duplicate node ID and edge ID queries.
- [ ] 2.6 Verify MongoDB metadata count and duplicate `file_id` aggregation.
- [ ] 2.7 During replay work, run `bash scripts/wait_neo4j_connector_idle.sh`
  before stale cleanup.
- [ ] 2.8 Update `docs/team/graph-stores.md` with query outputs, evidence
  links, and blockers.

## 3. Tuan - Evidence/Jupyter Book

- [ ] 3.1 Read `openspec/specs/evidence-book/spec.md`.
- [ ] 3.2 Run `git status --short`, `bash scripts/run_checks.sh`, and
  `docker compose config` before editing.
- [ ] 3.3 Verify book chapters map to Lab04 tasks 1 through 6.
- [ ] 3.4 Verify notebooks and screenshot folders exist for Kafka, Neo4j,
  MongoDB, Spark, and replay evidence.
- [ ] 3.5 Add only real command/notebook/query output or screenshots.
- [ ] 3.6 Run `jupyter-book build book/` when `jupyter-book` is installed.
- [ ] 3.7 Review notebooks and screenshots for credentials or irrelevant
  personal data before asking Tri for final review.
- [ ] 3.8 Update `docs/team/evidence-book.md` with evidence links and blockers.

## 4. Tri - Review Gate

- [ ] 4.1 Confirm each owner updated their tracker.
- [ ] 4.2 Confirm PRs list commands run and evidence captured.
- [ ] 4.3 Confirm schema fields and connector classes did not drift.
- [ ] 4.4 Confirm no credentials or private data were added.
- [ ] 4.5 Merge only after the relevant checks pass.
