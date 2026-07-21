# Stage 4 Spec Readiness Review

Date: 2026-07-21  
Scope: review only; no spec/code changes  
Decision owner: user

## Confirmed Completion Boundary

- Stage 4 must independently contain every final-submission condition from the assignment.
- The whole lab is complete only after the Pages root URL is submitted to Moodle.
- Moodle evidence is intentionally minimal: checked item, submission date, exact submitted URL.
- No Moodle screenshot/receipt required; owner accepts the traceability risk.
- Runtime Stage 1-3 design is not reopened; Stage 4 must verify its evidence is present in the final submission.

## Verdict

**NOT READY for whole-assignment completion.**

The technical publication is substantially proven: local tests and static gates pass, GitHub Actions published commit `7ae8a83`, Pages is built from `gh-pages`, and sampled live URLs return HTTP 200. However, the Stage 4 spec is not self-contained against the assignment, the final Moodle action remains unchecked, and the acceptance/archive edits exist only in the uncommitted working tree. The published book therefore still contains the pre-acceptance checklist state. Current `APPROVED`, archived, and "latest content" claims are premature.

## Verified Evidence

- Assignment defines one public GitHub Pages Jupyter Book URL: `docs/BigData_Lab04_Streaming.md:67-75`.
- Assignment requires each task chapter to contain approach/reasoning, executed real outputs, database UI figures, and an ending reflection: `docs/BigData_Lab04_Streaming.md:69-71`.
- Assignment requires all written source, logical organization, meaningful incremental commits, supporting files/logs/screenshots, and run instructions: `docs/BigData_Lab04_Streaming.md:73-75,92-96`.
- Graded deliverables are Task 1-6 plus Architecture: `docs/BigData_Lab04_Streaming.md:81-90`.
- `pytest -q tests/test_stage4_publication.py`: 6 passed.
- `bash scripts/run_checks.sh`: 136 tests passed; Compose, connector JSON, scaffold checks passed.
- `openspec validate --all --strict`: 5 specs passed.
- Stage 3 strict manifest validation: pass.
- `git diff --check`: pass.
- Workflow run `29791146201`: success; source SHA `7ae8a832b5da0976dc5b89ff93081618fe0ae382`.
- Pages deploy run `29791256702`: success; Pages source `gh-pages` `/`; HTTPS enabled.
- Public root and Reflection returned HTTP 200 during review.
- Fresh local `jupyter-book build` was not reproduced because `jupyter-book` is unavailable on this shell PATH. Successful CI build remains valid external evidence.

## Requirement Coverage Matrix

| Assignment/final condition | Stage 4 coverage | Result |
|---|---|---|
| One public Pages root URL | Canonical spec lines 108-127, 145-159 | Covered |
| Moodle receives only root URL | Canonical spec lines 145-159 | Partial: submission itself unchecked |
| Task 1-6 sequential narrative | Canonical spec lines 129-143 | Partial |
| Approach and reasoning in every task | No explicit per-task acceptance | Missing |
| Real executed outputs in every task | Generic live-render check only | Partial, authenticity underspecified |
| DB UI figures in task chapters | Neo4j/MongoDB requirement lines 64-77 | Covered for Tasks 4-5 only |
| Ending reflection in every task | Separate Reflection page checked; per-task ending not required | Missing |
| Architecture diagram/content correctness | Route exists; no diagram/content criteria | Missing |
| All team-written source in public repo | No requirement | Missing |
| Logical source organization | No requirement | Missing |
| Meaningful incremental commit history | Safe dev-to-main merge is not equivalent | Missing |
| Clear code comments | No requirement | Missing |
| Required files/logs/screenshots | Partial artifact checks, no completeness criterion | Partial |
| Run instructions for complex environments | Public-path cleanup only | Partial |
| No secrets/private data | Canonical spec lines 79-92 | Covered but scope/definitions ambiguous |
| Durable committed acceptance record | Canonical spec lines 145-157 | Required, currently not achieved |
| Submitted URL + date + checkbox | No complete acceptance model | Missing |

## Findings

### F1 — Blocker: Moodle submission is incomplete

