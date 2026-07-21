# Stage 3 Post-Merge Acceptance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Truc, Thanh, and Tuan complete three auditable post-merge acceptance PRs before Tri can accept and archive Stage 3.

**Architecture:** Keep `stage3-replay-hardening` as the single normative OpenSpec change. Add one owner-specific post-merge requirement to each affected delta spec, mirror those requirements into `tasks.md`, the team workplan, and each owner tracker, and protect the contract with static regression tests. Runtime code and canonical evidence remain unchanged.

**Tech Stack:** OpenSpec 1.5, Markdown, pytest 8.3, Git/GitHub branch workflow, PowerShell, Bash, Jupyter Book 1.0.3.

## Global Constraints

- Post-merge acceptance starts only after the implementation PR is merged into `dev`.
- Each owner opens a separate PR from the updated `origin/dev` back to `dev`.
- Acceptance PR merge order is Truc, then Thanh, then Tuan.
- Truc runs Windows verification in a disposable clean clone or worktree and does not replace canonical evidence.
- Thanh validates committed store evidence and does not alter fixed counts to make evidence pass.
- Tuan builds from committed evidence without live Docker services; Pages remains Stage 4.
- Tri archives OpenSpec only after all three acceptance PRs merge and final checks pass.
- Do not modify runtime code, canonical counts, schema `1.0`, dataset commit, replay target, or replay artifacts.

---

### Task 1: Lock Owner Acceptance In OpenSpec

**Files:**
- Modify: `openspec/changes/stage3-replay-hardening/specs/kafka-spark/spec.md`
- Modify: `openspec/changes/stage3-replay-hardening/specs/graph-stores/spec.md`
- Modify: `openspec/changes/stage3-replay-hardening/specs/evidence-book/spec.md`
- Test: `tests/test_stage3_replay.py`

**Interfaces:**
- Consumes: fixed Stage 3 metrics and artifacts already defined by the active OpenSpec change.
- Produces: three normative post-merge acceptance requirements discoverable by owner and branch name.

- [ ] **Step 1: Add a failing OpenSpec contract test**

Append this test to `tests/test_stage3_replay.py`:

```python
def test_post_merge_owner_acceptance_is_normative() -> None:
    change = PROJECT_ROOT / "openspec" / "changes" / "stage3-replay-hardening"
    specs = {
        "kafka": (change / "specs/kafka-spark/spec.md").read_text(),
        "stores": (change / "specs/graph-stores/spec.md").read_text(),
        "book": (change / "specs/evidence-book/spec.md").read_text(),
    }

    assert "test/truc/stage3-windows-acceptance" in specs["kafka"]
    assert "5 -> 5 -> 6" in specs["kafka"]
    assert "23 nodes, 16 edges, 1 metadata, and 0 errors" in specs["kafka"]
    assert "review/thanh/stage3-store-acceptance" in specs["stores"]
    assert "must not alter expected counts" in specs["stores"].lower()
    assert "review/tuan/stage3-book-acceptance" in specs["book"]
    assert "without live Docker services" in specs["book"]
```

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```bash
pytest tests/test_stage3_replay.py::test_post_merge_owner_acceptance_is_normative -q
```

Expected: FAIL because the three branch names are absent.

- [ ] **Step 3: Add the Truc post-merge requirement**

Append to `specs/kafka-spark/spec.md`:

```markdown
### Requirement: Windows Runtime Acceptance Is Independent

After the implementation PR is merged into `dev`, Truc SHALL open
`test/truc/stage3-windows-acceptance` from the updated `origin/dev` and run the
PowerShell wrapper in a disposable clean Windows clone or worktree with Docker
Desktop and Git Bash. The smoke run SHALL NOT replace canonical replay evidence.

#### Scenario: Windows wrapper acceptance PR

- **WHEN** `scripts/run_stage3_evidence.ps1` completes with exit code 0
- **THEN** the acceptance record reports Spark offsets `5 -> 5 -> 6`
- **AND** Kafka deltas are 23 nodes, 16 edges, 1 metadata, and 0 errors
- **AND** the record confirms the password was not printed and the target source was restored
- **AND** Truc opens a tracker-only acceptance PR into `dev` with `APPROVED`
- **AND** a failed run records a blocker without marking the gate complete
```

