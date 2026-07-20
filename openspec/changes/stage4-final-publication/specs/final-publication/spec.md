# Final Publication Delta Specification

## ADDED Requirements

### Requirement: Stage 4 Has One Sequential Executor

Stage 4 SHALL be performed by one executor using one ordered release checklist.
The workflow SHALL NOT require per-member ownership, parallel branches, or
member-specific approval records.

#### Scenario: Stage 4 execution starts

- **GIVEN** Stage 3 is accepted and archived
- **WHEN** Stage 4 work begins
- **THEN** one executor owns publication fixes, validation, merge, deployment,
  live review, and acceptance recording
- **AND** every task is completed in dependency order

### Requirement: The Publication Build Is Reproducible

The GitHub Pages workflow SHALL build the book with the repository-compatible
Jupyter Book version and SHALL fail before deployment when HTML output is absent.

#### Scenario: GitHub Actions builds the book

- **GIVEN** the workflow runs on Python 3.11 from `main`
- **WHEN** dependencies are installed
- **THEN** Jupyter Book is pinned to version `1.0.3` directly or through
  `requirements.txt`
- **AND** the workflow does not run `pip install -U jupyter-book`
- **WHEN** `jupyter-book build book/` completes
- **THEN** `book/_build/html/index.html` exists
- **AND** deployment cannot run after a failed or empty build

### Requirement: Publication Uses Committed Evidence Offline

The Pages build SHALL consume committed executed notebooks and accepted
manifest-backed artifacts without requiring live infrastructure.

#### Scenario: CI builds the final book

- **GIVEN** Task 1-6 notebook outputs and screenshots are committed
- **WHEN** the Pages job builds the book
- **THEN** notebook execution remains disabled
- **AND** Docker, Kafka, Spark, Neo4j, MongoDB, and the upstream dataset clone
  are not required
- **AND** no generated `book/_build/` content is committed to `main`

### Requirement: Public Documentation Matches The Final Repository

Public instructions SHALL describe the completed system and SHALL reference
only paths and commands available in a public checkout.

#### Scenario: Final documentation audit

- **WHEN** README and book content are reviewed before main merge
- **THEN** references to missing `.codex/scripts/doctor.sh`, `notebooks/`, and
  obsolete active change paths are removed or corrected
- **AND** inaccurate scaffold or incomplete-TODO claims are reconciled
- **AND** honest parser and CPG limitations remain documented
- **AND** commands use placeholders instead of publishable credentials

### Requirement: Database Chapters Contain Real UI Evidence

The final public book SHALL present real and accurately labeled database UI
evidence for the Neo4j and MongoDB tasks.

#### Scenario: Store chapters are finalized

- **WHEN** Task 4 and Task 5 are reviewed
- **THEN** Task 4 embeds or directly presents real Neo4j UI evidence
- **AND** Task 5 embeds or directly presents real MongoDB UI evidence
- **AND** final-state or replay screenshots are labeled with their actual phase
- **AND** screenshot values agree with committed JSON/text evidence and the
  strict Stage 3 manifest
- **AND** no synthetic or fabricated screenshot is used

### Requirement: Public Artifacts Are Safe

The public repository and book SHALL NOT expose secrets, tokens, private user
paths, personal data, or generated local build output.

#### Scenario: Pre-publication safety scan

- **WHEN** public files are scanned before main merge
- **THEN** no real credential, token, private key, home-directory path, or
  Windows user path is present
- **AND** connector credentials remain redacted
- **AND** literal lab-password examples in the book are replaced by placeholders
- **AND** `book/_build/`, local datasets, checkpoints, and environment files are
  not tracked

### Requirement: Dev Is Integrated Into Main Without History Rewriting

Stage 4 SHALL publish through a reviewed merge from `dev` into `main` while
preserving commits unique to both branches.

#### Scenario: Final integration

- **GIVEN** local release gates pass on the final `dev` commit
- **WHEN** the release is integrated
- **THEN** a PR targets `main` from `dev`
- **AND** the PR diff and merge result are reviewed
- **AND** `main` is not force-pushed, hard-reset, or replaced
- **AND** the merge commit becomes the source of the publication workflow

### Requirement: GitHub Pages Deployment Is Verified

Stage 4 SHALL configure and verify a GitHub Pages deployment that serves the
final Jupyter Book from the public repository.

#### Scenario: Main publication succeeds

- **GIVEN** the corrected workflow is present on `main`
- **WHEN** its build-and-deploy job completes
- **THEN** the workflow conclusion is `success`
- **AND** the configured publication source contains the generated HTML
- **AND** repository Pages settings serve the intended site
- **AND** the deployed content corresponds to the final `main` commit

#### Scenario: Deployment is unavailable

- **WHEN** the workflow fails, `gh-pages` is absent, Pages is disabled, or the
  root URL returns an error
- **THEN** Stage 4 remains incomplete
- **AND** no Moodle submission is made

### Requirement: Every Public Book Page Receives Live Acceptance

The executor SHALL open and validate the root page, Architecture, Task 1-6, and
Reflection on the live Pages site.

#### Scenario: Live site review

- **WHEN** GitHub Pages reports a successful deployment
- **THEN** the following paths return successfully: `/`, `/architecture.html`,
  `/task1_repository.html`, `/task2_parser.html`, `/task3_kafka.html`,
  `/task4_neo4j.html`, `/task5_mongodb.html`, `/task6_replay.html`, and
  `/reflection.html`
- **AND** navigation, executed outputs, images, and repository links render
- **AND** Task 1-6 narratives match the accepted evidence
- **AND** no page exposes private data or broken local-only paths

### Requirement: Completion Is Recorded Only After Live Acceptance

Stage 4 checklists and submission records SHALL remain pending until every
local, workflow, and live-site gate passes.

#### Scenario: Final acceptance is recorded

- **GIVEN** all live pages and assets pass review
- **WHEN** the executor records Stage 4 completion
- **THEN** the Pages checklist in the book and workplan is checked
- **AND** the workflow run URL, final main commit, deployment result, and review
  date are recorded
- **AND** this OpenSpec change is archived
- **AND** the only Moodle value is
  `https://emanhthangngot.github.io/lab04-datasets-cpg/`
