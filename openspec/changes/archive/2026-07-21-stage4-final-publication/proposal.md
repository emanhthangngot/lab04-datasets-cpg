# Stage 4 Final Publication Proposal

## Why

Stage 3 is accepted and archived, but the final submission is not published.
The public Pages URL returns `404`, no `gh-pages` branch exists, and the latest
publication workflow installed an incompatible unpinned Jupyter Book release.
The public README also contains stale or broken instructions, while Task 4 and
Task 5 need explicit database UI coverage to minimize grading ambiguity.

Stage 4 must turn the accepted evidence package on `dev` into one verified,
public Jupyter Book on `main` without changing runtime contracts or fabricating
evidence.

## What Changes

- Define a single-executor release workflow; no per-member task split.
- Repair and harden the GitHub Pages workflow around Jupyter Book 1.0.3.
- Reconcile public README/book content with the completed repository state.
- Close final screenshot, link, credential, and private-path review gaps.
- Run local release gates before merging `dev` into `main` through a PR.
- Publish from `main`, configure Pages, and verify every live chapter.
- Record the exact Moodle URL only after live acceptance passes.
- Archive this OpenSpec change after Stage 4 acceptance.

## Capabilities

### New Capability

- `final-publication`: reproducible build, safe `dev -> main` release, GitHub
  Pages deployment, live-site acceptance, and Moodle handoff.

### Existing Capabilities Preserved

- Parser/schema version `1.0` and ID semantics.
- Kafka topic and connector contracts.
- Spark checkpoint and MongoDB replacement behavior.
- Stage 2 and Stage 3 manifest metrics, hashes, screenshots, and replay counts.

## Scope

### In Scope

- `.github/workflows/publish-book.yml`
- `README.md`, `SECURITY.md`, and affected team trackers
- `book/_config.yml`, `book/_toc.yml`, book Markdown/notebook chapters
- Existing screenshot references and new real UI evidence when required
- Publication-focused tests and validation scripts
- PR from `dev` to `main`, Pages configuration, live-site review
- Final Stage 4 acceptance record and OpenSpec archive

### Out Of Scope

- Parser, Kafka, Spark, Neo4j, or MongoDB feature redesign
- Schema or accepted count changes
- Regenerating hashed Stage 3 evidence without a new canonical runtime run
- Force-pushing or replacing `main` history
- Publishing generated `book/_build/` content in the source branch
- Automatic Moodle login or submission

## Execution Model

One executor performs all tasks sequentially and owns the final decision log.
There are no member-specific branches, handoffs, or parallel ownership gates in
Stage 4.

## Success Criteria

- Local release gates pass from a clean `dev` checkout.
- Public instructions contain no broken repository paths or stale completion
  claims.
- Task 1-6, Architecture, and Reflection build with executed evidence.
- Every Task 1-6 chapter contains approach and reasoning, real executed output,
  a relevant figure, an ending worked/failed/fixed reflection, and task-specific
  run instructions where required.
- The Architecture page contains a readable diagram that matches both streaming
  routes, and the public repository contains all team source and verification
  artifacts with meaningful incremental history.
- Task 4 and Task 5 contain explicit, real database UI evidence or an accepted
  final-state image with accurate labeling.
- The `dev -> main` PR preserves both histories and is merged without force.
- The Pages workflow succeeds and publishes the final `main` content.
- The root URL and all eight chapter URLs return successfully and render their
  required assets.
- The public site exposes no credential, private path, token, or personal data.
- The only Moodle submission value is the verified Pages root URL.
- Whole-assignment state becomes `COMPLETE` only after the manual Moodle item,
  submission date, and exact submitted root URL are recorded.

## Risks

- An unpinned Jupyter Book release can produce no `book/_build/html` output.
- Pages may remain disabled even after a `gh-pages` branch is created.
- Stale README paths can make a correct implementation unreproducible to the
  grader.
- Reusing replay screenshots without clear labeling can misrepresent Task 4 or
  Task 5 evidence.
- Marking checklists complete before live verification can hide a failed
  deployment.
- Rewriting `main` can lose five commits unique to its history.

## Rollback

- Do not submit Moodle while any live-page gate fails.
- If deployment fails, keep `main` intact, fix publication on `dev`, and merge a
  follow-up PR.
- If the published site is wrong, restore the last known-good Pages deployment
  or republish the corrected `main`; never rewrite accepted evidence to make a
  deployment appear valid.
