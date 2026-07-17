## ADDED Requirements

### Requirement: Stage 3 Evidence Is Strict And Tamper-Evident

Task 6 evidence SHALL be accepted only through a validated replay manifest and
the complete artifact set it hashes.

#### Scenario: Manifest finalization

- **GIVEN** machine evidence has been sanitized and the live replay state is
  still available
- **WHEN** Neo4j Browser and Mongo Express screenshots are captured
- **THEN** the manifest records all runtime invariants and artifact SHA-256
  hashes
- **AND** missing files, mismatched hashes, wrong metrics, pending markers,
  secrets, or absolute local paths fail validation

### Requirement: Final Task 6 Narrative Is Executed

The book SHALL contain one canonical executed Task 6 notebook backed by the
validated manifest.

#### Scenario: Stage 3 book completion

- **WHEN** Tuan finalizes the book
- **THEN** the pending Markdown and duplicate notebook are replaced by
  `book/task6_replay.ipynb`
- **AND** Tasks 1 through 6 are executed in place after the fresh evidence run
- **AND** Task 6 embeds both database UI screenshots
- **AND** Task 6 and the final Reflection state what worked, failed, was fixed,
  and remains limited
- **AND** `jupyter-book build book/` succeeds without live Docker services

### Requirement: Book Receives Post-Merge Acceptance

After Thanh's acceptance PR merges, Tuan SHALL open
`review/tuan/stage3-book-acceptance` from the updated `origin/dev`, validate the
committed manifest, and build the book without live Docker services.

#### Scenario: Book acceptance PR

- **WHEN** repository checks, manifest validation, and a clean Jupyter Book build pass
- **THEN** Tuan confirms all six notebooks contain executed output
- **AND** Task 6 reads the strict manifest and embeds both UI screenshots
- **AND** Task 6 and Reflection explain replay events, unique IDs, stale cleanup, checkpoint resume, and MongoDB replacement accurately
- **AND** Tuan opens a tracker-only acceptance PR into `dev` with `APPROVED`
- **AND** GitHub Pages verification remains Stage 4