- [ ] **Step 4: Add the Thanh post-merge requirement**

Append to `specs/graph-stores/spec.md`:

```markdown
### Requirement: Store Evidence Receives Independent Acceptance

After Truc's acceptance PR merges, Thanh SHALL open
`review/thanh/stage3-store-acceptance` from the updated `origin/dev`, validate
the strict manifest, and independently compare the committed JSON and UI
evidence. Thanh must not alter expected counts to make failed evidence pass.

#### Scenario: Store acceptance PR

- **WHEN** manifest validation returns `stage=3, status=pass`
- **THEN** Thanh confirms target states `19/15`, `26/18`, and `23/16`
- **AND** stale deletion is `3/2` and final stale, duplicate, and old-run counts are zero
- **AND** MongoDB contains five documents with four unchanged non-target documents
- **AND** JSON and UI evidence agree on target `file_id`, replay `run_id`, and counts
- **AND** Thanh opens a tracker-only acceptance PR into `dev` with `APPROVED`
```

- [ ] **Step 5: Add the Tuan post-merge requirement**

Append to `specs/evidence-book/spec.md`:

```markdown
### Requirement: Book Receives Post-Merge Acceptance

After Thanh's acceptance PR merges, Tuan SHALL open
`review/tuan/stage3-book-acceptance` from the updated `origin/dev`, validate the
committed manifest, and build the book without live Docker services.

#### Scenario: Book acceptance PR

- **WHEN** repository checks, manifest validation, and a clean Jupyter Book build pass
- **THEN** Tuan confirms all six notebooks contain executed output
- **AND** Task 6 reads the strict manifest and embeds both UI screenshots
- **AND** Task 6 and Reflection explain replay events, unique IDs, stale cleanup, checkpoint resume, and MongoDB replacement accurately
- **AND** Tuan opens a tracker-only acceptance PR into `dev` with `APPROVED`
- **AND** GitHub Pages verification remains Stage 4
```

- [ ] **Step 6: Validate the OpenSpec requirements and focused test**

Run:

```bash
pytest tests/test_stage3_replay.py::test_post_merge_owner_acceptance_is_normative -q
openspec validate stage3-replay-hardening --strict
```

Expected: one test passes and OpenSpec reports the change valid.

- [ ] **Step 7: Commit the normative requirements**

```bash
git add tests/test_stage3_replay.py openspec/changes/stage3-replay-hardening/specs
git commit -m "docs(evidence): require owner acceptance PRs"
```

---

### Task 2: Make Merge Order And Final Gate Explicit

**Files:**
- Modify: `openspec/changes/stage3-replay-hardening/tasks.md`
- Modify: `docs/team/workplan.md`
- Test: `tests/test_stage3_replay.py`

**Interfaces:**
- Consumes: the three owner branches and acceptance scenarios from Task 1.
- Produces: one ordered merge gate and an unambiguous archive dependency for Tri.

- [ ] **Step 1: Add a failing workflow contract test**

Append:

```python
def test_post_merge_acceptance_order_and_archive_gate_are_documented() -> None:
    tasks = (
        PROJECT_ROOT / "openspec/changes/stage3-replay-hardening/tasks.md"
    ).read_text()
    workplan = (PROJECT_ROOT / "docs/team/workplan.md").read_text()

    ordered = [
        "test/truc/stage3-windows-acceptance",
        "review/thanh/stage3-store-acceptance",
        "review/tuan/stage3-book-acceptance",
    ]
    assert [tasks.index(value) for value in ordered] == sorted(
        tasks.index(value) for value in ordered
    )
    assert [workplan.index(value) for value in ordered] == sorted(
        workplan.index(value) for value in ordered
    )
    assert "all three acceptance PRs" in tasks
    assert "all three acceptance PRs" in workplan
    assert "Pages remain Stage 4" in workplan
```

