# Stage 2 Blocker Remediation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans (required for inline execution). Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix all remaining PR #10 blockers while preserving a shared end-to-end Stage 2 runbook and explicit Truc/Thanh/Tri ownership.

**Architecture:** Keep `scripts/run_stage2_evidence.sh` as the shared orchestrator. Harden Kafka and connector evidence capture, centralize credential sanitization, optimize Spark micro-batch persistence, and update team trackers with cross-owner acceptance gates.

**Tech Stack:** Bash strict mode, Python 3, Pytest, PySpark Structured Streaming, Docker Compose, Kafka, Neo4j, MongoDB, Git/GitHub.

## Global Constraints

- Shared E2E runbook retains Neo4j/MongoDB checks for whole-team testing.
- `NEO4J_PASSWORD` is required; no literal password enters changed source or evidence.
- Runtime evidence must come from real commands; never fabricate missing output.
- Truc executes; Thanh rechecks and accepts Graph Stores; Tri owns merge approval.
- Task 1.2 remains historically accurate: pre-edit checks were missed; current reruns are a documented waiver.
- Never force-push; fetch and compare the remote head before pushing.

---

### Task 1: Add Failing Contract Tests

**Files:**
- Modify: `tests/test_kafka_spark_stage2.py`

**Interfaces:**
- Consumes: capture scripts, runbook, Spark source, and trackers.
- Produces: focused tests for every agreed blocker.

- [ ] **Step 1: Add credential, ownership, count, and fail-fast tests**

Add:

```python
def test_runbook_requires_neo4j_password_without_literal_password() -> None:
    source = (PROJECT_ROOT / "scripts" / "run_stage2_evidence.sh").read_text()
    assert "NEO4J_PASSWORD" in source
    assert 'cypher-shell -u neo4j -p password' not in source


def test_runbook_keeps_shared_graph_store_checks() -> None:
    source = (PROJECT_ROOT / "scripts" / "run_stage2_evidence.sh").read_text()
    for marker in ["node_count", "edge_count", "duplicate_nodes", "duplicate_edges", "file_metadata"]:
        assert marker in source


def test_tracker_has_one_verified_test_count_and_cross_owner_gate() -> None:
    source = (PROJECT_ROOT / "docs" / "team" / "kafka-spark.md").read_text()
    assert "65 tests" not in source
    assert "63 tests" in source
    assert "Thanh" in source and "recheck" in source


def test_kafka_capture_has_fail_fast_contract() -> None:
    source = (PROJECT_ROOT / "scripts" / "capture_kafka_evidence.sh").read_text()
    assert "exit 1" in source
    assert "status" in source and "failed" in source
    assert "properties" in source
```

- [ ] **Step 2: Add Spark and test-hygiene tests**

Add:

```python
def test_spark_batch_is_persisted_and_released() -> None:
    source = (PROJECT_ROOT / "spark_jobs" / "metadata_stream_to_mongo.py").read_text()
    assert ".persist(" in source
    assert ".unpersist(" in source


def test_spark_metadata_test_has_no_unused_ast_assignment() -> None:
    source = (PROJECT_ROOT / "tests" / "test_kafka_spark_stage2.py").read_text()
    assert "tree = ast.parse" not in source
```

- [ ] **Step 3: Run focused tests and record expected failures**

Run:

```bash
python -m pytest tests/test_kafka_spark_stage2.py -q --override-ini="addopts=" -p no:langsmith
```

Expected: the new tests fail against the current head before implementation.

### Task 2: Harden Credentials and Evidence Capture

**Files:**
- Create: `scripts/sanitize_evidence.sh`
- Modify: `scripts/run_stage2_evidence.sh`
- Modify: `scripts/capture_connector_evidence.sh`
- Modify: `scripts/capture_kafka_evidence.sh`
- Test: `tests/test_kafka_spark_stage2.py`

**Interfaces:**
- Consumes: `NEO4J_PASSWORD`, Docker services, Kafka/Connect responses.
- Produces: valid JSON/JSON Lines evidence and non-zero exit on invalid required output.

- [ ] **Step 1: Create the shared sanitizer**

