# Kafka/Spark Progress Tracker

Owner: 23120180 - Tran Le Trung Truc

Role: Kafka/Spark Runtime

Primary branch examples:

```text
feature/truc/kafka-topics
feature/truc/spark-metadata-stream
fix/truc/connect-registration
```

## Working Rules

- Receive tasks only from `docs/team/workplan.md`.
- Implement from specs written by Le Xuan Tri.
- Do not create or edit spec files.
- Update this tracker before asking for PR review.
- Attach command output or screenshot references when a task affects evidence.

## Stage 1: Runtime Foundation

Tasks:

- [ ] Verify Kafka broker and topic scripts run inside Docker Compose.
- [ ] Verify Kafka Connect service exposes the Neo4j connector plugin.
- [ ] Verify Spark container can run `spark-submit`.
- [ ] Record any runtime blocker for Tri.

Done when:

- `scripts/init_kafka_topics.sh` can create all required topics.
- `scripts/check_connect_plugins.sh` proves the Neo4j connector is available.
- Spark command syntax and package requirements are documented.

Spec input to Tri:

- Kafka/Spark command outputs.
- Any config mismatch between Docker services.
- Any missing package or connector issue.

## Stage 2: Core Streaming Path

Tasks:

- [ ] Capture Kafka topic list evidence.
- [ ] Capture sample messages from `cpg.nodes`, `cpg.edges`, `cpg.metadata`, and `cpg.errors`.
- [ ] Run Spark metadata stream on sample parser output.
- [ ] Capture Spark checkpoint evidence.

Done when:

- Kafka sample messages are available for the Jupyter Book.
- Spark can read `cpg.metadata` from Kafka and write metadata path evidence.
- Progress and evidence links are updated in this file.

Spec input to Tri:

- Sample message fields that differ from expected schema.
- Spark failure modes or checkpoint behavior.

## Stage 3: Replay And Evidence Hardening

Tasks:

- [ ] Re-run Kafka/Spark flow during replay demo.
- [ ] Capture before/after metadata messages.
- [ ] Confirm consumer lag or stream status is stable before evidence capture.
- [ ] Provide outputs for Task 3 and Task 5 chapters.

Done when:

- Replay-related Kafka/Spark evidence is captured.
- Evidence is linked from notebooks or book pages.

Spec input to Tri:

- Replay timing issues.
- Any lag/checkpoint behavior that affects final explanation.

## Stage 4: Final Review

Tasks:

- [ ] Re-run assigned commands for final smoke check.
- [ ] Confirm all Kafka/Spark evidence references still resolve.
- [ ] Review Task 3 and Spark-related Task 5 text in the published book.

Done when:

- Tri approves Kafka/Spark evidence for final Pages publication.

## Latest Update

Status: Not started

Next action: Wait for Stage 1 task assignment from Tri.

Evidence links: None yet.

Blockers: None reported.
