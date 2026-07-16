# Stage 2 Architecture Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the dense Stage 2 architecture image with a minimal, legible system diagram created through the official remote Excalidraw MCP and committed as editable Excalidraw plus PNG assets.

**Architecture:** Register the official streamable HTTP MCP, restart Codex so its `read_me` and `create_view` tools are available, and build one native-element scene in the interactive Excalidraw app. Persist the same native elements to the repository, render them locally, inspect the PNG, and update the existing draft PR without changing book paths.

**Tech Stack:** Codex MCP CLI, Excalidraw MCP Apps, Excalidraw JSON v2, Playwright-based Excalidraw renderer, Jupyter Book, pytest.

## Global Constraints

- Use the official remote endpoint `https://mcp.excalidraw.com`.
- Do not silently fall back to a hand-authored-only workflow if MCP registration or tool discovery fails.
- Keep the diagram light themed and readable at approximately 700 px book width.
- Preserve all Stage 2 metrics and route semantics from the approved spec.
- Keep `book/architecture.md` paths unchanged.
- Keep Task 6, Pages, and Moodle outside this change.
- Do not spawn subagents unless the user explicitly authorizes delegation.

---

### Task 1: Register and verify the official remote MCP

**Files:**
- Modify outside repository: `/home/pearspringmind/.codex/config.toml`
- Inspect: `docs/superpowers/specs/2026-07-16-stage2-architecture-redesign.md`

**Interfaces:**
- Consumes: Codex CLI MCP configuration.
- Produces: an `excalidraw` streamable HTTP server entry that becomes available after restart.

- [ ] **Step 1: Record the current MCP state**

Run:

```bash
codex mcp list
codex mcp get excalidraw
```

Expected: the list does not yet contain `excalidraw`; `get` exits non-zero.

- [ ] **Step 2: Register the remote endpoint**

Run with approval because it writes user-level Codex configuration:

```bash
codex mcp add excalidraw --url https://mcp.excalidraw.com
```

Expected: Codex reports that server `excalidraw` was added.

- [ ] **Step 3: Verify the stored endpoint exactly**

Run:

```bash
codex mcp get excalidraw
rg -n 'mcp_servers\.excalidraw|https://mcp\.excalidraw\.com' /home/pearspringmind/.codex/config.toml
```

Expected: the server is enabled and its URL is exactly
`https://mcp.excalidraw.com`.

- [ ] **Step 4: Restart gate**

End the current Codex session and ask the user to reopen the repository. In the
new session, discover tools whose names or descriptions contain `excalidraw`,
`read_me`, or `create_view`.

Expected: both model-visible tools are present. If they are absent, stop and
report MCP discovery as the blocker; do not edit the diagram assets.

### Task 2: Create the minimal scene in the MCP App

**Files:**
- Reference: `screenshots/stage2_manifest.json`
- Reference: `book/_static/stage2_pipeline.excalidraw`

**Interfaces:**
- Consumes: official MCP tools `read_me()` and `create_view(elements: string)`.
- Produces: an interactive checkpoint containing the approved scene.

- [ ] **Step 1: Read the MCP element contract once**

Call `read_me` once and retain its returned palette, camera, binding, and
minimum-font rules for the rest of the turn.

Expected: the response directs the model to call `create_view` and documents
an 800×600 camera, minimum 16 px body text, and 120×60 minimum labeled shapes.

- [ ] **Step 2: Build the first complete scene**

Call `create_view` with a compact JSON string whose array begins with this
camera and uses the following exact component geometry:

