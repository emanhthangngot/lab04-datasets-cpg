# MongoDB Metadata Store

Spark Structured Streaming writes `cpg.metadata` events into:

- database: `cpg`
- collection: `file_metadata`
- idempotency key: `file_id`

Verified behavior:

- The MongoDB Spark Connector uses `operationType=replace`.
- Accepted evidence records `file_metadata.countDocuments()` output.
- Accepted evidence records the duplicate `file_id` aggregation output.
- Stage 3 records replay before/after `content_hash` and `run_id`.
