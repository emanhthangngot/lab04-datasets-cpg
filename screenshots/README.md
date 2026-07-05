# Screenshot Evidence Rules

Every screenshot or log artifact stored under this folder must be safe for
public submission and must map to a lab task.

Required metadata for each captured artifact:

- Task: Lab04 task number and short name.
- Command: exact command, UI action, or query that produced the evidence.
- Run date: date when the evidence was captured.
- Result: pass, fail, or blocked, with a short note.
- Source: teammate or owner who produced the evidence.

Folder mapping:

| Folder | Evidence slot |
|---|---|
| `kafka/` | Task 3 Kafka topics and sample messages |
| `neo4j/` | Task 4 Neo4j connector, graph counts, and duplicate checks |
| `mongodb/` | Task 5 MongoDB metadata count and duplicate checks |
| `spark/` | Task 5 Spark submit and checkpoint evidence |
| `replay/` | Task 6 replay, stale cleanup, and duplicate checks |

Do not store screenshots that expose real secrets, personal tokens, private keys,
unneeded local paths, or unrelated personal data.
