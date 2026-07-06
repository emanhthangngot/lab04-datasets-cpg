# Contributing Guide

This project is a Lab04 deliverable. The final Moodle submission is one GitHub
Pages URL for the published Jupyter Book, but the public repository must also
contain the source code, notebooks, screenshots, and meaningful commit history.

## Branch Flow

- `main`: final publish branch. Pushes that change `book/`, `notebooks/`, or
  `screenshots/` trigger GitHub Pages publication.
- `dev`: team integration branch. Team members branch from `dev` and open pull
  requests back into `dev`.
- Feature branches:
  - `feature/<owner>/<short-task>`
  - `fix/<owner>/<short-task>`
  - `docs/<owner>/<short-task>`
  - `chore/<owner>/<short-task>`

Allowed owner slugs: `tri`, `truc`, `thanh`, `tuan`.

Examples:

```text
feature/truc/kafka-topics
fix/thanh/neo4j-sink
docs/tuan/task4-evidence
```

## Commit Messages

Use a small Conventional Commit style:

```text
<type>(<scope>): <message>
```

Allowed types: `feat`, `fix`, `docs`, `test`, `chore`, `ci`, `refactor`.

Allowed scopes: `parser`, `kafka`, `spark`, `neo4j`, `mongo`, `evidence`,
`book`, `docs`, `ci`, `repo`.

Examples:

```text
feat(kafka): add topic initialization script
docs(book): add task 4 neo4j evidence
fix(parser): keep utils package in discovery scope
```

Avoid vague commits such as `update`, `fix`, `final`, or `misc`.

## Spec Ownership

- 23120099 - Le Xuan Tri is the only spec owner.
- Other members do not create or edit specs.
- Other members receive tasks from `docs/team/workplan.md`, implement from the
  approved spec, and update their assigned progress tracker.
- If a task is unclear, send the blocker and required decision to Tri before
  implementing.

## Pull Request Rules

Each pull request should include:

- Target task or stage.
- Short summary of changed files.
- Test commands or evidence collected.
- Screenshots or query outputs when the change affects Kafka, Neo4j, MongoDB,
  Spark, notebooks, or the Jupyter Book.
- Updated progress tracker for the owner:
  - Truc: `docs/team/kafka-spark.md`
  - Thanh: `docs/team/graph-stores.md`
  - Tuan: `docs/team/evidence-book.md`
  - Tri: `docs/team/workplan.md`

## Local Checks

Run before asking for review:

```bash
bash scripts/run_checks.sh
```

Before final publication:

```bash
jupyter-book build book/
```

## Evidence Rules

- Do not invent counts, screenshots, or database results.
- Keep executed notebook outputs when they are used as evidence.
- Store database or runtime screenshots under `screenshots/`.
- The final book must include Task 1-6, Architecture, and Reflection pages.
- Do not commit `.env`, secrets, local datasets, checkpoints, cache, or generated
  book build output.
