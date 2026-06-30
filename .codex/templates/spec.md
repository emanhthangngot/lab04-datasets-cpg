# Spec — <NNN>-<short-slug>

> Spec ID: <NNN>
> Created: <YYYY-MM-DD>
> Status: draft | reviewed | approved | shipped
> Constitution: `.codex/constitution.md` v1.0.0

## 1. Intent

<One sentence describing the Lab04 capability or evidence this spec delivers.>

## 2. Lab Context

- Affected lab task(s): Task 1 | Task 2 | Task 3 | Task 4 | Task 5 | Task 6 | Book
- Source of truth: `docs/plan.md` section(s): <links or headings>
- Pipeline area: parser | Kafka | Neo4j | Spark | MongoDB | replay | evidence

## 3. Functional Requirements

| ID | Requirement | Acceptance |
|---|---|---|
| FR-1 | <requirement> | <observable proof> |
| FR-2 | <requirement> | <observable proof> |

## 4. Event Or Data Contract

- Kafka topic(s): <if applicable>
- Event fields: <required schema fields or "none">
- Store contract: <Neo4j/MongoDB/checkpoint contract or "none">
- Idempotency rule: <stable ID/upsert/replay behavior or "none">

## 5. Evidence Requirements

- Notebook output:
- Command output:
- Screenshot or database UI evidence:
- Book chapter(s) to update:

## 6. Non-Goals

- <What this spec will not change.>

## 7. Risks And Open Questions

| Risk / Question | Impact | Resolution |
|---|---|---|
| <risk> | <low/med/high> | <mitigation or owner> |

## 8. Definition Of Done

- [ ] Functional requirements are implemented or documented.
- [ ] Relevant parser/runtime/store checks pass.
- [ ] Evidence is captured and linked from the book or notebook.
- [ ] No secrets or local credentials are published.
