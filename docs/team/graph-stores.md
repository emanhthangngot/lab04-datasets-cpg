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

- [ ] Verify Neo4j service starts with configured credentials and heap settings.
- [ ] Verify node uniqueness constraint can be applied.
- [ ] Verify MongoDB service is reachable.
- [ ] Record any credential, plugin, or Docker blocker for Tri.

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

Status: Not started

Next action: Wait for Stage 1 task assignment from Tri.

Evidence links: None yet.

Blockers: None reported.
