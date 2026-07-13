# Stage 2 Blocker Remediation Design

## Goal

Bring Truc's Stage 2 Kafka/Spark pull request to an approvable state by fixing
the remaining standards, evidence, validation, and code-quality findings while
preserving a shared end-to-end runbook for the whole team.

## Current State

Pull request #10 targets `dev` from `feature/truc/kafka-spark-stage2`. The
current reviewed head is `21ea59bbfb762876552491e35e552719321b6b03`.

The previous review confirmed that Truc already provides:

- all four explicit `cpg.*` topics and real sample messages;
- a real `cpg.errors` event with `status = "failed"`;
- Neo4j connector class, version, registration, and running-status evidence;
- Spark metadata consumption, checkpoint offsets, and MongoDB metadata output;
- valid, credential-redacted connector JSON artifacts; and
- repository-relative evidence links in the Kafka/Spark tracker.

The remaining work is focused on hard-coded credentials, inconsistent test
counts, validation that warns instead of failing, two unresolved code-quality
comments, stale runbook instructions, evidence hygiene, and an ambiguous
cross-owner verification gate.

## Ownership Model

Truc owns the execution and maintainability of the shared Stage 2 end-to-end
runbook. The runbook continues to execute Kafka, Spark, Neo4j, and MongoDB
checks so every team member can reproduce the complete sample pipeline.

Thanh remains the acceptance owner for Graph Stores. Truc running Neo4j and
MongoDB commands does not transfer tasks 2.3 through 2.6 to Truc. Thanh must:

1. recheck the Neo4j constraints, node/edge/placeholder counts, and duplicate
   node/edge results emitted by Truc's runbook;
2. recheck the MongoDB metadata count, sample document, and duplicate
   `file_id` aggregation;
3. confirm that the queries match the Graph Stores specification; and
4. record approval or a blocker in `docs/team/graph-stores.md` before Tri
   approves Truc's pull request.

Tri owns the final merge gate. The ownership rule will be recorded in
`docs/team/workplan.md`, Truc's tracker, and Thanh's tracker.

## Design

### Shared End-to-End Runbook

`scripts/run_stage2_evidence.sh` remains the single shared orchestration entry
point. It keeps the Neo4j constraint, count, duplicate, and MongoDB verification
steps because these outputs are useful for whole-pipeline testing.

The runbook will:

- remove literal database passwords from commands and require
  `NEO4J_PASSWORD` to be supplied through the environment; the script exits
  before starting services when the variable is absent;
- keep Truc's Kafka, connector, parser, Spark, and evidence steps;
- keep the Graph Stores checks but label their results as requiring Thanh's
  acceptance review;
- remove stale instructions to open a pull request that already exists; and
- exit unsuccessfully when a required evidence step fails.

### Kafka Evidence Validation

`scripts/capture_kafka_evidence.sh` will treat evidence validity as a gate, not
an informational warning.

For every required topic, the script must fail when no message is captured,
when a line is not JSON, or when required fields are absent. Node and edge
samples must contain an object-valued `properties` field. Error samples must
contain `status = "failed"`. The script must not replace a missing sample with a
synthetic note that could be mistaken for runtime evidence.

### Connector Evidence and Credential Hygiene

Connector JSON responses remain separate from human-readable logs. Each JSON
artifact must pass `python -m json.tool` after generation. Sanitization must
occur at the evidence boundary and must never turn invalid JSON into apparently
successful output.

Credential handling will use the required `NEO4J_PASSWORD` environment
variable. Evidence may contain `***REDACTED***`, but source and generated
evidence must not expose the supplied password. The duplicated sanitization
loops will be replaced by one helper script invoked by both capture paths.

### Spark Micro-Batch Processing

`spark_jobs/metadata_stream_to_mongo.py` currently counts a batch and then
writes it, causing Spark to evaluate the same micro-batch twice. The batch will
be persisted before the count and unpersisted in a `finally` block after the
write. This retains the useful document-count log while preventing redundant
recomputation and ensuring cached data is released on write failure.

### Tests and Tracker Accuracy

The unused `tree = ast.parse(...)` assignment in
`tests/test_kafka_spark_stage2.py` will be removed while retaining the parse
check.

Tests will cover the observable contracts introduced by this remediation:

- Kafka capture fails for missing messages, invalid JSON, missing required
  fields, invalid `properties`, and non-failed error events;
- the runbook contains the shared Graph Stores checks without embedding a
  literal Neo4j password;
- connector evidence files are machine-readable JSON;
- Spark persists and releases a counted micro-batch; and
- workplan and trackers encode Truc execution, Thanh acceptance, and Tri merge
  ownership consistently.

`docs/team/kafka-spark.md` will report exactly the test count produced by the
final verified run. Task 1.2 will remain historically accurate: the pre-edit
checks were missed, the current checks were rerun, and Tri accepts that miss as
a documented waiver rather than rewriting history.

## Error Handling

Required capture and validation commands run under shell strict mode. A missing
service, empty required topic, invalid artifact, failed query, or failed test
must stop the workflow with a non-zero exit code. No generated runtime result
will be fabricated or manually rewritten to make a gate pass.

If Docker or a required service is unavailable, the blocker is recorded with
the attempted command and error output. Previously committed runtime evidence
is not presented as evidence from the new run.

Before pushing, the remote branch head must be fetched and compared with the
starting head. New remote commits stop the push until they are reviewed and
integrated without force-pushing.

## Verification Strategy

Static verification includes:

- `bash -n` for all shell scripts;
- `python -m compileall` for parser, Spark, and test code;
- `docker compose config --quiet`;
- `git diff --check`;
- JSON parsing for document artifacts and per-line parsing for JSON Lines
  samples; and
- a credential scan over changed source and evidence.

Automated verification includes the complete pytest suite and
`bash scripts/run_checks.sh`. Tests added by this remediation are run first as
focused tests and then as part of the full suite.

Runtime verification uses `bash scripts/run_stage2_evidence.sh` when Docker and
all required services are available. It verifies four Kafka samples, a running
connector and task, a committed Spark metadata offset, MongoDB metadata, and
the Graph Stores evidence that Thanh must recheck.

## Commit and Push Strategy

Implementation commits will be small and reviewable:

1. tests and fail-fast evidence behavior;
2. Spark and credential/runbook fixes;
3. ownership and tracker documentation; and
4. regenerated evidence only when produced by a successful runtime run.

The branch will be pushed normally to `feature/truc/kafka-spark-stage2`; force
push is prohibited. The pull request head and checks will be read back after
the push.

## Definition of Done

The remediation is complete when:

- every currently identified blocker and applicable Copilot comment is fixed;
- all available static, focused, full-suite, and Compose checks pass;
- runtime evidence is regenerated only by a successful end-to-end run, or an
  honest Docker/service blocker is recorded;
- the tracker contains one verified test count;
- no literal credential is introduced in changed runbook or evidence content;
- Truc's execution ownership and Thanh's Graph Stores acceptance ownership are
  documented consistently in all three team documents;
- Thanh has a concrete recheck checklist for evidence from Truc's runbook;
- the final diff contains no unrelated user files; and
- the remote branch is unchanged immediately before a normal push.
