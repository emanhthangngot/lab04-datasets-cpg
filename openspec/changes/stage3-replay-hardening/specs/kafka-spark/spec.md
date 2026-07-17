## ADDED Requirements

### Requirement: Checkpoint Restart Proves Resume

Stage 3 SHALL restart Spark with the persistent Stage 2 checkpoint before
emitting the replay event.

#### Scenario: Unchanged offsets are skipped

- **GIVEN** Kafka metadata end offset and Spark checkpoint offset are both 5
- **WHEN** Spark restarts with `/mnt/checkpoints/cpg_metadata`
- **THEN** its checkpoint remains at offset 5 before replay
- **AND** the five MongoDB documents remain unchanged
- **WHEN** one replay metadata event is emitted
- **THEN** Kafka and Spark metadata offsets both advance to 6

### Requirement: Kafka Replay Is Distinguished From Store Duplication

Kafka graph topics SHALL retain append-only replay events while acceptance uses
unique IDs for pre-cleanup persistence and zero duplicate groups in stores.

#### Scenario: Replay topic deltas

- **WHEN** the modified target emits 23 node, 16 edge, and 1 metadata event
- **THEN** total topic counts advance by exactly those values
- **AND** `cpg.errors` does not advance
- **AND** repeated graph IDs across runs do not fail the connector wait gate
- **AND** cleanup cannot start before connector lag is zero

### Requirement: Windows Runtime Acceptance Is Independent

After the implementation PR is merged into `dev`, Truc SHALL open
`test/truc/stage3-windows-acceptance` from the updated `origin/dev` and run the
PowerShell wrapper in a disposable clean Windows clone or worktree with Docker
Desktop and Git Bash. The smoke run SHALL NOT replace canonical replay evidence.

#### Scenario: Windows wrapper acceptance PR

- **WHEN** `scripts/run_stage3_evidence.ps1` completes with exit code 0
- **THEN** the acceptance record reports Spark offsets `5 -> 5 -> 6`
- **AND** Kafka deltas are 23 nodes, 16 edges, 1 metadata, and 0 errors
- **AND** the record confirms the password was not printed and the target source was restored
- **AND** Truc opens a tracker-only acceptance PR into `dev` with `APPROVED`
- **AND** a failed run records a blocker without marking the gate complete