`openspec/changes/archive/2026-07-21-stage4-final-publication/tasks.md:148-155` leaves task 9.6 unchecked. `docs/team/workplan.md:130-152` also records Moodle as a remaining manual action. Under the confirmed boundary, the whole assignment cannot be marked complete.

Required spec behavior: completion requires checkbox, submission date, and exact root URL. Do not require screenshot evidence.

### F2 — Blocker: acceptance and archive are not committed

`HEAD` and `origin/main` are `7ae8a83`. The working tree contains modified acceptance trackers, deletion of the active change, and untracked archive/canonical spec files. At committed `HEAD`:

- `book/index.md:35` still has Pages unchecked;
- `docs/team/workplan.md:126-135` still has Stage 4 gates pending;
- the active Stage 4 change remains tracked;
- `openspec/specs/final-publication/spec.md` does not exist.

An uncommitted archive cannot satisfy the durable completion record.

### F3 — Blocker: post-deployment edits create a publication loop

The verified workflow deployed `7ae8a83`. The checked `book/index.md:35`, acceptance records, and archive were edited afterward and are not in that deployment. Therefore the current working-tree claim that Pages shows the latest final content is false.

The checklist requires recording acceptance after live review, but does not require commit, republish, and repeat live verification after book-affecting acceptance edits. This gap permits a locally checked state that the public book does not show.

### F4 — High: Stage 4 is not self-contained against the assignment

The canonical spec omits explicit acceptance for:

- approach and reasoning in every task chapter;
- an ending worked/failed/fixed reflection in every task chapter;
- Architecture diagram existence and correctness;
- all team-written source in the public repo;
- logical source layout;
- meaningful incremental commit messages/history;
- clear code comments;
- complete logs/files/screenshots;
- task-specific run instructions where needed.

These are authoritative at `docs/BigData_Lab04_Streaming.md:69-75,81-96`.

### F5 — High: evidence checks are weaker than assignment wording

`openspec/specs/final-publication/spec.md:129-143` only requires that outputs/images render and narratives match accepted evidence. It does not prove each task has real executed output, required figures, and its own reflection. Neo4j/MongoDB authenticity receives stronger checks than Tasks 1-3 and 6.

### F6 — Medium: Architecture has route coverage, not acceptance coverage

Architecture is worth one point (`docs/BigData_Lab04_Streaming.md:89`), but Stage 4 only opens `/architecture.html`. It does not require a readable diagram or verify the direct Kafka-to-Neo4j and Kafka-to-Spark-to-Mongo flows.

### F7 — Medium: canonical spec remains unfinished

`openspec/specs/final-publication/spec.md:3-4` contains generated `TBD` Purpose text. That contradicts a polished archived capability.

### F8 — Medium: stale tracker terminology

`docs/team/graph-stores.md:103-105` and `docs/team/kafka-spark.md:101-103` still call the publication checklist active while other working-tree documents say it is archived.

### F9 — Medium: acceptance terms lack objective definitions

Terms such as `real`, `accurately labeled`, `personal data`, `narratives match`, `layout`, and `return successfully` lack observable rules. The spec should define accepted HTTP status/redirect behavior, chapter evidence minimums, and scan scope.

### F10 — Low: process constraints are presented beside assignment requirements

One executor, Python 3.11, Jupyter Book 1.0.3, `dev -> main`, `gh-pages`, and exact routes are valid project decisions, not instructor requirements. Label them as implementation/release constraints to avoid confusing rubric coverage with internal process.

## What Should Be Done

1. Expand the canonical Stage 4 spec with a dedicated final-submission requirement group covering every condition at assignment lines 69-96.
2. Add an explicit per-task acceptance matrix for Task 1-6: approach/reasoning, real executed outputs, required figures, ending reflection, and run instructions where applicable.
3. Add Architecture content acceptance, not only URL availability.
4. Add public repository acceptance for source completeness, organization, comments, and meaningful incremental history.
5. Define whole-assignment completion as Moodle checkbox + date + exact verified root URL.
6. Repair the release sequence to avoid circular claims:
   - prepare acceptance/spec/archive edits on a reviewed branch;
   - merge and deploy all book-affecting changes;
   - live-review that deployed source SHA;
   - record final live acceptance in a docs-only commit that does not trigger/change the book;
   - submit URL to Moodle and record checkbox/date/URL.
