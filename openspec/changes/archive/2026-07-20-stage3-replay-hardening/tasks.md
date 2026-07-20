## 1. Tri — Spec, Contracts, And Acceptance

- [x] 1.1 Validate and merge this OpenSpec change before implementation PRs.
- [x] 1.2 Add failing mutation-contract and strict manifest tests.
- [x] 1.3 Implement `scripts/stage3_replay_manifest.py` with `write` and
  `validate` commands.
- [x] 1.4 Add fail-fast checks for metrics, artifact hashes, screenshots,
  credentials, local paths, and pending markers.
- [x] 1.5 Review every owner tracker and archive the change only after all
  acceptance gates pass.

## 2. Thanh — Neo4j And MongoDB Replay Stores

- [x] 2.1 Add failing tests for parameterized cleanup ordering and three-phase
  store evidence.
- [x] 2.2 Harden `neo4j/cleanup_stale.cypher` and implement
  `scripts/capture_replay_store_evidence.sh`.
- [x] 2.3 Prove 3 stale nodes and 2 stale edges are removed and final duplicate
  groups are zero.
- [x] 2.4 Prove MongoDB replaces one target document and preserves four
  unchanged documents.
- [x] 2.5 Capture `neo4j_after_cleanup.png` and `mongodb_after_replay.png` from
  the same live run, then update `docs/team/graph-stores.md`.

## 3. Truc — Kafka, Spark, Cross-Platform Runtime

- [x] 3.1 Add failing source-contract tests for reset guards, source restore,
  replay target, connector ordering, checkpoint restart, and output isolation.
- [x] 3.2 Parameterize replay graph-count output without weakening Stage 2.
- [x] 3.3 Implement `scripts/run_stage3_evidence.sh` and runtime snapshot helpers.
- [x] 3.4 Implement `scripts/run_stage3_evidence.ps1` as a Git Bash wrapper with
  secure password handling and exit-code propagation.
- [x] 3.5 Run the canonical clean workflow after code PRs merge, commit sanitized
  raw artifacts, and update `docs/team/kafka-spark.md`.

## 4. Tuan — Task 6 And Final Book Evidence

- [x] 4.1 Add failing book tests for canonical Task 6, executed outputs, two UI
  images, reflections, and absence of pending markers.
- [x] 4.2 Replace `book/task6_replay.md` and the duplicate notebook with
  `book/task6_replay.ipynb` backed only by the strict manifest.
- [x] 4.3 Re-execute Tasks 1 through 6 after the fresh baseline/replay run.
- [x] 4.4 Complete `book/reflection.md`, build the book locally, and update
  `docs/team/evidence-book.md`.

## 5. Post-Merge Owner Acceptance

- [x] 5.1 Truc opens `test/truc/stage3-windows-acceptance` from updated
  `origin/dev`, records the Windows Docker Desktop/Git Bash smoke result, and
  merges its tracker-only PR into `dev`.
- [x] 5.2 After 5.1 merges, Thanh opens
  `review/thanh/stage3-store-acceptance`, independently approves the committed
  store manifest/artifacts, and merges its tracker-only PR into `dev`.
- [x] 5.3 After 5.2 merges, Tuan opens `review/tuan/stage3-book-acceptance`,
  approves the committed Task 1-6 book from a clean local build, and merges its
  tracker-only PR into `dev`.

## 6. Shared Final Gate

- [x] 6.1 `openspec validate --all --strict` passes.
- [x] 6.2 Full Python tests, shell syntax, PowerShell syntax, Compose config,
  manifest validation, notebook execution, and Jupyter Book build pass.
- [x] 6.3 Source clone is clean and no credentials, private paths, or fabricated
  evidence are committed.
- [x] 6.4 After all three acceptance PRs merge, Tri reviews their tracker
  records, records Stage 3 acceptance, and archives this change. Main merge and
  Pages remain Stage 4.