Create `scripts/sanitize_evidence.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

for file in "$@"; do
  [ -f "$file" ] || continue
  sed -i \
    -e 's/"neo4j\.authentication\.basic\.password"[[:space:]]*:[[:space:]]*"[^"]*"/"neo4j.authentication.basic.password": "***REDACTED***"/g' \
    -e 's/"neo4j\.authentication\.basic\.username"[[:space:]]*:[[:space:]]*"[^"]*"/"neo4j.authentication.basic.username": "***REDACTED***"/g' \
    "$file"
done
```

- [ ] **Step 2: Require the password through the environment**

At the start of `run_stage2_evidence.sh`, add:

```bash
: "${NEO4J_PASSWORD:?Set NEO4J_PASSWORD before running Stage 2 evidence capture}"
```

Replace every `-p password` with `-p "$NEO4J_PASSWORD"`. Keep all shared Neo4j/MongoDB checks. Replace stale “commit and open PR” instructions with review/Thanh-recheck instructions.

- [ ] **Step 3: Keep JSON machine-readable**

Write connector logs to `connector_registration.txt`, extract only the JSON object into `connector_registration.json`, write plugin JSON only to `connector_plugins.json`, invoke the sanitizer, and validate:

```bash
bash scripts/sanitize_evidence.sh screenshots/kafka/*.json screenshots/kafka/*.txt
python -m json.tool screenshots/kafka/connector_plugins.json >/dev/null
python -m json.tool screenshots/kafka/connector_registration.json >/dev/null
```

- [ ] **Step 4: Make Kafka validation fail-fast**

