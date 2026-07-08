# Evidence Book Specification

## Purpose

Define the evidence behavior owned by Tuan: notebooks, screenshots, Jupyter Book
chapters, reflections, and safe public publication.

## Requirements

### Requirement: Evidence Maps To Lab Tasks

The Jupyter Book SHALL include evidence for Lab04 tasks 1 through 6.

#### Scenario: Chapter coverage

- GIVEN the book skeleton exists
- WHEN Tuan reviews `book/_toc.yml` and task chapters
- THEN every task from 1 through 6 has a chapter
- AND architecture and reflection pages are present
- AND each chapter points to real notebook output, command output, query output,
  or screenshots as evidence becomes available

### Requirement: Evidence Is Real

Notebook and book evidence MUST come from executed commands, executed notebooks,
database query output, or screenshots of the local lab environment.

#### Scenario: Evidence update

- GIVEN a teammate provides runtime or store output
- WHEN Tuan updates a notebook or book chapter
- THEN the output is copied or linked accurately
- AND missing evidence remains marked as pending instead of being invented

### Requirement: Screenshots Are Safe To Publish

Screenshots and notebook outputs MUST NOT expose credentials, private machine
details, or irrelevant personal data.

#### Scenario: Pre-publication review

- GIVEN the book is ready to publish
- WHEN Tuan reviews screenshots and notebooks
- THEN unsafe details are not visible
- AND any unsafe artifact is redacted or replaced before Tri approves publish

### Requirement: Book Build Is Verified

The final book SHALL build locally before publication.

#### Scenario: Build check

- GIVEN `jupyter-book` is installed in the local environment
- WHEN Tuan runs `jupyter-book build book/`
- THEN the build completes successfully
- AND broken links or missing assets are fixed before final review

### Requirement: Stage 2 Evidence Distinguishes Captured From Pending

The evidence book SHALL only replace pending slots with real Stage 2 output.

#### Scenario: Stage 2 evidence update

- GIVEN parser, Kafka, Neo4j, MongoDB, or Spark output has been captured
- WHEN Tuan updates notebooks or book chapters
- THEN Task 1-5 slots use exact command/query/notebook output or screenshot
  references
- AND Task 6 replay evidence remains pending unless the full replay workflow
  has actually run
