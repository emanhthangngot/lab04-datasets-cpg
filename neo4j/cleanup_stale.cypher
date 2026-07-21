// Delete stale graph entities for a replayed file.
// The caller must first prove Kafka Connect consumer lag is zero.
// Required params: file_id, run_id.

MATCH ()-[r:CPG_EDGE {file_id: $file_id}]->()
WHERE r.run_id <> $run_id
DELETE r;

MATCH (n:CPGNode {file_id: $file_id})
WHERE n.run_id <> $run_id
DETACH DELETE n;