- [ ] **Step 2: Run the focused test and verify RED**

```bash
pytest tests/test_stage3_replay.py::test_post_merge_acceptance_order_and_archive_gate_are_documented -q
```

Expected: FAIL because the ordered branch list is absent.

- [ ] **Step 3: Add a post-merge section before the shared gate in `tasks.md`**

Insert these unchecked tasks after owner implementation tasks:

```markdown
## 5. Post-Merge Owner Acceptance

- [ ] 5.1 Truc opens `test/truc/stage3-windows-acceptance` from updated `origin/dev`, records the Windows Docker Desktop/Git Bash smoke result, and merges its tracker-only PR into `dev`.
- [ ] 5.2 After 5.1 merges, Thanh opens `review/thanh/stage3-store-acceptance`, independently approves the committed store manifest/artifacts, and merges its tracker-only PR into `dev`.
- [ ] 5.3 After 5.2 merges, Tuan opens `review/tuan/stage3-book-acceptance`, approves the committed Task 1-6 book from a clean local build, and merges its tracker-only PR into `dev`.

## 6. Shared Final Gate
```

Renumber existing shared gates to `6.1`–`6.4`. Rewrite archive tasks so Tri
cannot complete them until all three acceptance PRs have merged.

- [ ] **Step 4: Replace the Stage 3 merge paragraph in `workplan.md`**

Document exactly:

```markdown
Post-merge acceptance order:

1. `test/truc/stage3-windows-acceptance` — Windows runtime record.
2. `review/thanh/stage3-store-acceptance` — committed store evidence approval.
3. `review/tuan/stage3-book-acceptance` — committed book approval.

Each branch starts from the latest `origin/dev` and returns through a separate
PR into `dev`. Tri records Stage 3 acceptance and archives OpenSpec only after
all three acceptance PRs merge. Main merge and Pages remain Stage 4.
```

- [ ] **Step 5: Run tests and strict validation**

```bash
pytest tests/test_stage3_replay.py -q
openspec validate --all --strict
```

Expected: all Stage 3 tests pass and five OpenSpec items validate.

- [ ] **Step 6: Commit the ordered gate**

```bash
git add tests/test_stage3_replay.py openspec/changes/stage3-replay-hardening/tasks.md docs/team/workplan.md
git commit -m "docs(evidence): order post-merge acceptance"
```

---

### Task 3: Add Executable Owner Sign-Off Templates

**Files:**
- Modify: `docs/team/kafka-spark.md`
- Modify: `docs/team/graph-stores.md`
- Modify: `docs/team/evidence-book.md`
- Test: `tests/test_stage3_replay.py`

**Interfaces:**
- Consumes: ordered branches and normative acceptance criteria from Tasks 1–2.
- Produces: copyable commands and complete `APPROVED`/blocker records for each owner PR.

- [ ] **Step 1: Add a failing tracker completeness test**

Append:

```python
def test_owner_trackers_define_post_merge_signoff_records() -> None:
    trackers = {
        "truc": (PROJECT_ROOT / "docs/team/kafka-spark.md").read_text(),
        "thanh": (PROJECT_ROOT / "docs/team/graph-stores.md").read_text(),
        "tuan": (PROJECT_ROOT / "docs/team/evidence-book.md").read_text(),
    }
    for source in trackers.values():
        assert "## Post-Merge Acceptance PR" in source
        assert "Acceptance status: `APPROVED` or `BLOCKED`" in source
        assert "git pull --ff-only origin dev" in source
    assert "Read-Host \"Neo4j password\" -AsSecureString" in trackers["truc"]
    assert "stage3_replay_manifest.py validate --root ." in trackers["thanh"]
    assert "jupyter-book clean book" in trackers["tuan"]
```

- [ ] **Step 2: Run the focused test and verify RED**

```bash
pytest tests/test_stage3_replay.py::test_owner_trackers_define_post_merge_signoff_records -q
```

Expected: FAIL because the common heading and status template are absent.

- [ ] **Step 3: Add Truc's tracker template**

