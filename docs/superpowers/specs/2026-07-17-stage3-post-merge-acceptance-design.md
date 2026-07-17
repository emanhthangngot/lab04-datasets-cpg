# Stage 3 Post-Merge Acceptance Design

## Purpose

Stage 3 implementation and canonical evidence are complete, but the current
specification does not fully define how Truc, Thanh, and Tuan independently
accept the merged result. This design makes those reviews mandatory, auditable,
and separate from Stage 4 publication.

## Source Of Truth

The active OpenSpec change `stage3-replay-hardening` remains the only normative
Stage 3 specification. Owner trackers explain how to execute their assigned
requirements, but they do not override OpenSpec counts, artifact names, or
acceptance criteria.

Post-merge acceptance starts only after the implementation PR is merged into
`dev`. Each owner branches from the updated `origin/dev`, changes only their
assigned tracker or a necessary corrective fix, and opens a separate PR back to
`dev`.

## Required Acceptance PRs

### 1. Truc — Windows Runtime Acceptance

Branch: `test/truc/stage3-windows-acceptance`.

Truc runs the PowerShell wrapper from a disposable clean clone or worktree on
Windows with Docker Desktop and Git Bash. The run must not replace the canonical
evidence already committed to `dev`.

Required command:

```powershell
git switch dev
git pull --ff-only origin dev
$password = Read-Host "Neo4j password" -AsSecureString
./scripts/run_stage3_evidence.ps1 `
  -ResetDockerState `
  -Neo4jPassword $password
```

Required acceptance record in `docs/team/kafka-spark.md`:

- Windows, PowerShell, Docker Desktop, and Git Bash versions;
- command and exit code;
- Spark metadata offsets `5 -> 5 -> 6`;
- Kafka deltas `23 nodes, 16 edges, 1 metadata, 0 errors`;
- confirmation that the password was not printed;
- confirmation that `src/datasets/__init__.py` was restored;
- either `APPROVED` or a concrete blocker with error output.

The PR is accepted by Tri. A failed run must not update canonical replay
artifacts or mark the Windows gate complete.

### 2. Thanh — Store Evidence Acceptance

Branch: `review/thanh/stage3-store-acceptance`.

Thanh validates the committed strict manifest and independently reviews the
Neo4j/MongoDB JSON and UI evidence. Re-running the destructive canonical
workflow is not required unless the manifest or artifacts disagree.

Required commands:

```bash
git switch dev
git pull --ff-only origin dev
python scripts/stage3_replay_manifest.py validate --root .
```

Required acceptance record in `docs/team/graph-stores.md`:

- Neo4j baseline `19/15`, pre-cleanup `26/18`, stale `3/2`, and final `23/16`;
- final stale counts, duplicate groups, and old-run entities are all zero;
- MongoDB remains at five distinct documents with four unchanged documents;
- target `file_id`, replay `run_id`, and counts agree across JSON and both UI
  screenshots;
- manifest validation returns `stage=3, status=pass`;
- either `APPROVED` or a concrete blocker naming the conflicting artifact.

The PR is accepted by Tri. Thanh must not edit expected counts to make a failed
artifact pass.

### 3. Tuan — Book Acceptance

Branch: `review/tuan/stage3-book-acceptance`.

Tuan reviews the committed Task 1-6 outputs and builds the book from updated
`dev`. The review consumes committed evidence and does not require live Docker
services.

Required commands:

```bash
git switch dev
git pull --ff-only origin dev
bash scripts/run_checks.sh
python scripts/stage3_replay_manifest.py validate --root .
jupyter-book clean book
jupyter-book build book
```

Required acceptance record in `docs/team/evidence-book.md`:

- all six canonical notebooks contain executed output;
- Task 6 reads the strict manifest and embeds both UI screenshots;
- Task 6 explains event counts, unique IDs, stale cleanup, checkpoint resume,
  and MongoDB replacement without describing replay events as duplicates;
- Architecture and Reflection contain no pending evidence claims;
- the clean book build succeeds without live Docker services;
- either `APPROVED` or a concrete blocker naming the page or artifact.

The PR is accepted by Tri. GitHub Pages verification is explicitly excluded and
remains Stage 4 work.

## Merge Order And Final Gate

Acceptance PRs merge in this order:

1. Truc Windows runtime acceptance;
2. Thanh store evidence acceptance;
3. Tuan book acceptance.

Later owners rebase or update from the latest `origin/dev` before requesting
review. An owner may prepare a PR early, but Tri does not merge it out of order.

After all three PRs merge, Tri:

1. reviews the three tracker records;
2. runs `openspec validate --all --strict` and `bash scripts/run_checks.sh`;
3. marks the shared PowerShell and Stage 3 acceptance gates complete;
4. records Stage 3 acceptance in `docs/team/workplan.md`;
5. archives `stage3-replay-hardening`;
6. starts Stage 4 without merging `dev` to `main` as part of Stage 3.

## Failure And Change Control

- A blocker PR records observed output but does not mark acceptance complete.
- Any corrective code change requires its own tests and must regenerate the
  strict manifest only when a hashed canonical artifact changes.
- A Windows smoke run in a disposable workspace is verification evidence, not a
  replacement canonical run.
- No owner may alter fixed counts, dataset commit, replay target, artifact names,
  or schema version without a new OpenSpec change approved by Tri.
- Tracker-only acceptance PRs must not contain generated book output, local
  datasets, secrets, checkpoints, or unrelated source changes.

## Specification Changes To Apply

Implementation of this design updates:

- OpenSpec delta specs with owner acceptance scenarios and merge-order gates;
- `openspec/changes/stage3-replay-hardening/tasks.md` with three post-merge PR
  tasks and explicit final-gate dependencies;
- `docs/team/workplan.md` with the acceptance sequence and PR naming;
- `docs/team/kafka-spark.md`, `docs/team/graph-stores.md`, and
  `docs/team/evidence-book.md` with exact commands and sign-off templates;
- the Stage 3 implementation plan so future agents do not treat implementation
  completion as owner acceptance.

No runtime code, canonical counts, or committed replay artifacts change as part
of this specification improvement.
