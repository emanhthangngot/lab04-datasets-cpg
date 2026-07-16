# Stage 2 Completion Design

## Goal

Close Stage 2 technically and editorially against the Lab04 PDF rubric for
Tasks 1-5 and the architecture diagram. Task 6 replay, GitHub Pages release,
and Moodle submission remain explicit later-stage work.

## Runtime and Evidence Architecture

The existing clean-run path remains the source of truth:

`huggingface/datasets -> parser -> Kafka -> Kafka Connect -> Neo4j`

`Kafka cpg.metadata -> Spark Structured Streaming -> MongoDB`

The runbook must resolve the cloned dataset Git SHA and pass it to every parser
invocation. Evidence capture rejects `commit_sha=unknown`, mixed repositories,
mixed commit SHAs, duplicate IDs, count drift, incomplete Spark checkpoints,
and store persistence mismatches.

After sanitization, a machine-readable `screenshots/stage2_manifest.json`
records run provenance, observed metrics, exact commands, and SHA-256 hashes
for public evidence artifacts. Five metadata events are captured so parser
AST/CFG/DFG/CALL totals can be derived from raw evidence rather than copied
from prose.

## Evidence UI and Diagram

Neo4j Browser supplies the graph-store UI evidence. MongoDB UI evidence uses
an optional, localhost-only, read-only Compose profile based on the pinned
`mongo-express:1.0.2-20-alpine3.19` image. The deprecated image is evidence
only, never starts in the default stack, and is not suitable for production.

The architecture diagram is an editable Excalidraw source plus a rendered PNG.
It shows the Kafka topic fan-out, direct Neo4j sink path, Spark metadata path,
persistent checkpoint, error evidence path, a representative event, and the
clean-run metrics. The renderer output must pass a visual inspection for
clipping, overlaps, ambiguous arrows, legibility, and sensitive information.

## Canonical Jupyter Book Chapters

The five Stage 2 placeholder Markdown pages and their duplicate notebooks are
replaced by canonical notebooks under `book/` while keeping the current TOC
logical names and URLs. Each chapter contains English narrative, reasoning,
exact reproduction commands, run metadata, executed cells backed by captured
artifacts, relevant figures, and a final worked/failed/resolution reflection.

Task 6 remains visibly pending. The global final reflection and publication
status are not marked complete by Stage 2 work.

## Acceptance

Stage 2 closes only when all automated tests pass, Compose validates with and
without the evidence profile, a fresh clean-run passes, the manifest matches
raw artifacts, all five notebooks execute, the Jupyter Book builds, Task 1-5
contain no pending placeholders, the UI/architecture images are safe and
legible, and the team trackers agree on one completion state.

The acceptance matrix must state that Moodle repository assignment is an
external assumption and that Task 6 and publication remain outstanding.
