# Stage 2 Acceptance Matrix

Evidence run: `2026-07-16T09:16:57Z`  
Pipeline commit: `b267a458bc053f76e54e37bbc3644d0c11caedc0`  
Dataset commit: `41adfd0f9ee9ba3a6b4f719d5b551c5b19ae45e2`

| PDF requirement | Status | Evidence |
|---|---|---|
| Task 1: shallow clone and Python discovery | Complete | `book/task1_repository.ipynb` |
| Task 2: incremental CPG with stable IDs and CFG/DFG/CALL | Complete | `book/task2_parser.ipynb`, `screenshots/stage2_manifest.json` |
| Task 3: four Kafka topics with schema version and event time | Complete | `book/task3_kafka.ipynb`, `screenshots/kafka/` |
| Task 4: direct Kafka connector to Neo4j, idempotent keys | Complete | `book/task4_neo4j.ipynb`, `screenshots/neo4j/` |
| Task 5: Spark metadata stream, checkpoint, MongoDB | Complete | `book/task5_mongodb.ipynb`, `screenshots/spark/`, `screenshots/mongodb/` |
| Architecture diagram and route explanation | Complete | `book/architecture.md`, editable Excalidraw source |
| Task 6: replay and before/after idempotence | Stage 3 | `book/task6_replay.md` remains explicit |
| GitHub Pages publication | Stage 4 | Requires merge to `main` and workflow verification |
| Moodle submission | External | Requires the final published Pages root URL |

## Accepted Stage 2 invariants

- Kafka: 21,415 unique nodes, 7,968 unique edges, five metadata events, one error event.
- Neo4j: 21,415 explicit nodes, 1,213 placeholders, 7,968 relationships, zero duplicate groups.
- MongoDB: five documents and zero duplicate `file_id` groups.
- Spark: metadata offset 5 and completed micro-batch 0.
- Provenance: every sampled event uses the exact 40-character dataset commit; artifact hashes validate.

UI screenshots were not fabricated when the integrated browser bridge was unavailable. Direct connector status, Cypher/Mongo queries, executed notebook outputs, and the validated manifest are the acceptance evidence.
