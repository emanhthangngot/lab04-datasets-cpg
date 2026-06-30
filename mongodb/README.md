# MongoDB Metadata Store

Spark Structured Streaming writes `cpg.metadata` events into:

- database: `cpg`
- collection: `file_metadata`
- idempotency key: `file_id`

TODO:

- Confirm MongoDB Spark Connector `operationType=replace`.
- Capture `file_metadata.countDocuments()` output.
- Capture duplicate `file_id` aggregation output.
- Capture replay before/after `content_hash` and `run_id`.
