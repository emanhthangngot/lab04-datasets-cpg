# Stage 2 Architecture Diagram Redesign

## Goal

Replace the current dense Stage 2 architecture image with a minimal system
diagram created through the official remote Excalidraw MCP endpoint at
`https://mcp.excalidraw.com`.

## Visual Direction

- Use a single left-to-right reading path.
- Organize the scene into four visual groups: Repository, Parser, Kafka, and
  Stores.
- Make Kafka the central fan-out hub for the four actual topics.
- Keep Neo4j and MongoDB as distinct destinations so the direct graph route and
  Spark metadata route are immediately visible.
- Use a restrained blue/slate palette with green success accents and one red
  error accent.
- Prefer short labels and metric badges over paragraphs or raw JSON.

## Required Content

- Source: `huggingface/datasets`, shallow clone.
- Parser output: AST plus CFG, DFG, and CALL relationships.
- Kafka topics: `cpg.nodes`, `cpg.edges`, `cpg.metadata`, and `cpg.errors`.
- Graph route: nodes and edges go through Kafka Connect directly to Neo4j.
- Metadata route: metadata goes through Spark Structured Streaming to MongoDB.
- Error route: errors terminate in observable evidence/log output.
- Provenance strip: schema `1.0`, dataset commit abbreviated to `41adfd0f`, and
  the full commit available in the surrounding book text.
- Metrics:
  - 21,415 explicit CPG nodes.
  - 7,968 relationships.
  - 1,213 unresolved-call placeholders.
  - Five MongoDB metadata documents.
  - Spark checkpoint offset 5.
  - Zero duplicate groups in both stores.

## Layout

1. A narrow provenance strip spans the top.
2. The primary pipeline occupies the center and reads left to right.
3. Kafka topics fan out vertically from one hub instead of appearing as long
   prose blocks.
4. Neo4j occupies the upper destination lane; Spark and MongoDB occupy the
   lower destination lane.
5. A thin acceptance footer shows manifest validation and zero duplicates.

The final scene should contain approximately 20–25 primary visual elements and
must avoid arrow/text collisions, clipped labels, and edge-to-edge content.

## Deliverables

- Replace `book/_static/stage2_pipeline.excalidraw` with the MCP-created
  editable scene.
- Replace `book/_static/stage2_pipeline.png` with its rendered export.
- Keep `book/architecture.md` paths unchanged.
- Preserve the existing Stage 2 metrics and technical meaning.

## Validation

- Open the MCP scene in the interactive Excalidraw UI and inspect the full
  canvas.
- Confirm all labels are legible at book-page width.
- Confirm arrows do not cross labels or unrelated components.
- Confirm the rendered PNG is included by a clean Jupyter Book build.
- Run the existing Stage 2 book tests and full Python test suite.

## Integration Constraint

The remote MCP must be registered as a custom connector and the Codex session
must be restarted before its tools can be invoked. If the connector cannot be
registered in the current environment, stop and report that setup blocker;
do not silently fall back to hand-authored Excalidraw JSON.
