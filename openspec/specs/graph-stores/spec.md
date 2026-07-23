# Graph Stores Specification

## Purpose

Define the persistence behavior owned by Thanh: Neo4j graph topology ingestion,
MongoDB metadata ingestion checks, and replay-safe duplicate verification.
## Requirements
### Requirement: Neo4j Receives Graph Topology Directly

Neo4j SHALL receive `cpg.nodes` and `cpg.edges` through Kafka Connect without
Spark between Kafka and Neo4j.

#### Scenario: Direct sink topology

- GIVEN Kafka Connect is registered with the verified Neo4j sink class
- WHEN node and edge events are produced
- THEN Neo4j receives graph topology directly from Kafka Connect
- AND Spark is not used for node or edge ingestion

### Requirement: Neo4j Upserts Are Idempotent

Neo4j MUST use `MERGE` for nodes and relationships and only define a node
uniqueness constraint on `CPGNode.id` by default.

#### Scenario: Placeholder endpoints

- GIVEN an edge arrives before one or both endpoint nodes
- WHEN the edge Cypher runs
- THEN missing endpoint nodes are created as placeholder `CPGNode` records
- AND later node events set `placeholder = false`
- AND `coalesce(event.properties, {})` prevents null property maps

### Requirement: MongoDB Metadata Is Replaced By File

MongoDB SHALL store one current metadata document per `file_id`.

#### Scenario: Metadata replay replacement

- GIVEN a file is processed again with a new `run_id`
- WHEN Spark writes the `cpg.metadata` event to MongoDB
- THEN the existing document for the same `file_id` is replaced or upserted
- AND no duplicate metadata documents remain for that `file_id`

### Requirement: Store Evidence Proves No Duplicates

Store verification MUST produce query outputs for node ID, edge ID, and
metadata `file_id` duplicate checks.

#### Scenario: Replay verification

- GIVEN the replay demo has reprocessed one modified file
- WHEN Thanh runs duplicate checks
- THEN Neo4j returns no duplicate node IDs
- AND Neo4j returns no duplicate edge IDs
- AND MongoDB returns no duplicate `file_id` groups

### Requirement: Stage 2 Full-Repository Store Evidence Is Captured

Stage 2 store evidence SHALL prove that every discovered source file reached
Neo4j and MongoDB.

#### Scenario: Full ingestion verification

- GIVEN Stage 2 parser output has been produced to Kafka
- WHEN Thanh verifies the stores
- THEN Neo4j node and relationship counts are captured
- AND MongoDB contains exactly one document per discovered source file
- AND one representative document is captured for readability
- AND placeholder node count is recorded so unresolved-call behavior is visible

### Requirement: Replay Store State Is Captured In Three Phases

Stage 3 SHALL capture store state before replay, after connector ingestion but
before cleanup, and after cleanup.

#### Scenario: Stale graph cleanup

- **GIVEN** the modified target has a new `run_id`
- **WHEN** connector lag reaches zero
- **THEN** Neo4j records the dynamic stale target-node and target-edge counts
- **WHEN** cleanup runs with `file_id` and current `run_id` parameters
- **THEN** stale target edges are removed before stale target nodes
- **AND** final graph totals equal pre-cleanup totals minus stale entities
- **AND** duplicate node and edge groups are zero
- **AND** no target entity retains the baseline `run_id`

#### Scenario: Metadata replacement preserves unchanged files

- **WHEN** Spark processes the one replay metadata event
- **THEN** MongoDB still contains exactly one distinct `file_id` document per
  discovered source file
- **AND** the target document has the new `run_id` and `content_hash`
- **AND** every non-target document retains its baseline `run_id` and
  `content_hash`
- **AND** duplicate `file_id` groups are zero

### Requirement: Store Evidence Receives Independent Acceptance

After Truc's acceptance PR merges, Thanh SHALL open
`review/thanh/stage3-store-acceptance` from the updated `origin/dev`, validate
the strict manifest, and independently compare the committed JSON and UI
evidence. Thanh must not alter expected counts to make failed evidence pass.

#### Scenario: Store acceptance PR

- **WHEN** manifest validation returns `stage=3, status=pass`
- **THEN** Thanh confirms the target-state transitions match the replay manifest
- **AND** stale deletion matches pre-cleanup counts and final stale, duplicate,
  and old-run counts are zero
- **AND** MongoDB contains one document per source file with every non-target
  document unchanged
- **AND** JSON and UI evidence agree on target `file_id`, replay `run_id`, and counts
- **AND** Thanh opens a tracker-only acceptance PR into `dev` with `APPROVED`
