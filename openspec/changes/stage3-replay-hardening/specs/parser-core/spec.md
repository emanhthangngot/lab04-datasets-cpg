## ADDED Requirements

### Requirement: Canonical Modified-File Replay

The parser replay SHALL process only the accepted baseline file
`src/datasets/__init__.py` with stable `file_id` `6c39568a6a11c430`, the exact
dataset commit, and a new non-empty `run_id`.

#### Scenario: Deterministic source mutation

- **WHEN** the Stage 3 runbook replaces the accepted version assignment with
  the annotated replay version and `LAB04_REPLAY_MARKER`
- **THEN** the file content hash differs from the baseline hash
- **AND** parser metadata reports 23 AST nodes and 16 total edges instead of
  19 AST nodes and 15 total edges
- **AND** the replay emits one metadata event for that file only

#### Scenario: Source restoration

- **GIVEN** the runbook saved the original target bytes before mutation
- **WHEN** replay succeeds, fails, or is interrupted
- **THEN** the target file is restored byte-for-byte
- **AND** no upstream source modification is committed
