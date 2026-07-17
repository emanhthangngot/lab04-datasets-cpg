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
