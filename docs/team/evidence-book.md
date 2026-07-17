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

- [ ] Execute the canonical `book/task6_replay.ipynb` against the strict Stage 3 manifest.
- [ ] Embed Neo4j Browser and Mongo Express replay screenshots.
- [ ] Re-execute canonical Task 1-6 notebooks after the fresh evidence run.
- [ ] Complete Task 6 and final chapter reflections.
- [ ] Build the book locally and fix broken links.

Done when:

- All six task chapters contain executed output and reflection.
- Architecture and Reflection pages are complete.
- `jupyter-book build book/` succeeds locally.

Spec input to Tri:

- Broken links or missing screenshots.
- Any limitation that should be stated honestly in the final Reflection.

## Stage 4: Publication Review

Tasks:

- [ ] Confirm GitHub Pages workflow has published the latest book from `main`.
- [ ] Open the root Pages URL and every chapter.
- [ ] Confirm repository links are visible from the book.
- [ ] Confirm final Moodle URL with Tri.

Done when:

- Tri approves the GitHub Pages URL as the only Moodle submission value.

## Latest Update

Status: Stage 2 Task 1-5 executed chapters, query evidence, manifest, and
architecture are complete. Task 6 replay and publication remain Stage 3/4.

Next action: implement and capture Task 6 replay, then verify the published book.

Evidence links:

- [_toc.yml](../../book/_toc.yml)
- [index.md](../../book/index.md)
- [task1_repository.md](../../book/task1_repository.md) through [task6_replay.md](../../book/task6_replay.md)
- [01_repository_discovery.ipynb](../../notebooks/01_repository_discovery.ipynb) through [06_idempotent_replay.ipynb](../../notebooks/06_idempotent_replay.ipynb)
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

- Runtime evidence is still pending for Stage 2 and Stage 3.
- `bash scripts/run_checks.sh` still requires a working Bash runtime on this
  Windows machine; use `.\scripts\run_checks.ps1` for local Windows scaffold
  validation until WSL or another Bash runtime is installed.
