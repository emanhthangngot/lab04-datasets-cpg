# Graph Stores Progress Tracker

Owner: 23120166 - Tran Huu Kim Thanh

Role: Neo4j/MongoDB Graph Stores

Primary branch examples:

```text
feature/thanh/neo4j-constraints
feature/thanh/mongodb-verification
fix/thanh/stale-cleanup
```

## Working Rules

- Receive tasks only from [workplan.md](workplan.md).
- Implement from specs written by Le Xuan Tri.
- Do not create or edit spec files.
- Update this tracker before asking for PR review.
- Attach Cypher, MongoDB shell output, or screenshot references when relevant.

## Stage 1: Store Foundation

Tasks:

- [x] Verify Neo4j service starts with configured credentials and heap settings.
- [x] Verify node uniqueness constraint can be applied.
- [x] Verify MongoDB service is reachable.
- [x] Record any credential, plugin, or Docker blocker for Tri.

Done when:

- Neo4j constraints are applied without relationship uniqueness constraints.
- MongoDB connectivity is verified.
- Store readiness evidence is captured.

Spec input to Tri:

- Any schema mismatch in Neo4j node/edge fields.
- Any MongoDB collection/index requirement.

## Stage 2: Core Store Ingestion

Tasks:

- [x] Verify Neo4j receives `cpg.nodes` and `cpg.edges` through Kafka Connect.
- [x] Capture Neo4j node and edge counts.
- [x] Capture Neo4j duplicate node ID, duplicate edge ID, and placeholder counts.
- [x] Verify MongoDB receives file metadata from Spark.
- [x] Capture MongoDB document count and sample document.
- [x] Capture MongoDB duplicate `file_id` aggregation.

Done when:

- Neo4j graph topology exists for sample parser output.
- MongoDB metadata exists for sample parser output.
- Counts and sample query outputs are ready for book evidence.
- Duplicate-check query outputs are ready for Stage 2 review.

### Shared E2E Evidence Recheck

Truc's Kafka/Spark runbook may execute the Stage 2 store queries so the whole
team can reproduce the pipeline. Thanh remains the acceptance owner and must
recheck the following artifacts before Tri merges Truc's PR:

- `screenshots/neo4j/node_count.txt`, `edge_count.txt`, and `placeholder_count.txt`;
- `screenshots/neo4j/duplicate_nodes.txt` and `duplicate_edges.txt`;
- Neo4j constraints output and the Cypher queries that produced it;
- `screenshots/mongodb/metadata_evidence.txt` and the Spark MongoDB check; and
- the MongoDB duplicate `file_id` aggregation.

Record either approval or a concrete blocker in this tracker.

Spec input to Tri:

- Any Cypher merge behavior that risks duplicates.
- Any metadata field needed by the final report.

## Stage 3: Replay And Duplicate Checks

Tasks:

- [x] Run Neo4j duplicate checks after the canonical Stage 3 replay.
- [x] Run MongoDB duplicate `file_id` checks after the canonical Stage 3 replay.
- [x] Verify stale cleanup behavior with `run_id`.
- [x] Capture before, pre-cleanup, and final store JSON under `screenshots/replay/`.
- [x] Capture Neo4j Browser and Mongo Express replay screenshots.
- [x] Provide final outputs for Task 6.

Done when:

- Replay evidence proves idempotent graph and metadata behavior.
- Duplicate checks are captured for final book chapters.

Spec input to Tri:

- Stale node/edge cleanup risks.
- Any count drift between parser metadata and stores.

## Stage 4: Final Review

Tasks:

- [ ] Re-run final Neo4j and MongoDB verification queries.
- [ ] Confirm screenshots and query outputs still match final text.
- [ ] Review Task 4, Task 5, and replay store evidence in the published book.

Done when:

- Tri approves graph-store evidence for final Pages publication.

## Stage 2 Acceptance Update (2026-07-16)

Status: Stage 2 graph-store clean-run acceptance passed locally; replay remains a separate follow-up.

