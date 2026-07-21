# Stage 4 Final Publication Tasks

All tasks are executed sequentially by one person. No owner assignment or
parallel handoff is required.

## 1. Establish The Release Baseline

- [x] 1.1 Start from clean, synchronized `dev` and record its commit SHA.
- [x] 1.2 Confirm Stage 3 is archived and all archived Stage 3 tasks are complete.
- [x] 1.3 Run strict OpenSpec and Stage 3 manifest validation.
- [x] 1.4 Record current `main`, `dev`, Pages, `gh-pages`, and latest workflow
  state before making Stage 4 changes.
- [x] 1.5 Confirm no destructive runtime or evidence regeneration is required.

## 2. Repair The Publication Workflow

- [x] 2.1 Add a failing static contract test proving the workflow does not use
  unpinned `pip install -U jupyter-book` and requires Jupyter Book 1.0.3.
- [x] 2.2 Update `.github/workflows/publish-book.yml` to install locked
  dependencies or `jupyter-book==1.0.3` on Python 3.11.
- [x] 2.3 Add an explicit existence gate for
  `book/_build/html/index.html` before deployment.
- [x] 2.4 Ensure deployment runs only after a successful build and retains one
  publication mechanism.
- [x] 2.5 Run the focused workflow contract tests.

## 3. Reconcile Public Documentation

- [x] 3.1 Fix README references to missing `.codex/scripts/doctor.sh`, the
  removed `notebooks/` directory, and obsolete active OpenSpec task paths.
- [x] 3.2 Replace inaccurate scaffold/TODO completion claims with the current
  finished architecture and verification workflow.
- [x] 3.3 Review source/docs TODO markers; remove stale claims and retain only
  truthful future limitations.
- [x] 3.4 Replace `NEO4J_PASSWORD=password` in the public book with a safe
  placeholder.
- [x] 3.5 Recheck all public run commands against tracked files.

## 4. Complete Final Evidence Presentation

- [x] 4.1 Re-run final Neo4j and MongoDB verification queries without changing
  accepted counts or hashed evidence.
- [x] 4.2 Compare query results, screenshots, JSON/text artifacts, and the Stage
  3 manifest.
- [x] 4.3 Add or embed real, correctly labeled Neo4j UI evidence in Task 4.
- [x] 4.4 Add or embed real, correctly labeled MongoDB UI evidence in Task 5.
- [x] 4.5 Review Task 3 Kafka, Task 5 Spark, and Task 6 replay narratives against
  the accepted artifacts.
- [x] 4.6 Confirm Task 1-6 and Reflection contain executed output, approach,
  failure/fix explanation, and honest limitations.
- [x] 4.7 Confirm every Task 1-6 chapter contains approach and reasoning, real
  executed output, relevant task evidence, an ending worked/failed/fixed
  reflection, and task-specific run instructions where required.
- [x] 4.8 Confirm Architecture is readable and matches the implemented Kafka to
  Neo4j and Kafka to Spark to MongoDB routes.
- [x] 4.9 Confirm the public repository contains all team source, verification
  files, logical organization, clear comments, and meaningful incremental history.

## 5. Run Local Release Gates

- [x] 5.1 Run full Python tests with zero failures.
- [x] 5.2 Run `openspec validate --all --strict`.
- [x] 5.3 Run strict Stage 3 manifest validation.
- [x] 5.4 Validate Docker Compose, connector JSON, and all Bash scripts.
- [x] 5.5 Validate PowerShell syntax when `.ps1` files changed; otherwise cite
  the accepted Windows record.
- [x] 5.6 Clean and build the Jupyter Book with Jupyter Book 1.0.3.
- [x] 5.7 Confirm all nine generated HTML pages and required images exist.
- [x] 5.8 Run broken-link, credential, token, private-path, personal-data,
  pending-marker, and tracked-build-output scans.
- [x] 5.9 Run `git diff --check` and confirm the release worktree is clean after
  committing the Stage 4 changes.

## 6. Integrate Dev Into Main

- [x] 6.1 Review commits unique to `main` and `dev` and simulate the final merge.
- [x] 6.2 Open a PR from `dev` into `main` with release commands and evidence.
- [x] 6.3 Review the complete PR diff; reject unrelated runtime or evidence
  changes.
- [x] 6.4 Merge normally without force-push, hard reset, or history replacement.
- [x] 6.5 Record the publication source `main` commit SHA.

Acceptance record for section 6:

- PR: https://github.com/emanhthangngot/lab04-datasets-cpg/pull/19
- Merge commit on `main`: `7ae8a832b5da0976dc5b89ff93081618fe0ae382`
- Merged at: `2026-07-21T00:43:58Z`
- Method: normal GitHub merge (no force-push, hard reset, or history rewrite)

