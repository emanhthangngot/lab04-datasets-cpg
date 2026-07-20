from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "publish-book.yml"
BOOK = ROOT / "book"


def _notebook_source(name: str) -> str:
    notebook = json.loads((BOOK / name).read_text(encoding="utf-8"))
    return "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"])


def test_publication_workflow_is_pinned_and_fail_fast() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")

    assert 'python-version: "3.11"' in source
    assert "python -m pip install -r requirements.txt" in source
    assert "pip install -U jupyter-book" not in source
    assert "test -f book/_build/html/index.html" in source
    assert source.count("peaceiris/actions-gh-pages@v4") == 1

    build = source.index("jupyter-book build book/")
    html_gate = source.index("test -f book/_build/html/index.html")
    deploy = source.index("peaceiris/actions-gh-pages@v4")
    assert build < html_gate < deploy


def test_publication_workflow_watches_only_tracked_inputs() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")

    assert '      - "notebooks/**"' not in source
    for tracked_input in (
        '      - "book/**"',
        '      - "screenshots/**"',
        '      - "requirements.txt"',
        '      - ".github/workflows/publish-book.yml"',
    ):
        assert tracked_input in source


def test_book_build_contract_is_offline_and_complete() -> None:
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    config = (BOOK / "_config.yml").read_text(encoding="utf-8")
    toc = (BOOK / "_toc.yml").read_text(encoding="utf-8")

    assert "jupyter-book==1.0.3" in requirements
    assert 'execute_notebooks: "off"' in config
    for page in (
        "root: index",
        "file: architecture",
        "file: task1_repository",
        "file: task2_parser",
        "file: task3_kafka",
        "file: task4_neo4j",
        "file: task5_mongodb",
        "file: task6_replay",
        "file: reflection",
    ):
        assert page in toc


def test_public_instructions_do_not_reference_removed_paths() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    contributing = (ROOT / "docs" / "CONTRIBUTING.md").read_text(encoding="utf-8")
    security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    active_docs = readme + contributing + security

    assert ".codex/scripts/doctor.sh" not in active_docs
    assert "notebooks/" not in active_docs
    assert "openspec/changes/stage2-core-sample-pipeline" not in active_docs
    assert "This scaffold intentionally contains TODO" not in readme


def test_store_chapters_embed_real_final_state_ui_evidence() -> None:
    task4 = _notebook_source("task4_neo4j.ipynb")
    task5 = _notebook_source("task5_mongodb.ipynb")
    metadata = json.loads(
        (ROOT / "screenshots" / "replay" / "evidence_metadata.json").read_text(
            encoding="utf-8"
        )
    )
    manifest = json.loads(
        (ROOT / "screenshots" / "replay" / "stage3_replay_manifest.json").read_text(
            encoding="utf-8"
        )
    )

    assert "../screenshots/replay/neo4j_after_cleanup.png" in task4
    assert "../screenshots/replay/mongodb_after_replay.png" in task5
    assert "Stage 3" in task4 and "final" in task4.lower()
    assert "Stage 3" in task5 and "final" in task5.lower()
    assert "no UI screenshot is claimed" not in task4
    assert "could not be captured" not in task5

    assert metadata["result"] == "pass"
    for image in ("neo4j_after_cleanup.png", "mongodb_after_replay.png"):
        assert image in metadata["screenshots"]
        assert f"screenshots/replay/{image}" in manifest["artifacts"]


def test_public_book_uses_password_placeholder() -> None:
    architecture = (BOOK / "architecture.md").read_text(encoding="utf-8")

    assert "NEO4J_PASSWORD=<local-lab-password>" in architecture
    assert "NEO4J_PASSWORD=password" not in architecture

