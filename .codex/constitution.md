# Lab04 CPG Streaming Constitution

> Version: 1.0.0
> Source of truth: `docs/plan.md` and the Lab04 assignment PDF.

This file defines non-negotiable rules for the Lab04 CPG Streaming project.
Skills, commands, hooks, and implementation work must conform to it.

## 1. Mission

Build a reproducible educational streaming pipeline that constructs a lab-level
incremental Code Property Graph from `huggingface/datasets` Python source files,
streams graph and metadata events through Kafka, persists graph topology in
Neo4j, persists file metadata in MongoDB, and publishes evidence through a
Jupyter Book.

This project is not a vulnerability scanner, production static-analysis
platform, or generic SaaS application.

## 2. Non-Negotiable Principles

1. **Incremental file processing:** the parser processes one Python file at a
   time and must not require loading the whole repository into memory.
2. **Stable event identity:** every emitted node, edge, and file metadata record
   must have deterministic identifiers suitable for idempotent replay.
3. **Schema discipline:** every event includes `schema_version`, `event_time`,
   repository context, `file_id`, and `file_path`; node and edge `properties`
   are always a map and never `null`.
4. **Explicit Kafka topics:** use `cpg.nodes`, `cpg.edges`, `cpg.metadata`, and
   `cpg.errors`; do not rely on implicit topic auto-creation.
5. **Correct ingestion boundary:** Neo4j receives graph topology directly from
   Kafka Connect; Spark consumes metadata events only and writes MongoDB.
6. **Replay evidence:** modified-file replay must prove no duplicate Neo4j nodes
   or edges, MongoDB replacement/upsert by `file_id`, and checkpointed Spark
   resume behavior.
7. **Evidence-first delivery:** each lab task needs executable notebook output,
   command output, screenshots, or queries that can be cited in the Jupyter Book.

## 3. Tech Stack Guardrails

| Layer | Required / Allowed | Forbidden |
|---|---|---|
| Parser | Python standard library `ast`, small typed helpers, bounded memory | Whole-repo parser state, Joern-only assumptions, unstable random IDs |
| Events | JSON records with version, event time, file and run context | Missing schema version, missing event time, `properties: null` |
| Kafka | Explicit Docker Compose topic creation in Kafka service context | Host-only Kafka CLI assumptions, auto-created topics as the plan |
| Neo4j | Kafka Connector Sink, Cypher `MERGE`, node uniqueness constraint | Spark between Kafka and Neo4j, default relationship uniqueness constraint |
| Spark | Structured Streaming for `cpg.metadata`, checkpointed writes | Spark consuming graph node/edge topology |
| MongoDB | Metadata upsert/replace by `file_id` | Duplicate metadata documents for the same file replay |
| Evidence | Jupyter notebooks, screenshots, Jupyter Book, GitHub Pages | PDF/Word/zip submission as final artifact |

## 4. Working Agreement

- Start from `.codex/context/lab04-cpg.md` before implementing a subsystem.
- Prefer project-specific skills and rules over generic advice.
- Run Docker CLI tools inside the intended service container unless the command
  is explicitly a host-level Docker Compose operation.
- Ask before destructive Git, Docker volume, database cleanup, connector
  registration in shared environments, or publishing actions.
- Do not claim tests, builds, or verification checks passed unless they were
  actually run.
