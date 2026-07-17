## 1. Tri — Spec, Contracts, And Acceptance

- [ ] 1.1 Validate and merge this OpenSpec change before implementation PRs.
- [ ] 1.2 Add failing mutation-contract and strict manifest tests.
- [ ] 1.3 Implement `scripts/stage3_replay_manifest.py` with `write` and
  `validate` commands.
- [ ] 1.4 Add fail-fast checks for metrics, artifact hashes, screenshots,
  credentials, local paths, and pending markers.
- [ ] 1.5 Review every owner tracker and archive the change only after all
  acceptance gates pass.

## 2. Thanh — Neo4j And MongoDB Replay Stores

- [ ] 2.1 Add failing tests for parameterized cleanup ordering and three-phase
  store evidence.
- [ ] 2.2 Harden `neo4j/cleanup_stale.cypher` and implement
  `scripts/capture_replay_store_evidence.sh`.
- [ ] 2.3 Prove 3 stale nodes and 2 stale edges are removed and final duplicate
  groups are zero.
- [ ] 2.4 Prove MongoDB replaces one target document and preserves four
  unchanged documents.
- [ ] 2.5 Capture `neo4j_after_cleanup.png` and `mongodb_after_replay.png` from
  the same live run, then update `docs/team/graph-stores.md`.

## 3. Truc — Kafka, Spark, Cross-Platform Runtime

- [ ] 3.1 Add failing source-contract tests for reset guards, source restore,
  replay target, connector ordering, checkpoint restart, and output isolation.
- [ ] 3.2 Parameterize replay graph-count output without weakening Stage 2.
- [ ] 3.3 Implement `scripts/run_stage3_evidence.sh` and runtime snapshot helpers.
- [ ] 3.4 Implement `scripts/run_stage3_evidence.ps1` as a Git Bash wrapper with
  secure password handling and exit-code propagation.
- [ ] 3.5 Run the canonical clean workflow after code PRs merge, commit sanitized
  raw artifacts, and update `docs/team/kafka-spark.md`.

## 4. Tuan — Task 6 And Final Book Evidence

- [ ] 4.1 Add failing book tests for canonical Task 6, executed outputs, two UI
  images, reflections, and absence of pending markers.
- [ ] 4.2 Replace `book/task6_replay.md` and the duplicate notebook with
  `book/task6_replay.ipynb` backed only by the strict manifest.
- [ ] 4.3 Re-execute Tasks 1 through 6 after the fresh baseline/replay run.
- [ ] 4.4 Complete `book/reflection.md`, build the book locally, and update
  `docs/team/evidence-book.md`.

## 5. Shared Final Gate

- [ ] 5.1 `openspec validate --all --strict` passes.
- [ ] 5.2 Full Python tests, shell syntax, PowerShell syntax, Compose config,
  manifest validation, notebook execution, and Jupyter Book build pass.
- [ ] 5.3 Source clone is clean and no credentials, private paths, or fabricated
  evidence are committed.
- [ ] 5.4 Tri records Stage 3 acceptance; main merge and Pages remain Stage 4.
