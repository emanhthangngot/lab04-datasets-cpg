# Stage 2 Acceptance Matrix

Evidence run: `2026-07-23T06:56:49Z`

Pipeline commit: `dc8302084e4cac111b912ca5f2e662c30b794a50`

Dataset commit: `41adfd0f9ee9ba3a6b4f719d5b551c5b19ae45e2`

| PDF requirement | Status | Evidence |
|---|---|---|
| Task 1: shallow clone and Python discovery | Complete | `book/task1_repository.ipynb` |
| Task 2: incremental CPG with stable IDs and CFG/DFG/CALL | Complete | `book/task2_parser.ipynb`, `screenshots/stage2_manifest.json` |
| Task 3: four Kafka topics with schema version and event time | Complete | `book/task3_kafka.ipynb`, `screenshots/kafka/` |
| Task 4: direct Kafka connector to Neo4j, idempotent keys | Complete | `book/task4_neo4j.ipynb`, `screenshots/neo4j/` |
| Task 5: Spark metadata stream, checkpoint, MongoDB | Complete | `book/task5_mongodb.ipynb`, `screenshots/spark/`, `screenshots/mongodb/` |
| Architecture diagram and route explanation | Complete | `book/architecture.md`, editable SVG source |
| Task 6: replay and before/after idempotence | Complete | `book/task6_replay.ipynb`, `screenshots/replay/stage3_replay_manifest.json` |
| GitHub Pages publication | Complete | Public root and all Task 1-6 pages return HTTP 200 |
| Moodle submission | External | Requires the final published Pages root URL |

## Accepted Stage 2 invariants

- Kafka: 133,263 unique nodes, 38,141 unique edges, 138 metadata events, one error event.
- Neo4j: 133,263 explicit nodes, 1,935 placeholders, 38,141 relationships, zero duplicate groups.
- MongoDB: 138 documents and zero duplicate `file_id` groups.
- Spark: metadata offset 138 and completed micro-batch 0.
- Provenance: every sampled event uses the exact 40-character dataset commit; artifact hashes validate.

Direct connector status, Cypher/Mongo queries, executed notebook outputs, the
validated manifests, and real Neo4j Browser/Mongo Express screenshots are the
acceptance evidence.
