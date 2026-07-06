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

- Receive tasks only from `docs/team/workplan.md`.
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

- [ ] Verify Neo4j receives `cpg.nodes` and `cpg.edges` through Kafka Connect.
- [ ] Capture Neo4j node and edge counts.
- [ ] Verify MongoDB receives file metadata from Spark.
- [ ] Capture MongoDB document count and sample document.

Done when:

- Neo4j graph topology exists for sample parser output.
- MongoDB metadata exists for sample parser output.
- Counts and sample query outputs are ready for book evidence.

Spec input to Tri:

- Any Cypher merge behavior that risks duplicates.
- Any metadata field needed by the final report.

## Stage 3: Replay And Duplicate Checks

Tasks:

- [ ] Run Neo4j duplicate checks after replay.
- [ ] Run MongoDB duplicate `file_id` checks after replay.
- [ ] Verify stale cleanup behavior with `run_id`.
- [ ] Provide outputs for Task 4, Task 5, and Task 6.

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

## Latest Update

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
- MongoDB ping returned `{ ok: 1 }`.

Next action: Wait for Stage 2 sample ingestion, then capture Neo4j node/edge
counts and MongoDB metadata evidence.

Evidence links: Command outputs captured in the local terminal session.

Blockers:

- Full `docker compose up -d` currently fails because Docker cannot resolve
  `docker.io/bitnami/spark:3.5.0`. Stage 1 store checks were completed by
  starting only the relevant services: `broker neo4j mongo connect`.
- On this workstation, PowerShell resolves plain `bash` to the WSL launcher,
  but WSL has no installed distribution. Git Bash was used explicitly from
  `C:\Program Files\Git\bin\bash.exe`.
- Initial `scripts/check_connect_plugins.sh` execution under Git Bash resolved
  `python3` to the WindowsApps shim and failed with permission denied. The
  script now follows the same Python selection pattern as `run_checks.sh`.
