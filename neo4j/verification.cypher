// Neo4j evidence queries for notebooks and Jupyter Book.
// TODO: Run these after connector ingestion and after replay.

MATCH (n:CPGNode) RETURN count(n) AS node_count;

MATCH ()-[r:CPG_EDGE]->() RETURN count(r) AS edge_count;

MATCH (n:CPGNode)
WITH n.id AS id, count(*) AS c
WHERE c > 1
RETURN id, c;

MATCH ()-[r:CPG_EDGE]->()
WITH r.id AS id, count(*) AS c
WHERE c > 1
RETURN id, c;

MATCH (n:CPGNode {placeholder: true})
RETURN count(n) AS placeholder_count;
