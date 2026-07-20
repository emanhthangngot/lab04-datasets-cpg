# Parser Core Specification

## Purpose

Define the incremental CPG parser service requirements owned by Tri: file discovery, stable identifier generation, and AST/CFG/DFG/CALL extraction.
## Requirements
### Requirement: File Discovery Scope

The parser SHALL discover and process only Python source files within the `src/datasets/` folder, respecting the project exclusions.

#### Scenario: File discovery filtering
- GIVEN the repository root contains Python files in multiple directories
- WHEN the file discovery function walks the repository
- THEN only files matching `src/datasets/**/*.py` are returned
- AND files matching `tests/**`, `docs/**`, `notebooks/**`, `benchmarks/**`, `templates/**`, `__pycache__/**` or `setup.py` are excluded

### Requirement: Stable Node and Edge Identifiers

The parser MUST generate deterministic identifiers for all node and edge events, suitable for idempotent replay.

#### Scenario: ID stability checks
- GIVEN the repository name, normalized relative file path, and AST node constructs
- WHEN the parser generates IDs for the module, classes, functions, assignments, and anonymous nodes
- THEN the generated IDs are stable across multiple runs
- AND edge IDs are stable hashes of their source ID, target ID, and edge type

### Requirement: Control Flow Graph (CFG) Extraction

The parser SHALL construct control flow edges between statements inside the same scope.

#### Scenario: CFG edge types
- GIVEN a parsed AST tree of a function or module
- WHEN the CFG extractor processes statements
- THEN sequential statements are linked with `CFG_NEXT`
- AND conditional blocks (If) link the condition to the branch entry nodes with `CFG_TRUE` and `CFG_FALSE`
- AND loops (For/While) link to the loop body entry with `CFG_LOOP_BODY` and loop body end back to loop head with `CFG_LOOP_BACK`
- AND Return statements link to the `function_exit` node with `CFG_RETURN`
- AND no control flow edges continue from Return, Break, or Continue statements to subsequent statements in the same block

### Requirement: Data Flow Graph (DFG) Extraction

The parser SHALL construct data flow edges tracking definitions and uses inside each function or module scope.

#### Scenario: Intra-procedural def-use chains
- GIVEN a parsed AST tree
- WHEN a variable is assigned a value (LHS)
- AND that variable is later read (RHS) within the same scope
- THEN a `DFG_DEF_USE` edge is created from the assignment node to the variable read node
- AND variables read on the RHS of an assignment connect to their previous definition, not to the new assignment itself

### Requirement: Scoped Call Edge Resolution

The parser SHALL resolve method and function calls locally where possible, defaulting to unresolved external targets.

#### Scenario: Call edge resolution
- GIVEN a Call expression in the AST
- WHEN the callee is defined locally in the same class (as a class method) or at the module level (global function)
- THEN a `CALL_RESOLVED` edge is created pointing to the target definition node
- AND when the callee is not defined locally, a `CALL_UNRESOLVED` edge is created pointing to a deterministic external placeholder ID of the form `external:<callee_name>`

### Requirement: Metadata Count Consistency

The parser MUST calculate `num_total_edges` explicitly.

#### Scenario: Edge count checking
- GIVEN successfully parsed AST, CFG, DFG, and CALL events
- WHEN the metadata event is built
- THEN `num_total_edges` is set exactly to the sum of CFG, DFG, and CALL edges

### Requirement: Canonical Modified-File Replay

The parser replay SHALL process only the accepted baseline file
`src/datasets/__init__.py` with stable `file_id` `6c39568a6a11c430`, the exact
dataset commit, and a new non-empty `run_id`.

#### Scenario: Deterministic source mutation

- **WHEN** the Stage 3 runbook replaces the accepted version assignment with
  the annotated replay version and `LAB04_REPLAY_MARKER`
- **THEN** the file content hash differs from the baseline hash
- **AND** parser metadata reports 23 AST nodes and 16 total edges instead of
  19 AST nodes and 15 total edges
- **AND** the replay emits one metadata event for that file only

#### Scenario: Source restoration

- **GIVEN** the runbook saved the original target bytes before mutation
- **WHEN** replay succeeds, fails, or is interrupted
- **THEN** the target file is restored byte-for-byte
- **AND** no upstream source modification is committed
