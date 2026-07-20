## Context

Stage 2 accepted a clean five-file sample at dataset commit
`41adfd0f9ee9ba3a6b4f719d5b551c5b19ae45e2`: 21,415 node events, 7,968
edge events, five metadata events, Spark offset 5, 21,415 explicit Neo4j
nodes, 7,968 relationships, and five MongoDB documents. The default replay
script instead targets `config.py`, which is not one of those five files, and
therefore cannot prove replacement of accepted baseline state.

The team uses Linux and Windows. Bash remains the single runtime implementation;
PowerShell locates Git Bash, passes secrets through the child environment, and
propagates the same exit status.

## Goals / Non-Goals

**Goals:**

- Produce a deterministic clean baseline and replay in one local run.
- Prove checkpoint resume, graph cleanup, metadata replacement, and zero store
  duplicates using machine-readable evidence.
- Make all committed evidence tamper-evident and usable by Pages without live
  Docker services.
- Finish Task 6 and final reflection content.

**Non-goals:**

- Change event schema `1.0`, topic names, parser extractors, or ingestion
  topology.
- Merge `dev` into `main`, publish Pages, or submit Moodle.
- Claim Kafka append-log events are unique across replay runs.

## Decisions

### Canonical source mutation

The replay target is fixed to `src/datasets/__init__.py`, baseline `file_id`
`6c39568a6a11c430`. Replace exactly one line:

```diff
-__version__ = "5.0.1.dev0"
+__version__: str = "5.0.1.dev0+lab04-replay"
+LAB04_REPLAY_MARKER = "replay_v2"
```

The current parser contract yields 19/15 target nodes/edges before, 23/16
after, and leaves 3 stale node IDs plus 2 stale edge IDs before cleanup. The
runbook saves the original bytes and restores them from an EXIT trap.

### Canonical runtime sequence

1. Refuse dirty pipeline or dataset worktrees and require
   `RESET_DOCKER_STATE=1` plus `NEO4J_PASSWORD`.
2. Run the existing reset-enabled Stage 2 workflow and validate its manifest.
3. Capture Kafka offsets, Spark offset, Neo4j state, and sorted Mongo snapshots.
4. Restart Spark while preserving `/mnt/checkpoints/cpg_metadata`; verify the
   checkpoint remains at metadata offset 5 and Mongo state is unchanged.
5. Apply the deterministic mutation and run parser file mode with the dataset
   commit and a new replay `run_id`.
6. Wait for Kafka Connect lag zero with replay event-ID repetition allowed, and
   wait for Spark checkpoint offset 6.
7. Capture Neo4j pre-cleanup state, count stale entities, run parameterized
   cleanup, and capture final Neo4j/Mongo state.
8. Restore the source, sanitize evidence, leave services live for the two UI
   screenshots, then write and validate the strict manifest.

Kafka total events after replay are 21,438 nodes, 7,984 edges, 6 metadata, and
1 error. Kafka unique graph IDs are 21,422 nodes and 7,971 edges. Neo4j moves
from 21,415/7,968 explicit nodes/relationships to 21,422/7,971 pre-cleanup and
21,419/7,969 final, while 1,213 external placeholders remain unchanged.

### Evidence boundary

Runtime helpers write normalized JSON/text into `screenshots/replay/`. The
manifest records source hashes, offsets, before/restart/after store states,
stale deletion counts, and SHA-256 hashes for every committed raw artifact and
PNG. The manifest never hashes itself. Sanitization happens before manifest
creation; any later artifact modification invalidates validation.

The Task 6 notebook reads only committed manifest/artifacts. It does not connect
to Docker during notebook execution or Pages builds.

### Cross-platform boundary

`scripts/run_stage3_evidence.sh` is the sole implementation. The PowerShell
wrapper accepts `-ResetDockerState` and a `SecureString` password, locates Git
Bash through an explicit path or Git installation, exposes the password only
for the child process, clears it in `finally`, and returns the Bash exit code.

## Failure Handling

- Wrong baseline counts, dataset SHA, target hash, or live offsets stop before
  source mutation.
- A mutation match count other than one stops immediately.
- Connector lag and Spark checkpoint waits have bounded configurable deadlines.
- Cleanup cannot run until the connector gate succeeds.
- Source restoration runs for success, failure, or interruption.
- Missing screenshots prevent manifest creation rather than creating a partial
  pass artifact.
- Services remain available after failure for investigation; no second volume
  reset occurs automatically.

## Verification Strategy

- Unit-test mutation counts, stale ID sets, manifest success/failure cases, and
  artifact hashing using temporary fixtures.
- Source-contract test ordering, reset guards, secret handling, replay-specific
  output paths, and PowerShell forwarding.
- Run shell syntax, PowerShell parser, OpenSpec strict validation, Compose
  parsing, full pytest, notebook execution, strict manifest validation, and a
  local Jupyter Book build.
- Run the destructive canonical workflow once on a machine with Docker access;
  Thanh approves store evidence before Tuan publishes it in the book.