7. Replace canonical `TBD` Purpose and reconcile tracker wording.
8. Re-run focused tests, OpenSpec strict validation, manifest validation, clean book build, link/safety scans, and verify all live pages after the final book deployment.

## What Should Not Be Done

- Do not mark the assignment complete before task 9.6 is checked with date and URL.
- Do not treat uncommitted working-tree files as accepted repository state.
- Do not call `7ae8a83` the final main commit after further commits are required.
- Do not republish acceptance text and assume the previous live review covers it.
- Do not weaken the assignment into a generic "page renders" check.
- Do not regenerate Stage 3 evidence or change accepted runtime counts without a real mismatch.
- Do not add a Moodle screenshot requirement; the owner explicitly rejected that overhead.

## Recommended State Model

Use three explicit states:

1. `PUBLICATION_DEPLOYED`: final book source SHA deployed; all live pages/assets accepted.
2. `SUBMISSION_RECORDED`: exact root URL submitted to Moodle; checkbox/date/URL recorded.
3. `COMPLETE`: both states true and durable committed records are internally consistent.

This keeps the workflow simple while preventing `APPROVED` from meaning three different things.

## Benefits

- Direct traceability to every grading condition.
- Removes premature completion and circular deployment claims.
- Makes manual Moodle submission unambiguous without unnecessary screenshot evidence.
- Separates instructor requirements from internal release mechanics.
- Creates verifiable handoff criteria for planning and execution.

## Trade-offs

- One more deployment/live-review cycle is required because book content changed after the first deployment.
- A final docs-only record commit means deployed source SHA and repository tip SHA may differ; both must be labeled clearly.
- Manual Moodle tick has weak dispute evidence; this is an explicitly accepted risk.
- More precise per-task checks increase spec length, but they protect rubric points.

## Work Checklist

- [ ] Replace canonical final-publication Purpose `TBD`.
- [ ] Add every assignment submission requirement to Stage 4.
- [ ] Add Task 1-6 per-chapter evidence/reflection acceptance matrix.
- [ ] Add Architecture diagram correctness acceptance.
- [ ] Add public source, organization, comments, commit-history acceptance.
- [ ] Define objective evidence, HTTP, redirect, link, safety, and scan rules.
- [ ] Add explicit `PUBLICATION_DEPLOYED`, `SUBMISSION_RECORDED`, `COMPLETE` states.
- [ ] Require Moodle checkbox, submission date, and exact root URL.
- [ ] Reconcile stale tracker wording and links.
- [ ] Commit/archive through a reviewed branch; preserve user changes.
- [ ] Deploy the commit containing every book-affecting final change.
- [ ] Live-review root, Architecture, Task 1-6, Reflection, navigation, and assets.
- [ ] Record deployed source SHA and final record SHA without conflating them.
- [ ] Submit the verified root URL to Moodle.
- [ ] Tick Moodle task and record date + exact submitted URL.

## Success Metrics

- 100% of assignment lines 69-96 mapped to at least one Stage 4 SHALL requirement and observable scenario.
- 6/6 task chapters satisfy approach, reasoning, executed real output, relevant figure/UI evidence, ending reflection, and required run instructions.
- Architecture page contains and renders the required architecture diagram; HTTP 200.
- Root + eight chapter routes return HTTP 200; required assets return HTTP 200; no broken navigation links.
- Stage 4 focused tests: 0 failures.
- Full repository tests: 0 failures.
- OpenSpec strict validation: 0 failures.
- Stage 3 manifest validation: pass with accepted hashes/counts unchanged.
- Clean Jupyter Book build produces `book/_build/html/index.html`.
- Committed `main` contains the canonical final-publication spec and archived change; no pending active duplicate.
- Acceptance record names deployed source SHA and final record SHA accurately.
- Moodle item is checked and includes submission date plus exactly `https://emanhthangngot.github.io/lab04-datasets-cpg/`.

## Unresolved Questions

None.
