// Lab04 Neo4j constraints.
// Apply with a locally supplied password:
// docker compose exec -T neo4j cypher-shell -u neo4j -p '<local-lab-password>' < neo4j/constraints.cypher
//
// Keep only node uniqueness by default. Relationship uniqueness constraints are
// intentionally omitted because they may not be supported in the lab setup.

CREATE CONSTRAINT cpg_node_id IF NOT EXISTS
FOR (n:CPGNode) REQUIRE n.id IS UNIQUE;
