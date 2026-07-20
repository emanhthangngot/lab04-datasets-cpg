"""Lab04 incremental CPG parser service package.

The parser stays bounded-memory by processing one Python file at a time and
emitting schema-versioned Kafka events for nodes, edges, metadata, and errors.
"""