When no message exists, print the topic to stderr and `return 1). After collecting validation errors, print them to stderr and call `sys.exit(1)`. For `cpg.errors`, require `status == "failed"`; for nodes/edges, require `properties` to be a dict.

- [ ] **Step 5: Run script syntax and focused tests**

```bash
bash -n scripts/*.sh
python -m pytest tests/test_kafka_spark_stage2.py -q --override-ini="addopts=" -p no:langsmith
```

Expected: all focused tests pass.

### Task 3: Fix Spark Batch Re-computation

**Files:**
- Modify: `spark_jobs/metadata_stream_to_mongo.py`
- Modify: `tests/test_kafka_spark_stage2.py`

- [ ] **Step 1: Persist and release the micro-batch**

Add `from pyspark import StorageLevel` and implement:

```python
def write_batch(batch_df, batch_id):
    batch_df = batch_df.persist(StorageLevel.MEMORY_AND_DISK)
    try:
        row_count = batch_df.count()
        if row_count == 0:
            return
        print(f"[Batch {batch_id}] Writing {row_count} metadata document(s) to MongoDB")
        (
            batch_df.write.format("mongodb")
            .mode("append")
            .option("spark.mongodb.write.database", MONGO_DATABASE)
            .option("spark.mongodb.write.collection", MONGO_COLLECTION)
            .option("spark.mongodb.write.operationType", "replace")
            .option("spark.mongodb.write.idFieldList", "file_id")
            .option("spark.mongodb.write.upsertDocument", "true")
            .save()
        )
    finally:
        batch_df.unpersist()
```

- [ ] **Step 2: Remove unused AST assignment**

Replace `tree = ast.parse(spark_source)` with `ast.parse(spark_source)`.

- [ ] **Step 3: Run focused Spark tests**

```bash
python -m pytest tests/test_kafka_spark_stage2.py -q --override-ini="addopts=" -p no:langsmith
```

Expected: all focused Spark tests pass.

### Task 4: Reconcile Shared Ownership and Trackers

**Files:**
- Modify: `docs/team/workplan.md`
- Modify: `docs/team/kafka-spark.md`
- Modify: `docs/team/graph-stores.md`
- Test: `tests/test_kafka_spark_stage2.py`

- [ ] **Step 1: Record the shared E2E rule in workplan**

Add:

```markdown
- Truc may execute the shared end-to-end Neo4j/MongoDB checks from the Kafka/Spark runbook.
- Thanh rechecks and accepts those Graph Stores outputs against tasks 2.3–2.6.
- Tri merges only after Thanh records approval or a blocker.
```

- [ ] **Step 2: Reconcile Truc's tracker**

Replace `65 tests` with the exact final verified count. Retain the honest task 1.2 waiver, add Graph Stores artifact links and `Thanh recheck required`, and remove stale instructions to open a PR.

- [ ] **Step 3: Add Thanh's recheck checklist**

List the exact evidence files and queries Thanh must recheck: constraints, node/edge/placeholder counts, duplicate node/edge reports, MongoDB metadata, and duplicate `file_id` aggregation.

- [ ] **Step 4: Run documentation tests**

```bash
python -m pytest tests/test_kafka_spark_stage2.py -q --override-ini="addopts=" -p no:langsmith
```

Expected: one test count, explicit Thanh acceptance wording, and shared Graph Stores markers.

### Task 5: Full Verification and Evidence

**Files:**
- Modify generated evidence only when the runtime capture succeeds.

- [ ] **Step 1: Run static verification**

```bash
bash -n scripts/*.sh
python -m compileall -q parser_service spark_jobs tests
docker compose config --quiet
python -m json.tool screenshots/kafka/connector_plugins.json >/dev/null
python -m json.tool screenshots/kafka/connector_registration.json >/dev/null
git diff --check
```

Expected: every command exits zero. Parse JSON Lines samples one line at a time.

- [ ] **Step 2: Run repository checks and full tests**

```bash
bash scripts/run_checks.sh
python -m pytest tests/ -v --override-ini="addopts=" -p no:langsmith
```

Expected: both pass; copy the exact count into Truc's tracker.

- [ ] **Step 3: Run shared E2E if Docker is available**

```bash
export NEO4J_PASSWORD='[provide via local environment, never commit]'
bash scripts/run_stage2_evidence.sh
```

Expected: four Kafka samples, connector RUNNING, committed Spark offset, MongoDB metadata, and Graph Stores artifacts. If Docker is unavailable, record the exact error and do not rewrite artifacts.

- [ ] **Step 4: Recheck evidence provenance**

Parse every JSON artifact, scan changed source/evidence for credentials, run `git diff --check`, and compare each evidence file with its generating command.

### Task 6: Commit and Push Safely

**Files:**
- Commit only planned implementation, test, tracker, and successfully regenerated evidence files.

- [ ] **Step 1: Review final diff**

```bash
git status --short
git diff --stat origin/pr-10-latest...HEAD
git diff --check origin/pr-10-latest...HEAD
```

Expected: only planned files are changed; existing user files under `docs/superpowers/` are not staged accidentally.

- [ ] **Step 2: Commit reviewable groups**

```bash
git add scripts tests spark_jobs
git commit -m "fix(evidence): harden stage2 validation and runtime capture"
git add docs/team
git commit -m "docs(docs): record shared stage2 ownership and verification"
```

If runtime evidence was regenerated successfully:

```bash
git add screenshots data
git commit -m "chore(evidence): refresh stage2 runtime outputs"
```

- [ ] **Step 3: Confirm remote head**

```bash
git fetch origin pull/10/head:refs/remotes/origin/pr-10-before-push
git log --oneline HEAD..refs/remotes/origin/pr-10-before-push
```

Expected: no unreviewed remote commits; stop and reconcile if any exist.

- [ ] **Step 4: Push without force**

```bash
git push origin HEAD:feature/truc/kafka-spark-stage2
```

Expected: normal fast-forward push only.

- [ ] **Step 5: Verify PR head**

```bash
gh pr view 10 --repo emanhthangngot/lab04-datasets-cpg --json headRefOid,reviewDecision,statusCheckRollup
```

Expected: PR head equals pushed commit and checks are visible.

## Self-Review

- [x] Spec coverage: credentials, evidence validity, Spark actions, ownership, tracker accuracy, tests, E2E, and safe push all have tasks.
- [x] Shared Graph Stores execution is retained while Thanh owns acceptance.
- [x] Commands include expected outcomes and do not fabricate runtime output.
- [x] Existing untracked `docs/superpowers/` files are protected from accidental staging.