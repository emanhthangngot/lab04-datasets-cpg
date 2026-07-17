# Stage 3 Replay Hardening Design

The approved source of truth is the active OpenSpec change at
`openspec/changes/stage3-replay-hardening/`. It defines a clean Stage 2 baseline,
Spark checkpoint restart at metadata offset 5, a deterministic replay of
`src/datasets/__init__.py`, Neo4j stale cleanup after connector lag reaches
zero, MongoDB replacement by `file_id`, strict artifact hashing, two required
database UI screenshots, and a canonical Task 6 notebook.

The implementation preserves event schema `1.0` and the existing pipeline
boundary: graph events flow from Kafka Connect directly to Neo4j while Spark
consumes metadata only. Bash remains the runtime source of truth; a PowerShell
wrapper provides secure Git Bash invocation for Windows teammates.

Stage 3 ends after strict manifest validation, six executed task chapters,
complete reflections, and a local Jupyter Book build. Main reconciliation,
Pages publication, and Moodle submission remain Stage 4.
