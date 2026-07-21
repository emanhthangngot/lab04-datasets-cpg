---
date: 2026-07-21
session: stage4-final-submission-contract
---

# Journal: 2026-07-21 — Stage 4 Final Submission Contract

## Context

The session strengthened Stage 4 so the final-publication capability is
self-contained against the Lab04 submission rubric. The work preserved accepted
Stage 1-3 runtime, schema, counts, and manifest-backed evidence while correcting
premature completion language. This is a chronological work record; later
entries record the deployment update while Moodle remains a separate manual
submission gate.

## What Happened

- Started from the readiness review, which found that the technical publication
  had been verified for source `7ae8a832`, but the final contract omitted rubric
  details, the current edits were not deployed, and Moodle remained pending.
- Added regression assertions first for Task 1-6 chapter content, Architecture,
  repository completeness, and the Moodle completion boundary. The new focused
  assertions failed against the old contract before implementation edits.
- Expanded the canonical and archived final-publication contracts to require
  approach/reasoning, real executed output, applicable figures, closing
  worked/failed/resolved reflections, run instructions, a grading-ready
  architecture diagram, and a complete public repository record.
- Added `## Approach and reasoning` sections to all six executed task notebooks
  so the book content satisfies the newly explicit contract without changing
  accepted evidence or runtime behavior.
- Reconciled README, book index, and team trackers. They initially identified
  `7ae8a832` as the previously verified publication source, kept the new update
  undeployed until live review, and kept Moodle status, date, and exact URL as
  `PENDING`.
- Archived the prepared Stage 4 change and promoted its canonical specification,
  while leaving the archive checklist's deployment/live-review and Moodle steps
  unchecked.
- Applied review findings by making HTTP/asset acceptance observable, separating
  deployed-source and repository-tip concepts, requiring a post-edit deployment
  and repeated live review, retaining meaningful-history/repository checks, and
  explicitly stating that Moodle needs checkbox/date/exact URL but no screenshot
  or receipt.
- After the contract and content edits, the focused suite passed with 11 tests.
  The broader verification also passed: 141 Python tests; 5 strict OpenSpec
  validations with 0 failures; Stage 3 replay manifest validation; scaffold and
  `git diff --check`; and a Jupyter Book 1.0.3 build.
- Removed the transient `uv.lock` created during final build verification; it is
  not part of the prepared Stage 4 change.
- Local code review approved the prepared change at 9.5/10. The review did not
  authorize calling the update deployed, submitted, shipped, or complete.
- AgentWiki publishing was skipped: neither `agentwiki` nor `agent-wiki` CLI is
  available on this shell PATH, and no available AgentWiki MCP integration was
  identified for this session.
- After user authorization, the prepared final contract/book update was pushed
  directly to `main` as
  `ebf9100e266a8352d7a292fd138aeb02649f9246`, published by workflow run
  `29794123254`, deployed by Pages run `29794146923`, and live-reviewed at the
  Pages root URL. Root, Architecture, Task 1-6, Reflection, and required images
  returned HTTP 200.

## Reflection

Tests-first work exposed the exact gap between a broadly successful publication
and a complete submission contract. The strongest improvement was replacing one
ambiguous “approved” state with explicit, independently verifiable states. The
remaining work is external by nature; treating it as locally complete would
reintroduce the circular publication claim that the review identified.

## Decisions Made

| Decision | Rationale | Impact |
|---|---|---|
| Use `PUBLICATION_DEPLOYED`, `SUBMISSION_RECORDED`, and `COMPLETE` as distinct states | A live book, a Moodle submission, and whole-assignment completion are different facts | Prevents a successful Pages run from implying Moodle submission or completion |
| Move the current state to `PUBLICATION_DEPLOYED` after push/deploy/live review | Source `ebf9100e266a8352d7a292fd138aeb02649f9246` is deployed and HTTP-reviewed | Task 9.5 is closed; Moodle remains the only completion blocker |
| Require Moodle checkbox, submission date, and exact root URL, but no screenshot/receipt | This is the accepted minimal durable record for the manual student action | Avoids invented evidence while preserving an explicit completion gate |
| Preserve Stage 1-3 evidence and runtime contracts | The task was submission-contract hardening, not runtime redesign | No accepted hashes, counts, schemas, or store behavior changed |
| Require a reviewed commit, deployment, and repeated live acceptance after book-affecting edits | Prior live review cannot validate content created afterward | Completion remains blocked on a new external publication cycle |

## Next Steps

- Have a student submit exactly
  `https://emanhthangngot.github.io/lab04-datasets-cpg/` to Moodle.
- Record the Moodle checkbox, submission date, and exact submitted root URL;
  mark `COMPLETE` only when both publication and submission states are true.

## Unresolved Questions

- On what date will the student submit the Pages root URL to Moodle?
