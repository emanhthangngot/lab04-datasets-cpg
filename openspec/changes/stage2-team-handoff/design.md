# Design: Stage 2 Team Handoff

## Approach

Use an OpenSpec-style artifact flow without adding the OpenSpec CLI:

```text
proposal -> specs -> design -> tasks -> implementation PR
```

Base specs under `openspec/specs/` describe current accepted behavior. The
active change folder packages the Stage 2 handoff with intent, design, and
small implementation tasks.

## Workflow

1. Tri assigns work in `docs/team/workplan.md`.
2. The owner reads `openspec/specs/<domain>/spec.md`.
3. The owner reads `openspec/changes/stage2-team-handoff/tasks.md`.
4. The owner creates a branch from `dev`.
5. The owner runs baseline checks before editing.
6. The owner implements only assigned tasks.
7. The owner captures command output, query output, notebook output, or
   screenshots as evidence.
8. The owner updates their tracker under `docs/team/`.
9. Tri reviews the PR against schema, runtime, store, replay, evidence, and
   security guardrails.

## Data Flow Boundaries

- Parser emits events to Kafka.
- Kafka Connect sends `cpg.nodes` and `cpg.edges` directly to Neo4j.
- Spark consumes only `cpg.metadata` and writes MongoDB.
- `cpg.errors` is evidence/logging, not graph topology.

## Review Boundaries

- Truc may update runtime scripts and Kafka/Spark evidence.
- Thanh may update Neo4j/MongoDB verification and store evidence.
- Tuan may update notebooks, screenshots, and book chapters.
- Only Tri updates schema/spec contracts unless a blocker is explicitly
  approved.

## Safety

- Do not publish GitHub Pages from Stage 2 handoff work.
- Do not commit credentials or screenshots with private local details.
- Do not prune Docker volumes, drop databases, or run destructive cleanup unless
  Tri explicitly approves the exact command.
