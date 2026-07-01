# Evidence/Jupyter Book Progress Tracker

Owner: 23120185 - Nguyen Ho Anh Tuan

Role: Evidence, Notebooks, and Jupyter Book

Primary branch examples:

```text
docs/tuan/task1-notebook
docs/tuan/task4-neo4j-screenshot
docs/tuan/final-book-review
```

## Working Rules

- Receive tasks only from `docs/team/workplan.md`.
- Implement from specs written by Le Xuan Tri.
- Do not create or edit spec files.
- Update this tracker before asking for PR review.
- Do not invent evidence. Only use executed notebook output and real screenshots.

## Stage 1: Book Foundation

Tasks:

- [ ] Verify Jupyter Book chapter structure matches the six lab tasks.
- [ ] Confirm each task has a matching notebook.
- [ ] Confirm screenshot folders exist for Kafka, Neo4j, MongoDB, Spark, and replay.
- [ ] Record any missing evidence slot for Tri.

Done when:

- Book skeleton has Overview, Architecture, Task 1-6, and Reflection.
- Notebook and screenshot evidence slots are mapped to chapters.

Spec input to Tri:

- Any missing chapter or evidence type.
- Any wording needed to align the book with the grading rubric.

## Stage 2: Core Evidence Capture

Tasks:

- [ ] Add executed outputs for repository discovery.
- [ ] Add parser output samples.
- [ ] Add Kafka message samples.
- [ ] Add initial Neo4j/MongoDB evidence references from Truc and Thanh.

Done when:

- Task 1-5 chapters have real command/notebook output placeholders replaced.
- Screenshot references point to actual files when available.

Spec input to Tri:

- Evidence gaps that block chapter completion.
- Any task chapter that needs more technical explanation.

## Stage 3: Replay And Final Evidence

Tasks:

- [ ] Add replay notebook output.
- [ ] Add replay screenshots or query outputs.
- [ ] Add chapter reflections for Task 1-6.
- [ ] Build the book locally and fix broken links.

Done when:

- All six task chapters contain executed output and reflection.
- Architecture and Reflection pages are complete.
- `jupyter-book build book/` succeeds locally.

Spec input to Tri:

- Broken links or missing screenshots.
- Any limitation that should be stated honestly in the final Reflection.

## Stage 4: Publication Review

Tasks:

- [ ] Confirm GitHub Pages workflow has published the latest book from `main`.
- [ ] Open the root Pages URL and every chapter.
- [ ] Confirm repository links are visible from the book.
- [ ] Confirm final Moodle URL with Tri.

Done when:

- Tri approves the GitHub Pages URL as the only Moodle submission value.

## Latest Update

Status: Assigned from OpenSpec handoff

Next action: Read `openspec/specs/evidence-book/spec.md` and
`openspec/changes/stage2-team-handoff/tasks.md` section 3 before editing.

Evidence links: None yet.

Blockers: None reported.