The earlier Stage 2 evidence is superseded. The old Docker state contained both
`local-sample/datasets` and `huggingface/datasets`, and the old runbook also
started the one-shot parser during `docker compose up` before invoking it again
explicitly. Those two conditions explained the mixed namespace and near-double
counts; they were not separate remote databases.

Clean-run acceptance after `RESET_DOCKER_STATE=1` reset the local
`lab04-datasets-cpg` containers, topics, volumes, and Spark checkpoint:

- Dataset provenance is the real commit
  `41adfd0f9ee9ba3a6b4f719d5b551c5b19ae45e2`; the hash-validated summary is
  `screenshots/stage2_manifest.json`.

- Kafka emitted 21,415 node events with 21,415 unique IDs and 7,968 edge events
  with 7,968 unique IDs. Every consumed graph event used
  `repo=huggingface/datasets`.
- Neo4j persisted 21,415 non-placeholder nodes, 1,213 placeholders, 22,628
  total nodes, and 7,968 relationships. Duplicate node and edge groups were 0.
- MongoDB persisted exactly 5 documents, 5 distinct `file_id` values, 5
  distinct `file_path` values, and only `huggingface/datasets`.
- Spark clean-run checkpoint reached Kafka metadata offset 5 with numeric batch
  commit 0.

Validation: 96 Python tests passed, Docker Compose config parsed, connector
JSON parsed, all shell scripts passed `bash -n`, and
`scripts/run_checks.sh` passed.

Evidence:

- `screenshots/neo4j/node_count.txt`, `non_placeholder_count.txt`,
  `edge_count.txt`, `placeholder_count.txt`, `duplicate_nodes.txt`, and
  `duplicate_edges.txt`;
- `screenshots/mongodb/metadata_evidence.txt`;
- `screenshots/spark/checkpoint_offsets.txt` and `checkpoint_commits.txt` for
  the single clean batch; and
- `screenshots/kafka/sample_cpg_nodes.json`, `sample_cpg_edges.json`,
  `sample_cpg_metadata.json`, and `sample_cpg_errors.json`.

Stage 3 store acceptance update (2026-07-17): the canonical replay removed 3
stale target nodes and 2 stale target edges. Final Neo4j duplicate groups are
zero, MongoDB retains 5 unique documents with four unchanged hashes, both UI
screenshots were inspected, and `screenshots/replay/stage3_replay_manifest.json`
validates with status `pass`.

## Previous Update

Status: Stage 1 store foundation verified on 2026-07-06.

Commands run:

- `git switch dev`
- `git pull --ff-only origin dev`
- `git switch -c feature/thanh/graph-stores-stage1`
- `git status --short --branch`
- `C:\Program Files\Git\bin\bash.exe scripts/run_checks.sh`
- `docker compose config`
- `docker compose up -d`
- `docker compose up -d broker neo4j mongo connect`
- `docker compose ps`
- `C:\Program Files\Git\bin\bash.exe scripts/check_connect_plugins.sh`
- `docker compose exec -T neo4j cypher-shell -u neo4j -p password "RETURN 1 AS ok;"`
- `docker compose exec -T neo4j cypher-shell -u neo4j -p password "CREATE CONSTRAINT cpg_node_id IF NOT EXISTS FOR (n:CPGNode) REQUIRE n.id IS UNIQUE;"`
- `docker compose exec -T neo4j cypher-shell -u neo4j -p password "SHOW CONSTRAINTS;"`
- `docker compose exec -T neo4j printenv NEO4J_server_memory_heap_initial__size NEO4J_server_memory_heap_max__size`
- `docker compose exec -T mongo mongosh --quiet --eval "db.runCommand({ ping: 1 })"`
- Opened Neo4j Browser at `http://localhost:7474` and connected with
  `neo4j://localhost:7687`, username `neo4j`, password from Compose config.

Evidence:

- Baseline checks passed: Python tests `17 passed`, Docker Compose syntax passed,
  and Neo4j connector JSON config parsed successfully.
- Docker Compose config confirms Neo4j credentials `neo4j/password` and heap
  settings `1G` initial, `2G` max.
- Running services for Stage 1: `broker`, `connect`, `mongo`, and `neo4j` are
  healthy.
