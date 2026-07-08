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

### Requirement: Stage 2 Sample Store Evidence Is Captured

Stage 2 store evidence SHALL prove that sample parser output reached Neo4j and
MongoDB.

#### Scenario: Sample ingestion verification

- GIVEN Stage 2 parser output has been produced to Kafka
- WHEN Thanh verifies the stores
- THEN Neo4j node and relationship counts are captured
- AND MongoDB metadata count and one sample document are captured
- AND placeholder node count is recorded so unresolved-call behavior is visible
