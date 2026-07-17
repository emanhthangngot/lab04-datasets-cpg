# Stage 3 Replay Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:executing-plans` to implement this plan task-by-task. Do not
> dispatch subagents unless the user explicitly authorizes delegation.

**Goal:** Produce reproducible Task 6 replay evidence and a locally verified
six-task Jupyter Book.

**Architecture:** Rebuild the accepted five-file baseline, restart Spark from
its persistent checkpoint, replay one deterministic source edit, wait for both
consumers, remove stale graph entities, and validate all evidence through a
strict hash manifest. Notebook execution consumes only committed artifacts.

**Tech Stack:** Bash, PowerShell, Python 3.11+, pytest, Docker Compose, Kafka,
Neo4j 5.20, Spark 3.5, MongoDB 7, Jupyter Book 1.0.3, OpenSpec 1.5.

## Global Constraints

- Preserve schema `1.0`, topic names, dataset commit, and ingestion topology.
- Require explicit local Docker reset approval and never log credentials.
- Fix the replay target and mutation exactly as defined by OpenSpec.
- Leave main merge and Pages publication outside Stage 3.

### Task 1: Stage 3 specification and contracts

- Create and strictly validate the OpenSpec change.
- Add replay-manifest tests first and implement `write`/`validate` until green.
- Add exact target, offset, store, screenshot, safety, and artifact-hash gates.

### Task 2: Store and runtime helpers

- Add failing source-contract tests for store phases, cleanup order, checkpoint
  snapshots, reset guards, source restoration, and Windows forwarding.
- Implement the Neo4j/Mongo capture helper, Kafka/Spark snapshot helper,
  canonical Bash orchestrator, finalizer, and PowerShell wrapper.
- Run focused tests and syntax checks after each helper becomes green.

### Task 3: Book and team delivery

- Add the failing canonical Task 6 book test.
- Replace pending duplicate sources with one manifest-backed notebook and
  complete the final Reflection.
- Update workplan, owner trackers, and mixed-platform commands.

### Task 4: Canonical evidence and verification

- Commit code before running the destructive clean evidence workflow.
- Run the workflow on a Docker-capable machine, capture both UI images, then
  write and validate the strict manifest.
- Execute Task 1-6 notebooks, build the book, run all checks, inspect the diff,
  and prepare the implementation PR for review. Implementation completion does
  not constitute owner acceptance and does not authorize OpenSpec archival.

### Task 5: Post-merge owner acceptance and archive

- After the implementation PR merges into `dev`, Truc creates the tracker-only
  `test/truc/stage3-windows-acceptance` PR from the latest `origin/dev`, runs
  the disposable Windows wrapper check, and records `APPROVED` or `BLOCKED`.
- After Truc's PR merges, Thanh creates the tracker-only
  `review/thanh/stage3-store-acceptance` PR from the latest `origin/dev`,
  independently checks the manifest, raw JSON, and database UI evidence, and
  records `APPROVED` or `BLOCKED` without changing expected counts.
- After Thanh's PR merges, Tuan creates the tracker-only
  `review/tuan/stage3-book-acceptance` PR from the latest `origin/dev`, performs
  a clean six-task book build without live Docker services, and records
  `APPROVED` or `BLOCKED`.
- Tri reviews the three merged acceptance records, confirms each is
  `APPROVED`, closes the shared acceptance gate, and only then archives the
  Stage 3 OpenSpec change.
- Merging `dev` into `main` and validating GitHub Pages remain Stage 4 work and
  are not part of any Stage 3 acceptance PR.
