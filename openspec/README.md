# Lab04 OpenSpec Workflow

This folder applies the lightweight OpenSpec style to the Lab04 CPG Streaming
project. It does not require the OpenSpec CLI. The goal is to keep specs,
design notes, and implementation tasks reviewable before team members start
coding.

## Structure

```text
openspec/
├── specs/                 # Source of truth for current behavior
│   ├── kafka-spark/
│   ├── graph-stores/
│   └── evidence-book/
└── changes/               # Active proposed work
    └── stage2-team-handoff/
        ├── proposal.md
        ├── design.md
        ├── tasks.md
        └── specs/
```

## Rules

- Tri owns spec approval and can update source-of-truth specs.
- Truc, Thanh, and Tuan implement from assigned specs and tasks.
- Team members must not redefine schema fields, connector classes, topic names,
  or replay semantics in implementation PRs.
- If implementation reveals a spec gap, record the blocker in the owner tracker
  under `docs/team/` and ask Tri for a spec update before continuing.
- Evidence must come from real commands, notebook outputs, query outputs, or
  screenshots. Do not invent evidence.
- Do not publish credentials, local machine details, or irrelevant personal data
  in notebooks, screenshots, or book pages.

## Work Loop

1. Read the relevant base spec in `openspec/specs/`.
2. Read the active change in `openspec/changes/stage2-team-handoff/`.
3. Create a short-lived branch from `dev`.
4. Run baseline checks before editing.
5. Implement only the assigned task slice.
6. Run relevant checks and capture evidence.
7. Update the matching `docs/team/*.md` tracker.
8. Open a PR to `dev` and list checks, evidence, and blockers.

This mirrors OpenSpec's proposal -> specs -> design -> tasks -> implementation
flow while keeping the Lab04 repository simple and self-contained.