```json
[
  {"type":"cameraUpdate","x":0,"y":0,"width":1200,"height":900},
  {"type":"text","id":"title","x":60,"y":35,"text":"Stage 2 CPG Streaming","fontSize":28,"strokeColor":"#1e1e1e"},
  {"type":"rectangle","id":"provenance","x":60,"y":85,"width":1080,"height":48,"roundness":{"type":3},"backgroundColor":"#dbe4ff","fillStyle":"solid","strokeColor":"#4a9eed","opacity":45},
  {"type":"text","id":"provenance_text","x":92,"y":99,"text":"huggingface/datasets  ·  commit 41adfd0f  ·  schema 1.0","fontSize":16,"strokeColor":"#2563eb"},
  {"type":"rectangle","id":"repo","x":70,"y":250,"width":170,"height":90,"roundness":{"type":3},"backgroundColor":"#a5d8ff","fillStyle":"solid","strokeColor":"#4a9eed","boundElements":[{"id":"repo_text","type":"text"},{"id":"repo_parser","type":"arrow"}]},
  {"type":"text","id":"repo_text","x":95,"y":270,"width":120,"height":50,"text":"Repository\nshallow clone","fontSize":18,"textAlign":"center","verticalAlign":"middle","containerId":"repo","strokeColor":"#1e1e1e"},
  {"type":"rectangle","id":"parser","x":320,"y":235,"width":190,"height":120,"roundness":{"type":3},"backgroundColor":"#d0bfff","fillStyle":"solid","strokeColor":"#8b5cf6","boundElements":[{"id":"parser_text","type":"text"},{"id":"repo_parser","type":"arrow"},{"id":"parser_kafka","type":"arrow"}]},
  {"type":"text","id":"parser_text","x":345,"y":258,"width":140,"height":72,"text":"Parser\nAST + CFG\nDFG + CALL","fontSize":18,"textAlign":"center","verticalAlign":"middle","containerId":"parser","strokeColor":"#1e1e1e"},
  {"type":"ellipse","id":"kafka","x":600,"y":220,"width":180,"height":150,"backgroundColor":"#fff3bf","fillStyle":"solid","strokeColor":"#f59e0b","boundElements":[{"id":"kafka_text","type":"text"},{"id":"parser_kafka","type":"arrow"}]},
  {"type":"text","id":"kafka_text","x":630,"y":270,"width":120,"height":50,"text":"Kafka\n4 topics","fontSize":20,"textAlign":"center","verticalAlign":"middle","containerId":"kafka","strokeColor":"#1e1e1e"},
  {"type":"rectangle","id":"neo4j","x":940,"y":180,"width":200,"height":120,"roundness":{"type":3},"backgroundColor":"#c3fae8","fillStyle":"solid","strokeColor":"#22c55e","boundElements":[{"id":"neo4j_text","type":"text"}]},
  {"type":"text","id":"neo4j_text","x":965,"y":202,"width":150,"height":78,"text":"Neo4j\n21,415 nodes\n7,968 rels","fontSize":18,"textAlign":"center","verticalAlign":"middle","containerId":"neo4j","strokeColor":"#15803d"},
  {"type":"rectangle","id":"spark","x":850,"y":405,"width":160,"height":80,"roundness":{"type":3},"backgroundColor":"#d0bfff","fillStyle":"solid","strokeColor":"#8b5cf6","boundElements":[{"id":"spark_text","type":"text"}]},
  {"type":"text","id":"spark_text","x":875,"y":425,"width":110,"height":40,"text":"Spark\noffset 5","fontSize":18,"textAlign":"center","verticalAlign":"middle","containerId":"spark","strokeColor":"#1e1e1e"},
  {"type":"rectangle","id":"mongo","x":1040,"y":405,"width":140,"height":80,"roundness":{"type":3},"backgroundColor":"#c3fae8","fillStyle":"solid","strokeColor":"#22c55e","boundElements":[{"id":"mongo_text","type":"text"}]},
  {"type":"text","id":"mongo_text","x":1060,"y":425,"width":100,"height":40,"text":"MongoDB\n5 documents","fontSize":18,"textAlign":"center","verticalAlign":"middle","containerId":"mongo","strokeColor":"#15803d"},
  {"type":"rectangle","id":"errors","x":850,"y":555,"width":180,"height":64,"roundness":{"type":3},"backgroundColor":"#ffc9c9","fillStyle":"solid","strokeColor":"#ef4444","boundElements":[{"id":"errors_text","type":"text"}]},
  {"type":"text","id":"errors_text","x":875,"y":570,"width":130,"height":34,"text":"Errors\n1 controlled event","fontSize":16,"textAlign":"center","verticalAlign":"middle","containerId":"errors","strokeColor":"#b91c1c"},
  {"type":"rectangle","id":"acceptance","x":60,"y":720,"width":1080,"height":70,"roundness":{"type":3},"backgroundColor":"#d3f9d8","fillStyle":"solid","strokeColor":"#22c55e","opacity":45},
  {"type":"text","id":"acceptance_text","x":90,"y":742,"text":"Manifest validated  ·  1,213 placeholders  ·  zero duplicate groups","fontSize":18,"strokeColor":"#15803d"}
]
```