Add `## Post-Merge Acceptance PR` to `kafka-spark.md` containing:

- branch `test/truc/stage3-windows-acceptance`;
- the approved PowerShell command from the design;
- fields for Windows, PowerShell, Docker Desktop, and Git Bash versions;
- exit code, offsets, Kafka deltas, password visibility, and source restoration;
- `Acceptance status: APPROVED or BLOCKED` and blocker output location;
- a warning to use a disposable workspace and not commit regenerated evidence.

- [ ] **Step 4: Add Thanh's tracker template**

Add the same heading to `graph-stores.md` containing:

- branch `review/thanh/stage3-store-acceptance`;
- `git switch dev`, `git pull --ff-only origin dev`, and manifest validation;
- exact Neo4j and MongoDB values from the design;
- JSON/UI agreement and immutable-count checks;
- `Acceptance status: APPROVED or BLOCKED` and conflicting artifact field.

- [ ] **Step 5: Add Tuan's tracker template**

Add the same heading to `evidence-book.md` containing:

- branch `review/tuan/stage3-book-acceptance`;
- repository checks, manifest validation, `jupyter-book clean book`, and build;
- Task 1-6 output, Task 6 screenshot/narrative, Reflection, and no-live-Docker checks;
- `Acceptance status: APPROVED or BLOCKED` and page/artifact blocker field;
- an explicit note that Pages verification is Stage 4.

- [ ] **Step 6: Run tracker tests**

```bash
pytest tests/test_stage3_replay.py -q
```

Expected: all Stage 3 tests pass.

- [ ] **Step 7: Commit the owner templates**

```bash
git add tests/test_stage3_replay.py docs/team/kafka-spark.md docs/team/graph-stores.md docs/team/evidence-book.md
git commit -m "docs(evidence): add owner signoff templates"
```

---

### Task 4: Align Planning Documents And Verify The Package

**Files:**
- Modify: `docs/superpowers/plans/2026-07-16-stage3-replay-hardening.md`
- Verify: all files changed by Tasks 1–3

**Interfaces:**
- Consumes: final OpenSpec, ordered gate, and owner templates.
- Produces: one consistent implementation/acceptance story with no placeholder or Stage 4 scope leak.

- [ ] **Step 1: Add post-merge acceptance to the original Stage 3 plan**

Append a task stating that implementation completion does not equal owner
acceptance. List the three branch names, ordered PR merges, Tri's final checks,
OpenSpec archive, and the exclusion of `dev -> main`/Pages.

- [ ] **Step 2: Run placeholder and contradiction scans**

```bash
rg -n "FIXME|XXX|<fill-me>|implementation deferred|decision required" \
  openspec/changes/stage3-replay-hardening \
  docs/superpowers/plans/2026-07-16-stage3-replay-hardening.md \
  docs/team/workplan.md \
  docs/team/kafka-spark.md \
  docs/team/graph-stores.md \
  docs/team/evidence-book.md
```

Expected: no unresolved placeholder in the new post-merge sections.

- [ ] **Step 3: Run the complete verification suite**

```bash
bash scripts/run_checks.sh
openspec validate --all --strict
python scripts/stage3_replay_manifest.py validate --root .
git diff --check
```

Expected:

- Python suite passes;
- five OpenSpec items pass strict validation;
- manifest remains `stage=3, status=pass`;
- diff check returns no output.

- [ ] **Step 4: Confirm evidence and runtime code are unchanged**

```bash
git diff --name-only f32eb03..HEAD -- scripts neo4j screenshots book
```

Expected: no output. This specification improvement must not modify runtime,
canonical evidence, or book artifacts.

- [ ] **Step 5: Commit planning alignment**

```bash
git add docs/superpowers/plans/2026-07-16-stage3-replay-hardening.md
git commit -m "docs(evidence): align stage3 acceptance plan"
```

- [ ] **Step 6: Review branch status**

```bash
git status --short --branch
git log --oneline origin/dev..HEAD
```

Expected: clean `feature/tri/stage3-replay-hardening` branch with the design,
plan, and specification-improvement commits ready to push.
