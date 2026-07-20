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
- [x] Review Kafka/Spark sample evidence.
- [x] Review Neo4j/MongoDB sample evidence.
- [x] Ensure sample outputs are captured in notebooks.

### Shared E2E Verification Gate

- Truc may execute the shared end-to-end Neo4j/MongoDB checks from the Kafka/Spark runbook.
- Thanh rechecks and accepts those Graph Stores outputs against tasks 2.3–2.6.
- Tri merges only after Thanh records approval or a blocker.

### Stage 3

- [x] Review replay strategy and duplicate checks.
- [x] Confirm each task chapter has real executed output.
- [x] Confirm screenshots are stored under `screenshots/`.
- [x] Resolve the remaining Windows PowerShell/Docker Desktop smoke check before final freeze.
- [x] Tuan book acceptance: post-merge acceptance PR approved 2026-07-20.
- [x] Tri final acceptance: all owner PRs reviewed, final gates passed, and
  Stage 3 accepted on 2026-07-20.

Stage 3 change package:
[`stage3-replay-hardening`](../../openspec/changes/archive/2026-07-20-stage3-replay-hardening/README.md)
(archived after final acceptance).

| Owner | Branch | Deliverable | Acceptance owner |
|---|---|---|---|
| Tri | `feature/tri/stage3-replay-hardening` | OpenSpec, replay contracts, strict manifest validator, final gate | Tri |
| Thanh | `fix/thanh/stage3-replay-stores` | Three-phase Neo4j/Mongo evidence, stale cleanup, two UI screenshots | Tri |
| Truc | `feature/truc/stage3-replay-runtime` | Clean orchestrator, Kafka deltas, Spark restart proof, Windows wrapper | Thanh for stores; Tri final |
| Tuan | `docs/tuan/stage3-replay-book` | Canonical Task 6 notebook, six executed chapters, Reflection, local build | Tri |

Implementation merge order: contracts/store helpers, runtime, canonical
evidence, then book.

Post-merge acceptance order:

1. `test/truc/stage3-windows-acceptance` — Windows runtime record.
2. `review/thanh/stage3-store-acceptance` — committed store evidence approval.
3. `review/tuan/stage3-book-acceptance` — committed book approval.

Each branch starts from the latest `origin/dev` and returns through a separate
PR into `dev`. Tri records Stage 3 acceptance and archives OpenSpec only after
all three acceptance PRs merge. Main merge and Pages remain Stage 4.

Final Stage 3 acceptance recorded by Le Xuan Tri on 2026-07-20:

- Truc Windows runtime acceptance: PR #15 merged.
- Thanh store evidence acceptance: PR #17 merged.
- Tuan book acceptance: PR #18 merged as `7f48c7c`.
- Strict replay manifest: pass.
- OpenSpec strict validation: 5/5 pass.
- Full Python tests, Compose/connector validation, Bash syntax, and clean
  Jupyter Book build: pass.
- Stage 3 result: `APPROVED`. Stage 4 remains separate.

### Stage 4

Stage 4 follows the single-executor checklist in
[`stage4-final-publication`](../../openspec/changes/stage4-final-publication/tasks.md).
These release items remain pending until local gates, deployment, and live-site
acceptance all pass.

- [ ] Run local checks and `jupyter-book build book/`.
- [ ] Merge `dev` into `main`.
- [ ] Confirm GitHub Pages workflow passes.
- [ ] Open every chapter from the Pages URL.
- [ ] Submit only the Pages root URL to Moodle.

## Current Status

| Area | Owner | Status | Next Checkpoint |
|---|---|---|---|
| Parser/schema/specs | Tri | Strict Stage 3 manifest passes; schema v1.0 unchanged | Stage 4 main merge |
| Kafka/Spark | Truc | Windows acceptance complete; baseline 5, restart 5, replay 6; Kafka delta 23/16/1/0 | Stage 4 main merge |
| Neo4j/MongoDB | Thanh | Three-phase replay passed; stale 3/2 removed; duplicates 0; store acceptance APPROVED | Stage 4 main merge |
| Evidence/Jupyter Book | Tuan | Stage 3 book acceptance APPROVED 2026-07-20; all 6 chapters executed; local build clean | Stage 4 Pages review |

## Blocker Policy

If Docker, Kafka, Spark, Neo4j, MongoDB, or publishing is blocked for more than
two hours, report it to Tri the same day with:

- Command run.
- Error output.
- Files changed.
- What was tried.
- What decision is needed.
