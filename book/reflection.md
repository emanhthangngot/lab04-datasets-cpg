# Reflection

## What worked

The pipeline keeps clear ownership boundaries: the parser processes one file at
a time, Kafka Connect writes graph topology directly to Neo4j, and Spark reads
only metadata into MongoDB. Stable file keys, graph `MERGE`, metadata replacement
by `file_id`, and a persistent Spark checkpoint make the replay behavior
observable and repeatable.

## Failures and fixes

Early evidence mixed stale Docker state and multiple parser invocations, which
made counts look nearly doubled. The clean-run guard now resets only explicitly,
records the dataset commit, and rejects mixed repository identities. The first
replay stub also targeted a file outside the accepted five-file sample and
treated expected Kafka replay events as duplicate failures. Stage 3 instead
replays `src/datasets/__init__.py`, separates append-log repetition from store
duplication, waits for both consumers, and validates a hashed evidence manifest.

## CPG limitations

This is a lab-level Python CPG, not a Joern-equivalent model. CFG extraction
covers common statement flow, DFG is intra-procedural, and call resolution is
limited to local lexical definitions. Imports, aliases, inheritance, dynamic
dispatch, exceptions, closures, and inter-file data flow are not fully modeled.
Structural AST IDs are stable for identical content but can change after edits,
so replay requires file-scoped cleanup using `file_id + run_id`.

## Production improvements

A production implementation would use semantic IDs resilient to unrelated AST
movement, emit explicit delete/tombstone events, resolve symbols across modules,
validate schemas in a registry, authenticate and encrypt every service, monitor
consumer lag, and retain versioned evidence outside the runtime database. It
would also execute replay tests in CI against ephemeral infrastructure instead
of relying on one manually operated local stack.
