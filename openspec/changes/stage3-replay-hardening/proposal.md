## Why

Task 6 is still a stub: the current replay target was not part of the accepted
five-file baseline, stale cleanup has never been exercised, Spark checkpoint
resume has not been proven, and the final book has no replay evidence. Stage 3
must produce one reproducible clean run whose machine-readable artifacts and UI
evidence prove the complete before/after path.

## What Changes

- Rebuild the accepted Stage 2 baseline and replay one deterministic edit to
  `src/datasets/__init__.py` in the same run.
- Restart Spark with the existing checkpoint and prove offsets remain at 5
  before the replay and advance to 6 after exactly one metadata event.
- Capture Neo4j before, pre-cleanup, and final states; delete stale entities by
  `file_id + run_id` only after Kafka Connect lag reaches zero.
- Prove MongoDB replaces the target document while four unchanged documents
  retain their original `run_id` and `content_hash`.
- Add strict replay-manifest validation, two database UI screenshots, an
  executed Task 6 notebook, complete reflections, and Linux/Windows commands.
- Preserve schema version `1.0`, all four topic names, and the existing direct
  Kafka Connect-to-Neo4j architecture.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `parser-core`: define the canonical one-file replay target, deterministic
  mutation, new-run context, and source restoration contract.
- `kafka-spark`: distinguish expected Kafka replay events from store
  duplicates and prove checkpoint restart/resume with exact offset deltas.
- `graph-stores`: require three-phase store evidence and parameterized stale
  cleanup with post-cleanup invariants.
- `evidence-book`: require strict manifest-backed Task 6 evidence, two UI
  screenshots, executed notebooks, reflections, and local book build.

## Impact

- Runtime scripts under `scripts/`, Neo4j cleanup queries, and a PowerShell
  wrapper for mixed Windows/Linux team environments.
- New replay artifacts under `screenshots/replay/` and a canonical Task 6
  notebook under `book/`.
- New tests for replay contracts, manifest integrity, runtime ordering, store
  acceptance, Windows forwarding, and book completeness.
- The canonical run resets only local Compose state and requires the explicit
  `RESET_DOCKER_STATE=1` guard plus a runtime Neo4j password.
