## ADDED Requirements

### Requirement: Replay Store State Is Captured In Three Phases

Stage 3 SHALL capture store state before replay, after connector ingestion but
before cleanup, and after cleanup.

#### Scenario: Stale graph cleanup

- **GIVEN** the modified target has a new `run_id`
- **WHEN** connector lag reaches zero
- **THEN** Neo4j contains 3 stale target nodes and 2 stale target edges
- **WHEN** cleanup runs with `file_id` and current `run_id` parameters
- **THEN** stale target edges are removed before stale target nodes
- **AND** final explicit graph totals are 21,419 nodes and 7,969 relationships
- **AND** duplicate node and edge groups are zero
- **AND** no target entity retains the baseline `run_id`

#### Scenario: Metadata replacement preserves unchanged files

- **WHEN** Spark processes the one replay metadata event
- **THEN** MongoDB still contains exactly five distinct `file_id` documents
- **AND** the target document has the new `run_id` and `content_hash`
- **AND** the other four documents retain their baseline `run_id` and
  `content_hash`
- **AND** duplicate `file_id` groups are zero
