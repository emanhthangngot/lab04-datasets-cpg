# Architecture

```text
huggingface/datasets -> parser_service -> Kafka
Kafka cpg.nodes/cpg.edges -> Neo4j Kafka Connector -> Neo4j
Kafka cpg.metadata -> Spark Structured Streaming -> MongoDB
Kafka cpg.errors -> logs / evidence
```

## Evidence Slots

| Slot | Status | Source |
|---|---|---|
| Final architecture diagram or screenshot | Pending | `book/architecture.md` |
| Service names and ports | Pending | `docker-compose.yml` |
| Neo4j path explanation | Pending | `openspec/specs/graph-stores/spec.md` |
| Spark metadata path explanation | Pending | `openspec/specs/kafka-spark/spec.md` |

## Pending Work

- Replace the text diagram with the final architecture diagram or screenshot.
- Explain why Spark is not between Kafka and Neo4j.
- Record service names and ports from `docker-compose.yml`.
