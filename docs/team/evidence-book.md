# Evidence/Jupyter Book Progress Tracker

Owner: 23120185 - Nguyen Ho Anh Tuan

Role: Evidence, Notebooks, and Jupyter Book

Primary branch examples:

```text
docs/tuan/task1-notebook
docs/tuan/task4-neo4j-screenshot
docs/tuan/final-book-review
```

## Working Rules

- Receive tasks only from [workplan.md](workplan.md).
- Implement from specs written by Le Xuan Tri.
- Do not create or edit spec files.
- Update this tracker before asking for PR review.
- Do not invent evidence. Only use executed notebook output and real screenshots.

## Stage 1: Book Foundation

Tasks:

- [x] Verify Jupyter Book chapter structure matches the six lab tasks.
- [x] Confirm each task has a matching notebook.
- [x] Confirm screenshot folders exist for Kafka, Neo4j, MongoDB, Spark, and replay.
- [x] Record any missing evidence slot for Tri.

Done when:

- Book skeleton has Overview, Architecture, Task 1-6, and Reflection.
- Notebook and screenshot evidence slots are mapped to chapters.

Stage 1 review result on 2026-07-05:

- `book/_toc.yml` maps Overview, Architecture, Task 1-6, and Reflection.
- `notebooks/01_repository_discovery.ipynb` through
  `notebooks/06_idempotent_replay.ipynb` exist and contain pending evidence
  metadata slots.
- `screenshots/kafka`, `screenshots/neo4j`, `screenshots/mongodb`,
  `screenshots/spark`, and `screenshots/replay` exist.
- `screenshots/README.md` defines the capture rule for task, command, run date,
  result, and source.

Spec input to Tri:

- Runtime evidence is still pending for Stage 2 and Stage 3.
- A local `.venv` with `jupyter-book==1.0.3` can build the current Stage 1
  book skeleton successfully.

## Stage 2: Core Evidence Capture

Tasks:

- [x] Add executed outputs for repository discovery.
- [x] Add parser output samples.
- [x] Add parser CFG/DFG/CALL edge count evidence from Tri.
- [x] Add Kafka message samples.
- [x] Add initial Neo4j/MongoDB evidence references from Truc and Thanh.
- [x] Keep replay slots explicit until the full replay workflow actually runs.

Done when:

- Task 1-5 chapters have real command/notebook output placeholders replaced.
- Screenshot references point to actual files when available.
- Task 6 replay evidence is either real or explicitly still pending.

Spec input to Tri:

- Evidence gaps that block chapter completion.
- Any task chapter that needs more technical explanation.

## Stage 3: Replay And Final Evidence

Tasks:

- [x] Execute the canonical `book/task6_replay.ipynb` against the strict Stage 3 manifest.
- [x] Embed Neo4j Browser and Mongo Express replay screenshots.
- [x] Re-execute canonical Task 1-6 notebooks after the fresh evidence run.
- [x] Complete Task 6 and final chapter reflections.
- [x] Build the book locally and fix broken links.

Done when:

- All six task chapters contain executed output and reflection.
- Architecture and Reflection pages are complete.
- `jupyter-book build book/` succeeds locally.

Spec input to Tri:

- Broken links or missing screenshots.
- Any limitation that should be stated honestly in the final Reflection.

## Stage 4: Publication Review

Stage 4 is no longer split by member. One executor follows the ordered
[`stage4-final-publication`](../../openspec/changes/stage4-final-publication/tasks.md)
checklist and uses this tracker only as Stage 1-3 evidence history.

Final review gates:

- [ ] Confirm GitHub Pages workflow has published the latest book from `main`.
- [ ] Open the root Pages URL and every chapter.
- [ ] Confirm repository links are visible from the book.
- [ ] Confirm the verified Pages root URL is the only Moodle value.

Done when:

- Tri approves the GitHub Pages URL as the only Moodle submission value.

## Latest Update

Status: Stage 3 Task 1-6 executed chapters, replay evidence, strict manifest,
reflection, Windows acceptance, and local Jupyter Book build are approved.
Publication workflow repair and live Pages verification remain Stage 4.

Evidence links:

- [_toc.yml](../../book/_toc.yml)
- [index.md](../../book/index.md)
- [task1_repository.ipynb](../../book/task1_repository.ipynb) through [task6_replay.ipynb](../../book/task6_replay.ipynb)
- [stage3_replay_manifest.json](../../screenshots/replay/stage3_replay_manifest.json)
- [README.md](../../screenshots/README.md)

Commands run on 2026-07-05:

