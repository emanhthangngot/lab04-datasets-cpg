# Lab04 Team Workplan

Final submission: `https://emanhthangngot.github.io/lab04-datasets-cpg/`

The Moodle submission is exactly one text entry: the root URL of the published
Jupyter Book. The repository behind that site must remain public and contain all
source code, notebooks, screenshots, and meaningful commit history.

## Roster And Ownership

| Student | Role | Progress File | Responsibility |
|---|---|---|---|
| 23120099 - Le Xuan Tri | Lead + Spec Owner + Parser/Schema Owner | [workplan.md](workplan.md) | Write all specs, assign tasks, review PRs, control merges, own parser/schema/test gates |
| 23120180 - Tran Le Trung Truc | Kafka/Spark Runtime | [kafka-spark.md](kafka-spark.md) | Kafka topics, Kafka samples, Kafka Connect operations, Spark metadata stream |
| 23120166 - Tran Huu Kim Thanh | Graph Stores | [graph-stores.md](graph-stores.md) | Neo4j sink, Cypher checks, MongoDB metadata verification |
| 23120185 - Nguyen Ho Anh Tuan | Evidence/Jupyter Book | [evidence-book.md](evidence-book.md) | Notebooks, screenshots, Jupyter Book chapters, final evidence |

## Task Intake

1. Tri writes or updates the spec for the stage.
2. Tri assigns tasks in this workplan.
3. Each member reads the matching [specs](../../openspec/specs) and
   [tasks.md](../../openspec/changes/archive/stage2-team-handoff/tasks.md).
4. Each member branches from `dev`, implements only assigned work, and updates
   their progress file.
5. Each member opens a PR back to `dev`.
6. Tri reviews implementation, evidence, and progress tracker before merge.
7. Final stage merges `dev` into `main`, which publishes the Jupyter Book.

## Stage Timeline

| Stage | Dates | Goal | Exit Condition |
|---|---:|---|---|
| Stage 1 | 2026-07-01 to 2026-07-07 | Public repo, workflow docs, baseline specs, infra scaffold, parser discovery/schema baseline | Repo public, `dev` ready, team trackers ready, scaffold checks pass |
| Stage 2 | 2026-07-08 to 2026-07-14 | Core sample pipeline: parser -> Kafka -> Neo4j/MongoDB | Parser edge counts, Kafka samples, Neo4j and MongoDB query outputs exist |
| Stage 3 | 2026-07-15 to 2026-07-22 | Replay and evidence hardening | Six task chapters have executed outputs, screenshots, and reflection notes |
| Stage 4 | 2026-07-23 to 2026-07-25 | Final review, merge `dev` to `main`, publish Pages | GitHub Pages URL opens the latest final Jupyter Book |

## Lead Checklist

### Stage 1

- [x] Confirm GitHub public repo and `dev` branch.
- [x] Lock schema v1.0 before writing specs.
- [x] Document JSON Schema contract for `cpg.nodes`, `cpg.edges`, `cpg.metadata`, and `cpg.errors`.
- [x] Standardize error events on `status = "failed"`.
- [x] Include parser error `lineno` and zero-based `col_offset` in the schema.
- [x] Standardize `CALL_UNRESOLVED` as a deterministic external placeholder target.
- [x] Runtime recheck pending: `/connector-plugins` must report
  `org.neo4j.connectors.kafka.sink.Neo4jConnector` before registering the sink.
- [x] Lock Spark MongoDB replace/upsert by `file_id`.
- [x] Write baseline spec for parser, Kafka topics, store contracts, replay, and evidence after schema lock.
- [x] Verify `bash scripts/run_checks.sh` passes.
- [x] Assign initial tasks to Truc, Thanh, and Tuan.

### Stage 2 Assignments

| Owner | Spec | Task Checklist | Tracker |
|---|---|---|---|
| Tri | [parser-core/spec.md](../../openspec/specs/parser-core/spec.md) | [tasks.md](../../openspec/changes/archive/stage2-team-handoff/tasks.md) section 4 | [workplan.md](workplan.md) |
| Truc | [kafka-spark/spec.md](../../openspec/specs/kafka-spark/spec.md) | [tasks.md](../../openspec/changes/archive/stage2-team-handoff/tasks.md) section 1 | [kafka-spark.md](kafka-spark.md) |
| Thanh | [graph-stores/spec.md](../../openspec/specs/graph-stores/spec.md) | [tasks.md](../../openspec/changes/archive/stage2-team-handoff/tasks.md) section 2 | [graph-stores.md](graph-stores.md) |
| Tuan | [evidence-book/spec.md](../../openspec/specs/evidence-book/spec.md) | [tasks.md](../../openspec/changes/archive/stage2-team-handoff/tasks.md) section 3 | [evidence-book.md](evidence-book.md) |

### Stage 2

- [x] Review parser/schema output before downstream ingestion.
- [x] Confirm parser sample emits CFG, DFG, and CALL edges when constructs exist.
- [ ] Review Kafka/Spark sample evidence.
- [ ] Review Neo4j/MongoDB sample evidence.
- [ ] Ensure sample outputs are captured in notebooks.

### Shared E2E Verification Gate

- Truc may execute the shared end-to-end Neo4j/MongoDB checks from the Kafka/Spark runbook.
- Thanh rechecks and accepts those Graph Stores outputs against tasks 2.3–2.6.
- Tri merges only after Thanh records approval or a blocker.

### Stage 3

- [ ] Review replay strategy and duplicate checks.
- [ ] Confirm each task chapter has real executed output.
- [ ] Confirm screenshots are stored under `screenshots/`.
- [ ] Resolve any blocker before final freeze.

### Stage 4

- [ ] Run local checks and `jupyter-book build book/`.
- [ ] Merge `dev` into `main`.
- [ ] Confirm GitHub Pages workflow passes.
- [ ] Open every chapter from the Pages URL.
- [ ] Submit only the Pages root URL to Moodle.

## Current Status

| Area | Owner | Status | Next Checkpoint |
|---|---|---|---|
| Parser/schema/specs | Tri | Schema v1.0 locked; Stage 2 parser-core spec added | Parser sample edge evidence |
| Kafka/Spark | Truc | Assigned from OpenSpec handoff; Spark image decision recorded | Topic, plugin, connector, and Spark evidence |
| Neo4j/MongoDB | Thanh | Assigned from OpenSpec handoff | Neo4j/MongoDB validation evidence |
| Evidence/Jupyter Book | Tuan | Assigned from OpenSpec handoff | Stage 1 book skeleton review |

## Blocker Policy

If Docker, Kafka, Spark, Neo4j, MongoDB, or publishing is blocked for more than
two hours, report it to Tri the same day with:

- Command run.
- Error output.
- Files changed.
- What was tried.
- What decision is needed.
