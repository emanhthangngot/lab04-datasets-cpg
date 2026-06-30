# Lab04 Team Workplan

Final submission: `https://emanhthangngot.github.io/lab04-datasets-cpg/`

The Moodle submission is exactly one text entry: the root URL of the published
Jupyter Book. The repository behind that site must remain public and contain all
source code, notebooks, screenshots, and meaningful commit history.

## Roster And Ownership

| Student | Role | Progress File | Responsibility |
|---|---|---|---|
| 23120099 - Le Xuan Tri | Lead + Spec Owner + Parser/Schema Owner | `docs/team/workplan.md` | Write all specs, assign tasks, review PRs, control merges, own parser/schema/test gates |
| 23120180 - Tran Le Trung Truc | Kafka/Spark Runtime | `docs/team/kafka-spark.md` | Kafka topics, Kafka samples, Kafka Connect operations, Spark metadata stream |
| 23120166 - Tran Huu Kim Thanh | Graph Stores | `docs/team/graph-stores.md` | Neo4j sink, Cypher checks, MongoDB metadata verification |
| 23120185 - Nguyen Ho Anh Tuan | Evidence/Jupyter Book | `docs/team/evidence-book.md` | Notebooks, screenshots, Jupyter Book chapters, final evidence |

## Task Intake

1. Tri writes or updates the spec for the stage.
2. Tri assigns tasks in this workplan.
3. Each member branches from `dev`, implements only assigned work, and updates
   their progress file.
4. Each member opens a PR back to `dev`.
5. Tri reviews implementation, evidence, and progress tracker before merge.
6. Final stage merges `dev` into `main`, which publishes the Jupyter Book.

## Stage Timeline

| Stage | Dates | Goal | Exit Condition |
|---|---:|---|---|
| Stage 1 | 2026-07-01 to 2026-07-07 | Public repo, workflow docs, baseline specs, infra scaffold, parser discovery/schema baseline | Repo public, `dev` ready, team trackers ready, scaffold checks pass |
| Stage 2 | 2026-07-08 to 2026-07-14 | Core sample pipeline: parser -> Kafka -> Neo4j/MongoDB | Node counts, Kafka samples, Neo4j and MongoDB query outputs exist |
| Stage 3 | 2026-07-15 to 2026-07-22 | Replay and evidence hardening | Six task chapters have executed outputs, screenshots, and reflection notes |
| Stage 4 | 2026-07-23 to 2026-07-25 | Final review, merge `dev` to `main`, publish Pages | GitHub Pages URL opens the latest final Jupyter Book |

## Lead Checklist

### Stage 1

- [ ] Confirm GitHub public repo and `dev` branch.
- [ ] Lock schema v1.0 before writing specs.
- [ ] Document JSON Schema contract for `cpg.nodes`, `cpg.edges`, `cpg.metadata`, and `cpg.errors`.
- [ ] Standardize error events on `status = "failed"`.
- [ ] Standardize `CALL_UNRESOLVED` as a deterministic external placeholder target.
- [ ] Write baseline spec for parser, Kafka topics, store contracts, replay, and evidence after schema lock.
- [ ] Verify `bash scripts/run_checks.sh` passes.
- [ ] Assign initial tasks to Truc, Thanh, and Tuan.

### Stage 2

- [ ] Review parser/schema output before downstream ingestion.
- [ ] Review Kafka/Spark sample evidence.
- [ ] Review Neo4j/MongoDB sample evidence.
- [ ] Ensure sample outputs are captured in notebooks.

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
| Parser/schema/specs | Tri | Not started | Stage 1 baseline spec |
| Kafka/Spark | Truc | Not started | Stage 1 infra readiness |
| Neo4j/MongoDB | Thanh | Not started | Stage 1 store readiness |
| Evidence/Jupyter Book | Tuan | Not started | Stage 1 book skeleton review |

## Blocker Policy

If Docker, Kafka, Spark, Neo4j, MongoDB, or publishing is blocked for more than
two hours, report it to Tri the same day with:

- Command run.
- Error output.
- Files changed.
- What was tried.
- What decision is needed.