| Command | Result |
|---|---|
| `git status --short --branch` | Pass: on `feature/tuan/evidence-book-stage1`, ahead of `origin/dev` with no behind commits |
| `bash scripts/run_checks.sh` | Blocked before script execution: Windows `bash.exe` points to WSL, and no WSL distro is installed. Script was hardened for public clones and Python command fallback. |
| `.\scripts\run_checks.ps1` | Pass: Codex doctor skipped as optional, 17 tests passed, Docker Compose syntax valid, JSON connector config valid |
| `$env:TMP=(Resolve-Path -LiteralPath .).Path; $env:TEMP=$env:TMP; $env:TMPDIR=$env:TMP; python -m pytest -q` | Pass: 17 tests passed |
| `docker compose config` | Pass with warning: Docker could not read the local Docker client config because access is denied |
| `python -m json.tool neo4j\sink_connector.json` | Pass |
| `.venv\Scripts\jupyter-book.exe --version` | Pass: Jupyter Book 1.0.3 |
| `$env:TMP=(Resolve-Path -LiteralPath .).Path; $env:TEMP=$env:TMP; $env:TMPDIR=$env:TMP; .venv\Scripts\python.exe -m pytest -q` | Pass: 17 tests passed |
| `$env:TMP=(Resolve-Path -LiteralPath .).Path; $env:TEMP=$env:TMP; $env:TMPDIR=$env:TMP; .venv\Scripts\jupyter-book.exe build book` | Pass: build succeeded, HTML generated under `book/_build/html` |

Blockers:

- Runtime evidence for Stage 2 and Stage 3 is captured and hash-validated.
- `bash scripts/run_checks.sh` still requires a working Bash runtime on this
  Windows machine; use `.\scripts\run_checks.ps1` for local Windows scaffold
  validation until WSL or another Bash runtime is installed.

## Post-Merge Acceptance PR

This is Tuan's mandatory Stage 3 book acceptance. Start only after Thanh's
store-acceptance PR has merged, and perform the build from the latest `dev`
without live Docker services.

```bash
git switch dev
git pull --ff-only origin dev
git switch -c review/tuan/stage3-book-acceptance
bash scripts/run_checks.sh
python scripts/stage3_replay_manifest.py validate --root .
jupyter-book clean book
jupyter-book build book
```

The tracker-only PR must record the exit code of each command and confirm that
all six task chapters have executed outputs. For Task 6, verify the strict
manifest, Neo4j and MongoDB images, replay narrative, and reflection agree with
one another. Confirm the clean book build succeeds without live Docker services
and that no generated `_build/` content is committed.

Acceptance status: `APPROVED` or `BLOCKED`

Recorded acceptance status: `APPROVED`

### Acceptance run: 2026-07-20

Branch: `review/tuan/stage3-book-acceptance`
Started from: `dev` at commit `5fd94ed`

| Command | Exit code | Result |
|---|---:|---|
| `python scripts/stage3_replay_manifest.py validate --root .` | 0 | `{"stage": 3, "status": "pass"}` |
| `.\\scripts\\run_checks.ps1` | 0 | 129 passed, 1 skipped |
| `.venv\\Scripts\\jupyter-book.exe clean book` | 0 | `_build` cleared |
| `PYTHONUTF8=1 .venv\\Scripts\\jupyter-book.exe build book` | 0 | build succeeded, no warnings |

Chapter verification (all six task chapters have executed outputs):

| Chapter | Executed cells | Reflection | Screenshots |
|---|:---:|:---:|:---:|
| task1_repository.ipynb | ✓ | ✓ | — |
| task2_parser.ipynb | ✓ | ✓ | — |
| task3_kafka.ipynb | ✓ | ✓ | — |
| task4_neo4j.ipynb | ✓ | ✓ | — |
| task5_mongodb.ipynb | ✓ | ✓ | — |
| task6_replay.ipynb | ✓ | ✓ | neo4j_after_cleanup.png, mongodb_after_replay.png |

Task 6 strict manifest verification:

- `stage3_replay_manifest.json` — status: **pass**, stage: 3
- Content hash changed: `74ab1762…` → `6db67191…`
- run_id changed: `2088754454f44aa2b4394aff0c565d49` → `stage3-replay-20260717T002053Z`
- Kafka delta: nodes +23, edges +16, metadata +1, errors 0
- Spark offsets: 5 → 5 (restart) → 6 (replay)
- Neo4j stale deleted: nodes 3, edges 2; duplicates 0
- MongoDB: 5 docs before = 5 docs after, 4 unchanged, 0 duplicates
- Both UI screenshots (PNG) are valid and present

No `_build/` content committed. Book builds cleanly from manifest without live
Docker services.
