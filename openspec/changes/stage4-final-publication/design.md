# Stage 4 Final Publication Design

## Context

The repository uses `dev` as the integration branch and `main` as the public
publication branch. `peaceiris/actions-gh-pages@v4` publishes
`book/_build/html` to `gh-pages` after a push to `main` that changes book,
notebook, screenshot, or workflow paths.

The current book builds locally with Jupyter Book 1.0.3. The previous GitHub
Actions run installed Jupyter Book 2.1.6 through `pip install -U jupyter-book`,
failed to create `book/_build/html`, and then failed deployment. Pages is not
configured and the intended public URL returns `404`.

## Goals

- Produce a deterministic publication build from accepted committed evidence.
- Preserve the existing branch and evidence history.
- Make release failure explicit before Moodle submission.
- Keep the process executable by one person from start to finish.

## Non-Goals

- Re-run the destructive Stage 3 workflow by default.
- Change runtime architecture or evidence metrics.
- Create a new documentation framework.
- Add multi-person approvals or ownership matrices.
- Automate Moodle submission.

## Release Architecture

```text
clean dev checkout
  -> publication/content fixes
  -> local release gates
  -> reviewed dev-to-main PR
  -> push/merge on main
  -> GitHub Actions with Jupyter Book 1.0.3
  -> book/_build/html existence gate
  -> gh-pages deployment
  -> Pages source configuration
  -> nine-page live acceptance
  -> Stage 4 acceptance + OpenSpec archive
  -> Moodle root URL
```

## Design Decisions

### Deterministic Build Dependency

The workflow SHALL install the locked repository requirements or explicitly
install `jupyter-book==1.0.3`. It SHALL NOT use an unbounded upgrade command.
The build step SHALL fail when `book/_build/html/index.html` is absent.

Branch-based deployment through `peaceiris/actions-gh-pages@v4` remains the
minimal accepted design. Migrating to the official Pages artifact workflow is
allowed only as a deliberate replacement, not alongside the branch workflow.

### Evidence Is Consumed, Not Regenerated

The Pages build keeps notebook execution disabled and consumes committed
executed outputs and manifest-backed artifacts. Live Docker, Kafka, Spark,
Neo4j, and MongoDB are not dependencies of the publication job.

Final store queries may be re-run for review. Existing Stage 3 artifacts SHALL
not be regenerated unless a real mismatch requires a new canonical evidence
run and manifest update.

### Public Content Reconciliation

Before release, the executor audits all public-facing instructions and book
content. At minimum:

- remove or rewrite stale scaffold/TODO claims that contradict completion;
- remove references to missing `.codex/scripts/doctor.sh`, `notebooks/`, and
  obsolete active OpenSpec task paths;
- use placeholders rather than literal password assignments in the book;
- preserve honest parser limitations in Reflection;
- ensure Task 4 and Task 5 show or link real, accurately labeled database UI
  evidence.

### Safe Main Integration

`main` contains commits not reachable from `dev`, so Stage 4 SHALL use a normal
reviewed PR/merge. No force-push, hard reset, or branch replacement is allowed.
The executor reviews the final PR diff and merge result before relying on the
publication workflow.

### Live Acceptance Is Authoritative

Local success is necessary but not sufficient. Stage 4 is complete only when
the public root and all eight chapter pages load from GitHub Pages, navigation
and assets work, repository links target `main`, and the deployed content
matches the final main commit.

Checklist items in `book/index.md` and team tracking documents remain unchecked
until this live verification completes.

## Files Expected To Change

| Path | Purpose |
|---|---|
| `.github/workflows/publish-book.yml` | Pin build dependency; assert HTML; deploy |
| `README.md` | Replace stale scaffold and broken-path instructions |
| `book/architecture.md` | Remove literal credential example |
| `book/task4_neo4j.ipynb` | Add/verify Neo4j UI evidence and final review |
| `book/task5_mongodb.ipynb` | Add/verify MongoDB UI evidence and final review |
| `book/index.md` | Record Pages completion only after live acceptance |
| `docs/team/workplan.md` | Record Stage 4 final acceptance |
| `docs/team/evidence-book.md` | Record publication review |
| `docs/team/kafka-spark.md` | Record final runtime/evidence review without owner split |
| `docs/team/graph-stores.md` | Record final store/evidence review without owner split |
| `tests/` | Add focused publication/static-contract tests as needed |

The executor may touch other public docs only when the audit proves they are
stale or broken. Runtime implementation files remain unchanged unless a final
gate exposes a real defect.

## Validation Strategy

### Static And Contract Gates

```bash
git diff --check
openspec validate --all --strict
python scripts/stage3_replay_manifest.py validate --root .
bash scripts/run_checks.sh
docker compose config
python -m json.tool neo4j/sink_connector.json
bash -n scripts/*.sh
```

PowerShell syntax is validated on a PowerShell-capable environment or through
the previously accepted Windows record when no `.ps1` file changes.

### Publication Gates

```bash
jupyter-book clean book/
jupyter-book build book/
test -f book/_build/html/index.html
```

Additionally scan public files for credentials, tokens, private paths, broken
local links, stale pending markers, and tracked generated output.

### Live Pages Matrix

Verify HTTP success and visual/content correctness for:

- `/`
- `/architecture.html`
- `/task1_repository.html`
- `/task2_parser.html`
- `/task3_kafka.html`
- `/task4_neo4j.html`
- `/task5_mongodb.html`
- `/task6_replay.html`
- `/reflection.html`

For each page verify navigation, executed outputs, images, repository link,
layout, and public-data safety.

## Failure Handling

- Workflow build failure: stop; do not configure/submit Pages as complete.
- Deployment failure: inspect Actions logs and fix through a new `dev` PR.
- Pages `404`: verify successful `gh-pages` creation and repository Pages source.
- Missing/broken image: fix source reference and rebuild before republishing.
- Evidence mismatch: stop; do not edit constants. Decide whether text is wrong
  or a canonical evidence rerun is required.
- Secret/private path: remove or replace the artifact, rebuild, and republish.

## Completion Boundary

Stage 4 ends after live acceptance is recorded and this change is archived.
Moodle receives only:

```text
https://emanhthangngot.github.io/lab04-datasets-cpg/
```
