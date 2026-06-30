# CPG Event Schema Contract

`cpg-events.schema.json` is the canonical contract for Lab04 Kafka payloads.
When a field changes here, update parser builders, Spark metadata schema, Neo4j
connector Cypher, MongoDB verification, tests, and the active spec in the same
change.

## Version

Current version: `1.0`

Only 23120099 - Le Xuan Tri can approve schema version changes. Breaking
changes after Stage 1 require a new version and a downstream impact review.

## Topics

| Topic | Event definition | Kafka key |
|---|---|---|
| `cpg.nodes` | `$defs.nodeEvent` | `file_id` |
| `cpg.edges` | `$defs.edgeEvent` | `file_id` |
| `cpg.metadata` | `$defs.metadataEvent` | `file_id` |
| `cpg.errors` | `$defs.errorEvent` | `file_id` |

## Invariants

- Every event includes common run context: `schema_version`, `event_time`,
  `repo`, `commit_sha`, `run_id`, `file_id`, and `file_path`.
- Node and edge `properties` are always JSON objects. Emit `{}` when no extra
  properties exist; never emit `null`.
- Metadata `num_total_edges` is the explicit sum of CFG, DFG, and CALL edge
  counts.
- Error events use `status = "failed"`.
- Stable IDs are required for replay and upsert behavior.

## CALL_UNRESOLVED

Unresolved external calls use normal edge events:

- `edge_type = "CALL_UNRESOLVED"`
- `source_id` points to the internal call-site node.
- `target_id` is a deterministic external placeholder ID derived from the
  unresolved callee name, for example `external:numpy.array`.
- `properties.target_name` stores the unresolved callee name.
- `properties.resolution = "unresolved"`.

The parser does not emit a full `ExternalSymbol` node. Neo4j may create a
placeholder `CPGNode` through the existing edge MERGE behavior. Referential
integrity tests should treat this placeholder target as intentional.
