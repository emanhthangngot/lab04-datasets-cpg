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
- [ ] 6.4 Merge normally without force-push, hard reset, or history replacement.
- [ ] 6.5 Record the final `main` commit SHA.

## 7. Publish GitHub Pages

- [ ] 7.1 Confirm the main-branch `Build and Publish Jupyter Book` run starts.
- [ ] 7.2 Confirm build, HTML existence gate, and deployment all conclude
  `success`.
- [ ] 7.3 Confirm the publication branch/artifact is created.
- [ ] 7.4 Configure repository Pages settings to serve the chosen publication
  mechanism.
- [ ] 7.5 Confirm the root Pages URL stops returning `404` and corresponds to the
  final `main` release.

## 8. Perform Live Site Acceptance

- [ ] 8.1 Open the root index page.
- [ ] 8.2 Open Architecture.
- [ ] 8.3 Open Task 1 repository discovery.
- [ ] 8.4 Open Task 2 parser service.
- [ ] 8.5 Open Task 3 Kafka topics.
- [ ] 8.6 Open Task 4 Neo4j ingestion.
- [ ] 8.7 Open Task 5 MongoDB metadata.
- [ ] 8.8 Open Task 6 replay verification.
- [ ] 8.9 Open Reflection.
- [ ] 8.10 On every page verify navigation, executed output, images, repository
  link, layout, and absence of private data.

## 9. Record Completion And Submission

- [ ] 9.1 Update `book/index.md` only after the live Pages review passes.
- [ ] 9.2 Record Stage 4 acceptance in `docs/team/workplan.md`, including final
  main commit, workflow run URL, deployment result, and review date.
- [ ] 9.3 Update publication/final-review tracker text without creating
  member-specific Stage 4 ownership.
- [ ] 9.4 Re-run OpenSpec, tests, manifest, book build, and public-safety gates
  after acceptance-record edits.
- [ ] 9.5 Archive `stage4-final-publication` only when all tasks above pass.
- [ ] 9.6 Submit exactly the verified Pages root URL to Moodle; do not submit a
  ZIP, PDF, Word document, chapter URL, or repository URL.

## 10. Failure Control

- [ ] 10.1 Keep Stage 4 incomplete while the workflow, Pages configuration, or
  any live page fails.
- [ ] 10.2 Fix publication failures through reviewed follow-up commits/PRs; do
  not rewrite `main` history.
- [ ] 10.3 Stop on evidence mismatch; do not edit constants or fabricate output.
- [ ] 10.4 Rebuild and republish after any secret, broken asset, or content fix.
