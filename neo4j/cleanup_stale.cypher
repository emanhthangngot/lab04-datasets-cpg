// Delete stale graph entities for a replayed file.
// TODO: Run only after wait_neo4j_connector_idle.sh confirms connector lag is 0.
// Required params: file_id, run_id.

MATCH ()-[r:CPG_EDGE {file_id: $file_id}]->()
WHERE r.run_id <> $run_id
DELETE r;

MATCH (n:CPGNode {file_id: $file_id})
WHERE n.run_id <> $run_id
DETACH DELETE n;
