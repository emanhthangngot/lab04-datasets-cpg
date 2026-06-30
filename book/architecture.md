# Architecture

```text
huggingface/datasets -> parser_service -> Kafka
Kafka cpg.nodes/cpg.edges -> Neo4j Kafka Connector -> Neo4j
Kafka cpg.metadata -> Spark Structured Streaming -> MongoDB
Kafka cpg.errors -> logs / evidence
```

TODO:

- Replace this text diagram with final architecture diagram or screenshot.
- Explain why Spark is not between Kafka and Neo4j.
- Record service names and ports from `docker-compose.yml`.