- Kafka Connect exposes Neo4j sink class
  `org.neo4j.connectors.kafka.sink.Neo4jConnector` version `5.1.0`.
- Neo4j credential check returned `ok = 1`.
- Neo4j heap env inside the container returned `1G` and `2G`.
- Neo4j `SHOW CONSTRAINTS` returned `cpg_node_id`, type `UNIQUENESS`,
  entity `NODE`, label `CPGNode`, property `id`.
- Neo4j Browser UI login succeeded and displayed the connected `neo4j$` prompt.
- MongoDB ping returned `{ ok: 1 }`.

Next action: Wait for Stage 2 sample ingestion, then capture Neo4j node/edge
counts and MongoDB metadata evidence.

Evidence links: Command outputs captured in the local terminal session.

Blockers:

- The previous full Compose blocker was the unavailable
  `docker.io/bitnami/spark:3.5.0` image. Stage 2 now uses
  `docker.io/bitnamilegacy/spark:3.5.0` with `SPARK_MODE=master`; local Spark
  service start and `spark-submit --version` passed.
- On this workstation, PowerShell resolves plain `bash` to the WSL launcher,
  but WSL has no installed distribution. Git Bash was used explicitly from
  `C:\Program Files\Git\bin\bash.exe`.
- Initial `scripts/check_connect_plugins.sh` execution under Git Bash resolved
  `python3` to the WindowsApps shim and failed with permission denied. The
  script now follows the same Python selection pattern as `run_checks.sh`.

## Post-Merge Acceptance PR

This is Thanh's mandatory independent Stage 3 store acceptance. Start only
after Truc's Windows acceptance PR has merged. Review the committed manifest,
raw JSON evidence, and both database UI screenshots independently; this review
must not alter expected counts.

```bash
git switch dev
git pull --ff-only origin dev
git switch -c review/thanh/stage3-store-acceptance
python scripts/stage3_replay_manifest.py validate --root .
```

The tracker-only PR must record all of the following:

- Neo4j before state: 19 target nodes and 15 target edges.
- Neo4j append state: 26 target nodes and 18 target edges.
- Neo4j final replay state: 23 target nodes and 16 target edges.
- Reconciliation removed exactly 3 stale target nodes and 2 stale target
  edges; duplicate-node and duplicate-edge groups are both zero.
- MongoDB still has 5 unique metadata documents, with 4 unchanged hashes and
  zero duplicate `file_id` groups.
- Neo4j Browser and Mongo Express values agree with their corresponding JSON
  artifacts and with the validated manifest.

Acceptance status: `APPROVED` or `BLOCKED`

Recorded acceptance status: `APPROVED`

### Acceptance Record

Date: 2026-07-19

Base commit: `e60e3d0d6d7df1d9a882d67dc8e548177ae9d777`

- `scripts/run_checks.ps1` passed with 130 tests, valid Compose config, and a
  valid Neo4j connector JSON document.
- Strict manifest validation returned `stage=3, status=pass`; OpenSpec strict
  validation passed all five items.
- Neo4j target state progressed from `19/15` before replay to `26/18` before
  cleanup and `23/16` after cleanup. Reconciliation removed exactly 3 stale
  nodes and 2 stale edges.
- Final stale node/edge counts, duplicate node/edge groups, and old-run entity
  count are all zero.
- MongoDB contains 5 unique metadata documents with zero duplicate `file_id`
  groups. Four non-target documents retain their baseline `run_id` and
  `content_hash`; the target document matches replay run
  `stage3-replay-20260717T002053Z` and its replay content hash.
- `neo4j_after_cleanup.png` shows 23 target/replay nodes, 16 target/replay
  edges, and zero stale nodes or edges. `mongodb_after_replay.png` shows the
  matching target `file_id`, replay document, and collection count of 5.
- JSON artifacts, both database UI screenshots, and the strict manifest agree.
  No canonical evidence or acceptance constants were changed.

For `BLOCKED`, identify the mismatching field, expected and actual values,
failing command, and artifact or screenshot path. Do not regenerate evidence or
change the acceptance constants inside this PR.