Append these native arrows and labels after their endpoints so they render
above the zone shapes:

```json
[
  {"type":"arrow","id":"repo_parser","x":240,"y":295,"width":80,"height":0,"points":[[0,0],[80,0]],"strokeColor":"#4a9eed","strokeWidth":2,"endArrowhead":"arrow","startBinding":{"elementId":"repo","fixedPoint":[1,0.5]},"endBinding":{"elementId":"parser","fixedPoint":[0,0.5]}},
  {"type":"arrow","id":"parser_kafka","x":510,"y":295,"width":90,"height":0,"points":[[0,0],[90,0]],"strokeColor":"#8b5cf6","strokeWidth":2,"endArrowhead":"arrow","startBinding":{"elementId":"parser","fixedPoint":[1,0.5]},"endBinding":{"elementId":"kafka","fixedPoint":[0,0.5]}},
  {"type":"arrow","id":"nodes_neo4j","x":780,"y":260,"width":160,"height":-25,"points":[[0,0],[70,0],[160,-25]],"strokeColor":"#4a9eed","strokeWidth":2,"endArrowhead":"arrow","startBinding":{"elementId":"kafka","fixedPoint":[1,0.3]},"endBinding":{"elementId":"neo4j","fixedPoint":[0,0.35]}},
  {"type":"text","id":"nodes_label","x":805,"y":230,"text":"cpg.nodes","fontSize":14,"strokeColor":"#2563eb"},
  {"type":"arrow","id":"edges_neo4j","x":780,"y":320,"width":160,"height":-25,"points":[[0,0],[70,0],[160,-25]],"strokeColor":"#06b6d4","strokeWidth":2,"endArrowhead":"arrow","startBinding":{"elementId":"kafka","fixedPoint":[1,0.7]},"endBinding":{"elementId":"neo4j","fixedPoint":[0,0.75]}},
  {"type":"text","id":"edges_label","x":805,"y":325,"text":"cpg.edges","fontSize":14,"strokeColor":"#0e7490"},
  {"type":"arrow","id":"metadata_spark","x":735,"y":355,"width":115,"height":90,"points":[[0,0],[35,90],[115,90]],"strokeColor":"#8b5cf6","strokeWidth":2,"endArrowhead":"arrow","startBinding":{"elementId":"kafka","fixedPoint":[0.75,1]},"endBinding":{"elementId":"spark","fixedPoint":[0,0.5]}},
  {"type":"text","id":"metadata_label","x":720,"y":415,"text":"cpg.metadata","fontSize":14,"strokeColor":"#6d28d9"},
  {"type":"arrow","id":"spark_mongo","x":1010,"y":445,"width":30,"height":0,"points":[[0,0],[30,0]],"strokeColor":"#22c55e","strokeWidth":2,"endArrowhead":"arrow","startBinding":{"elementId":"spark","fixedPoint":[1,0.5]},"endBinding":{"elementId":"mongo","fixedPoint":[0,0.5]}},
  {"type":"arrow","id":"errors_route","x":690,"y":370,"width":160,"height":217,"points":[[0,0],[0,217],[160,217]],"strokeColor":"#ef4444","strokeWidth":2,"endArrowhead":"arrow","startBinding":{"elementId":"kafka","fixedPoint":[0.5,1]},"endBinding":{"elementId":"errors","fixedPoint":[0,0.5]}},
  {"type":"text","id":"errors_label","x":705,"y":565,"text":"cpg.errors","fontSize":14,"strokeColor":"#b91c1c"}
]
```

Expected: `create_view` returns a checkpoint ID and renders the complete scene.

- [ ] **Step 3: Inspect the interactive full-screen scene**

Open the MCP App's full-screen editor and inspect at 100% zoom. Check title and
provenance alignment, all six arrow paths, all component labels, and footer
padding.

Expected: no label is clipped, no arrow crosses a component label, and the
primary pipeline reads left to right without consulting the book text.

