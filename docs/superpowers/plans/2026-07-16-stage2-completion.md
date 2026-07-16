# Stage 2 Completion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:executing-plans` to implement this plan task-by-task. Do not
> dispatch subagents unless the user explicitly authorizes delegation.

**Goal:** Produce a fresh, provenance-correct Stage 2 clean run and a complete
Jupyter Book presentation for Tasks 1-5 plus Architecture.

**Architecture:** The runbook produces sanitized raw evidence and a validated
manifest. Canonical notebooks consume those artifacts without requiring Docker
during Pages builds. Optional local UIs and an Excalidraw diagram provide the
visual evidence required by the assignment.

**Tech Stack:** Bash, Python 3.11, pytest, Docker Compose, Kafka, Neo4j, Spark
3.5, MongoDB 7, Jupyter Book 1.0.3, Excalidraw.

## Global Constraints

- Work on `feature/stage2-completion` from `origin/dev`.
- Preserve `repo=huggingface/datasets` and schema version `1.0`.
- Never accept `commit_sha=unknown` in Stage 2 evidence.
- Keep Mongo Express evidence-only, read-only, and bound to localhost.
- Keep Task 6 replay pending and do not claim the complete lab is finished.
- Use English for book content and retain exact commands/run metadata.

### Task 1: Dataset commit provenance

- Add failing source-contract tests proving both parser runs receive the cloned
  dataset SHA and Kafka evidence rejects unknown or mixed SHAs.
- Run the focused tests and confirm the expected failures.
- Resolve the SHA after clone, pass it to sample/error parser runs, validate it
  in Kafka capture, and document the manual parser command.
- Re-run focused and full tests, then commit the runtime provenance change.

### Task 2: Evidence manifest and optional Mongo UI

- Add failing tests for the manifest schema, artifact/raw-count consistency,
  five metadata events, one error event, and the isolated Compose profile.
- Implement a small manifest writer/validator, graph-event summary capture,
  per-topic sample counts, and the evidence-only Mongo Express service.
- Validate default/profile Compose configurations and all evidence tests, then
  commit the evidence contract.

### Task 3: Fresh clean run and visual evidence

- Run the complete reset-enabled Stage 2 workflow with extended readiness
  windows and stop on any provenance/count/duplicate mismatch.
- Validate and sanitize all runtime artifacts and record the observed metrics.
- Capture Neo4j Browser and Mongo UI images from the same live run.
- Install and audit the pinned Excalidraw skill, generate the editable diagram
  and PNG section-by-section, and complete the render/view/fix loop.
- Commit refreshed runtime and visual evidence.

### Task 4: Canonical executed chapters

- Add failing tests requiring Task 1-5 notebooks, executed outputs, run
  metadata, figures, final reflections, and no pending markers.
- Replace the five Markdown placeholders and duplicate notebooks with canonical
  `book/task1_repository.ipynb` through `book/task5_mongodb.ipynb` chapters.
- Complete the architecture page, service/port explanation, index checklist,
  and exact reproduction instructions.
- Execute all five notebooks in place, run the focused tests, build the book,
  inspect rendered pages, and commit the book changes.

### Task 5: Acceptance and delivery

- Add a PDF-requirement matrix that marks Tasks 1-5 and Architecture complete
  while leaving Task 6, Pages, and Moodle verification explicit.
- Synchronize Kafka/Spark, graph-store, evidence-book, and workplan trackers;
  leave archived OpenSpec history unchanged.
- Run all tests, shell syntax checks, both Compose configs, manifest validation,
  notebook execution, placeholder/secret scans, and the Jupyter Book build.
- Review the final diff and images, push the branch, and open a draft PR to
  `dev` with commands, metrics, evidence links, and remaining Stage 3/4 work.