## 7. Publish GitHub Pages

- [x] 7.1 Confirm the main-branch `Build and Publish Jupyter Book` run starts.
- [x] 7.2 Confirm build, HTML existence gate, and deployment all conclude
  `success`.
- [x] 7.3 Confirm the publication branch/artifact is created.
- [x] 7.4 Configure repository Pages settings to serve the chosen publication
  mechanism.
- [x] 7.5 Confirm the root Pages URL stops returning `404` and corresponds to the
  named `main` publication source commit.

Acceptance record for section 7:

- Workflow run: https://github.com/emanhthangngot/lab04-datasets-cpg/actions/runs/29791146201
  (`Build and Publish Jupyter Book`, conclusion `success`, head `7ae8a832`)
- Pages deploy run: https://github.com/emanhthangngot/lab04-datasets-cpg/actions/runs/29791256702
  (conclusion `success`)
- Publication branch: `gh-pages` (`7bc77d02857b6edfc4a069bedcc243beb44fcdf7`)
- Pages source: branch `gh-pages`, path `/`, status `built`, HTTPS enforced
- Public root URL: https://emanhthangngot.github.io/lab04-datasets-cpg/ → HTTP 200

## 8. Perform Live Site Acceptance

- [x] 8.1 Open the root index page.
- [x] 8.2 Open Architecture.
- [x] 8.3 Open Task 1 repository discovery.
- [x] 8.4 Open Task 2 parser service.
- [x] 8.5 Open Task 3 Kafka topics.
- [x] 8.6 Open Task 4 Neo4j ingestion.
- [x] 8.7 Open Task 5 MongoDB metadata.
- [x] 8.8 Open Task 6 replay verification.
- [x] 8.9 Open Reflection.
- [x] 8.10 On every page verify navigation, executed output, images, repository
  link, layout, and absence of private data.

Live acceptance matrix (reviewed 2026-07-21):

| Path | HTTP | Notes |
|---|---:|---|
| `/` | 200 | Deliverable checklist + Moodle URL present |
| `/architecture.html` | 200 | Password placeholder only |
| `/task1_repository.html` | 200 | Executed discovery evidence |
| `/task2_parser.html` | 200 | Executed parser evidence |
| `/task3_kafka.html` | 200 | Topic/event evidence |
| `/task4_neo4j.html` | 200 | Real Neo4j UI image loads |
| `/task5_mongodb.html` | 200 | Real MongoDB UI image loads |
| `/task6_replay.html` | 200 | Replay evidence chapter |
| `/reflection.html` | 200 | Limitations documented |

Asset checks: `_images/neo4j_after_cleanup.png`,
`_images/mongodb_after_replay.png`, and `_images/stage2_pipeline.png` all
return HTTP 200. Repository link targets
`https://github.com/emanhthangngot/lab04-datasets-cpg`. No private home-directory
paths or literal lab passwords observed on live pages.

## 9. Record Completion And Submission

- [x] 9.1 Update `book/index.md` only after the live Pages review passes.
- [x] 9.2 Record technical publication acceptance in `docs/team/workplan.md`,
  including deployed source commit, workflow run URL, deployment result, and
  review date.
- [x] 9.3 Update publication/final-review tracker text without creating
  member-specific Stage 4 ownership.
- [x] 9.4 Re-run OpenSpec, tests, manifest, book build, and public-safety gates
  after acceptance-record edits.
- [ ] 9.5 Commit the prepared archive and book-affecting acceptance/spec edits
  through a reviewed branch, deploy that source commit, and repeat live
  acceptance before finalizing the archive record.
- [ ] 9.6 Submit exactly the verified Pages root URL to Moodle; do not submit a
  ZIP, PDF, Word document, chapter URL, or repository URL.
- [ ] 9.7 Record the checked Moodle item, submission date, and exact submitted
  root URL. A screenshot or receipt is not required.
- [ ] 9.8 Mark the whole assignment `COMPLETE` only when both
  `PUBLICATION_DEPLOYED` and `SUBMISSION_RECORDED` are true.

Moodle handoff value (manual student action only):

```text
https://emanhthangngot.github.io/lab04-datasets-cpg/
```

## 10. Failure Control

- [x] 10.1 Keep Stage 4 incomplete while the workflow, Pages configuration, or
  any live page fails. (All publication and live-page gates passed before
  acceptance recording.)
- [x] 10.2 Fix publication failures through reviewed follow-up commits/PRs; do
  not rewrite `main` history. (Release used normal PR #19 merge only.)
- [x] 10.3 Stop on evidence mismatch; do not edit constants or fabricate output.
  (No evidence regeneration; Stage 3 hashes unchanged.)
- [x] 10.4 Rebuild and republish after any secret, broken asset, or content fix.
  (No secret/asset defects found during live review.)