- [ ] **Step 4: Apply at most one focused correction pass**

If inspection finds arrow collisions, call `create_view` with the actual
checkpoint ID returned by Step 2, delete the six arrows and four topic labels,
and recreate them using the exact element definitions above after increasing
their horizontal or vertical waypoint clearance by 20 px. The call structure
is:

```json
[
  {"type":"restoreCheckpoint","id":"ACTUAL_CHECKPOINT_ID_FROM_STEP_2"},
  {"type":"delete","ids":"repo_parser,parser_kafka,nodes_neo4j,edges_neo4j,metadata_spark,spark_mongo,errors_route,nodes_label,edges_label,metadata_label,errors_label"},
  {"type":"cameraUpdate","x":0,"y":0,"width":1200,"height":900}
]
```

Append the corrected arrows using new IDs suffixed `_v2`; never reuse deleted
IDs. Do not change metrics or introduce new content. If any non-arrow defect is
found, stop and revise the approved design instead of inventing a new layout
during implementation.

Expected: the corrected scene passes the same full-screen inspection.

### Task 3: Persist and render the approved MCP scene

**Files:**
- Modify: `book/_static/stage2_pipeline.excalidraw`
- Modify: `book/_static/stage2_pipeline.png`

**Interfaces:**
- Consumes: the final native element array used by `create_view`.
- Produces: repository assets consumed by `book/architecture.md`.

- [ ] **Step 1: Save the final native elements**

Use `apply_patch` to replace the Excalidraw file with this wrapper and the exact
final native elements from Task 2, excluding `cameraUpdate`,
`restoreCheckpoint`, and `delete` pseudo-elements:

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [],
  "appState": {"viewBackgroundColor": "#ffffff", "gridSize": 20},
  "files": {}
}
```

Populate `elements` with the exact inspected scene. Retain the native
`containerId`, `boundElements`, and arrow bindings so the file remains editable.

- [ ] **Step 2: Validate and render**

Run:

```bash
.venv/bin/python -m json.tool book/_static/stage2_pipeline.excalidraw >/dev/null
uv run python /tmp/render_excalidraw.py \
  /tmp/lab04-datasets-cpg-stage2-completion/book/_static/stage2_pipeline.excalidraw \
  --output /tmp/lab04-datasets-cpg-stage2-completion/book/_static/stage2_pipeline.png \
  --width 1920
```

Expected: JSON validation succeeds and the renderer exits 0 with the PNG path.

- [ ] **Step 3: Inspect the repository PNG**

Open `book/_static/stage2_pipeline.png` with `view_image` at original detail and
repeat the clipping, overlap, arrow-routing, contrast, and balance checks.

Expected: the local PNG matches the approved MCP scene and is readable at book
width. If it differs, correct the native element array, rerender, and recheck.

- [ ] **Step 4: Commit the assets**

```bash
git add book/_static/stage2_pipeline.excalidraw book/_static/stage2_pipeline.png
git commit -m "docs(stage2): improve architecture diagram"
```

### Task 4: Verify and publish the redesign

**Files:**
- Test: `tests/test_stage2_evidence_book.py`
- Verify: `book/architecture.md`

**Interfaces:**
- Consumes: committed diagram assets.
- Produces: an updated remote branch and draft PR #13.

- [ ] **Step 1: Run focused and full verification**

```bash
.venv/bin/python -m pytest -q tests/test_stage2_evidence_book.py
.venv/bin/python -m pytest -q
.venv/bin/jupyter-book clean book
.venv/bin/jupyter-book build book
git status --short --branch
```

Expected: five focused tests pass, 112 total tests pass, the book reports
`build succeeded`, and only ignored build artifacts remain.

- [ ] **Step 2: Push the feature branch**

```bash
git push origin feature/stage2-completion
```

Expected: remote branch advances to the asset commit without force-push.

- [ ] **Step 3: Confirm the existing draft PR**

```bash
gh pr view 13 --json number,isDraft,baseRefName,headRefName,url
```

Expected: PR `13` is still draft, base is `dev`, head is
`feature/stage2-completion`, and the URL is
`https://github.com/emanhthangngot/lab04-datasets-cpg/pull/13`.
