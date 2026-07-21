# Proposal: Stage 2 Team Handoff

## Intent

Move from Tri-owned Stage 1 schema/spec locking into Stage 2 parallel work for
Truc, Thanh, and Tuan without allowing downstream schema drift.

## Scope

In scope:

- Assign Kafka/Spark runtime readiness and evidence to Truc.
- Assign Neo4j/MongoDB validation and duplicate checks to Thanh.
- Assign notebook, screenshot, and Jupyter Book evidence mapping to Tuan.
- Require each member to read specs and tasks before implementation.
- Require tracker updates and command evidence before PR review.

Out of scope:

- Changing the Stage 1 JSON Schema contract.
- Replacing Docker Compose runtime architecture.
- Publishing GitHub Pages.
- Dropping databases, pruning Docker volumes, or changing shared connectors
  without Tri approval.

## Owners

- Tri: spec approval, PR review, merge control.
- Truc: Kafka/Spark runtime and evidence.
- Thanh: Neo4j/MongoDB stores and replay duplicate checks.
- Tuan: notebooks, screenshots, and Jupyter Book evidence.

## Success Criteria

- Every owner has a clear base spec and task checklist.
- README explains the task intake workflow and required commands.
- Workplan links each owner to the matching spec and tracker.
- Existing scaffold checks still pass.
