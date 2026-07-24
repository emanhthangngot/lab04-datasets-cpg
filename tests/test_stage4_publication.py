from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "publish-book.yml"
BOOK = ROOT / "book"
FINAL_SPEC = ROOT / "openspec" / "specs" / "final-publication" / "spec.md"
COMPOSE = ROOT / "docker-compose.yml"


def _notebook_source(name: str) -> str:
    notebook = json.loads((BOOK / name).read_text(encoding="utf-8"))
    return "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"])


def _notebook_output(name: str) -> str:
    notebook = json.loads((BOOK / name).read_text(encoding="utf-8"))
    return "\n".join(
        "".join(item.get("text", []))
        for cell in notebook["cells"]
        for item in cell.get("outputs", [])
    )


def test_publication_workflow_is_pinned_and_fail_fast() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")

    assert 'python-version: "3.11"' in source
    assert "python -m pip install -r requirements.txt" in source
    assert "pip install -U jupyter-book" not in source
    assert "test -f book/_build/html/index.html" in source
    assert source.count("peaceiris/actions-gh-pages@v4") == 1

    tests = source.index("python -m pytest")
    evidence = source.index("stage2_evidence_manifest.py validate")
    replay = source.index("stage3_replay_manifest.py validate")
    build = source.index("jupyter-book build book/")
    html_gate = source.index("test -f book/_build/html/index.html")
    deploy = source.index("peaceiris/actions-gh-pages@v4")
    assert tests < evidence < replay < build < html_gate < deploy


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


def test_kafka_chapter_renders_real_message_samples() -> None:
    task3 = _notebook_source("task3_kafka.ipynb")
    notebook = json.loads((BOOK / "task3_kafka.ipynb").read_text(encoding="utf-8"))
    output = "\n".join(
        "".join(item.get("text", []))
        for cell in notebook["cells"]
        for item in cell.get("outputs", [])
    )

    for topic, filename in {
        "cpg.nodes": "sample_cpg_nodes.json",
        "cpg.edges": "sample_cpg_edges.json",
        "cpg.metadata": "sample_cpg_metadata.json",
        "cpg.errors": "sample_cpg_errors.json",
    }.items():
        assert f"../screenshots/kafka/{filename}" in task3
        assert f"{topic} sample:" in output

    assert '"schema_version": "1.0"' in output
    assert '"event_time":' in output


def test_store_chapter_dates_match_replay_evidence() -> None:
    metadata = json.loads(
        (ROOT / "screenshots" / "replay" / "evidence_metadata.json").read_text(
            encoding="utf-8"
        )
    )
    expected = f"| Run date | `{metadata['run_date']}` |"

    assert expected in _notebook_source("task4_neo4j.ipynb")
    assert expected in _notebook_source("task5_mongodb.ipynb")


def test_neo4j_healthcheck_uses_the_configured_password() -> None:
    compose = COMPOSE.read_text(encoding="utf-8")

    assert 'LAB04_NEO4J_PASSWORD: "${NEO4J_PASSWORD:-password}"' in compose
    assert '-p \\"$${LAB04_NEO4J_PASSWORD}\\"' in compose
    assert '      NEO4J_PASSWORD: "${NEO4J_PASSWORD:-password}"' not in compose
    assert "-p password 'RETURN 1'" not in compose


def test_public_book_uses_password_placeholder() -> None:
    architecture = (BOOK / "architecture.md").read_text(encoding="utf-8")

    assert "NEO4J_PASSWORD=<local-lab-password>" in architecture
    assert "NEO4J_PASSWORD=password" not in architecture


def test_architecture_explicitly_shows_required_routes_and_correct_ports() -> None:
    architecture = (BOOK / "architecture.md").read_text(encoding="utf-8")
    diagram = (BOOK / "_static" / "cpg_pipeline.svg").read_text(encoding="utf-8")

    assert "_static/cpg_pipeline.svg" in architecture
    assert "Kafka Connect" in diagram
    assert "Neo4j Sink Connector" in diagram
    assert "Structured Streaming" in diagram
    assert "cpg.nodes" in diagram and "cpg.edges" in diagram
    assert "cpg.metadata" in diagram and "cpg.errors" in diagram
    assert "`29092` host / `9092` Compose" in architecture


def test_final_publication_spec_covers_every_task_chapter_contract() -> None:
    spec = FINAL_SPEC.read_text(encoding="utf-8")

    assert "Every Task Chapter Satisfies The Submission Rubric" in spec
    for requirement in (
        "approach and reasoning",
        "real executed notebook output",
        "database UI screenshot or embedded figure",
        "ends with a brief reflection",
        "what worked, what failed, and how the issue was resolved",
        "run instructions",
    ):
        assert requirement in spec


def test_final_publication_spec_covers_architecture_and_repository_contracts() -> None:
    spec = FINAL_SPEC.read_text(encoding="utf-8")

    assert "Architecture Diagram Is Grading-Ready" in spec
    assert "Public Repository Is Submission-Complete" in spec
    for requirement in (
        "owned by the team",
        "all source code written by the team",
        "logical folder structure",
        "meaningful incremental commit messages",
        "clear code comments",
        "necessary files, logs, and screenshots",
    ):
        assert requirement in spec


def test_final_publication_spec_requires_moodle_submission_before_completion() -> None:
    spec = FINAL_SPEC.read_text(encoding="utf-8")

    assert "Publication, Submission, And Completion Are Distinct States" in spec
    assert "PUBLICATION_DEPLOYED" in spec
    assert "SUBMISSION_RECORDED" in spec
    assert "COMPLETE" in spec
    assert "submission date" in spec
    assert "exact submitted root URL" in spec
    assert "screenshot or receipt is not required" in spec


def test_repository_records_moodle_as_pending_until_manual_submission() -> None:
    workplan = (ROOT / "docs" / "team" / "workplan.md").read_text(encoding="utf-8")
    index = (BOOK / "index.md").read_text(encoding="utf-8")

    assert "- [ ] Submit only the Pages root URL to Moodle" in workplan
    assert "- Status: `PENDING`" in workplan
    assert "- Submission date: `PENDING`" in workplan
    assert "- Exact submitted root URL: `PENDING`" in workplan
    assert "whole assignment is not `COMPLETE`" in workplan
    assert "Whole-assignment completion remains pending" in index


def test_all_task_chapters_have_executed_outputs_and_closing_reflections() -> None:
    chapters = (
        "task1_repository.ipynb",
        "task2_parser.ipynb",
        "task3_kafka.ipynb",
        "task4_neo4j.ipynb",
        "task5_mongodb.ipynb",
        "task6_replay.ipynb",
    )

    for chapter in chapters:
        notebook = json.loads((BOOK / chapter).read_text(encoding="utf-8"))
        source = "\n".join(
            "".join(cell.get("source", [])) for cell in notebook["cells"]
        ).lower()
        executed = [
            cell
            for cell in notebook["cells"]
            if cell["cell_type"] == "code"
            and cell.get("execution_count") is not None
            and cell.get("outputs")
        ]

        assert executed, f"{chapter} has no real executed output"
        assert "## approach and reasoning" in source
        assert "## reflection" in source
        assert "command:" in source or ".sh" in source, (
            f"{chapter} has no task run command"
        )
        assert "worked" in source
        assert "failed" in source
        assert "resolution" in source

    for chapter in (
        "task4_neo4j.ipynb",
        "task5_mongodb.ipynb",
        "task6_replay.ipynb",
    ):
        assert ".png" in _notebook_source(chapter), (
            f"{chapter} has no applicable database UI figure"
        )


def test_all_task_chapters_use_consistent_evidence_format() -> None:
    chapters = (
        "task1_repository.ipynb",
        "task2_parser.ipynb",
        "task3_kafka.ipynb",
        "task4_neo4j.ipynb",
        "task5_mongodb.ipynb",
        "task6_replay.ipynb",
    )

    for chapter in chapters:
        source = _notebook_source(chapter)

        assert "```{admonition} Evidence summary" in source
        assert "## What this chapter proves" in source
        assert "```{admonition} Closing reflection" in source

    for chapter in (
        "task4_neo4j.ipynb",
        "task5_mongodb.ipynb",
        "task6_replay.ipynb",
    ):
        assert "```{admonition} Database UI evidence" in _notebook_source(chapter)


def test_all_task_chapters_use_reviewable_hybrid_source_excerpts() -> None:
    expected_sources = {
        "task1_repository.ipynb": (
            "../scripts/clone_repo.sh",
            "../parser_service/discover.py",
        ),
        "task2_parser.ipynb": (
            "../parser_service/parser.py",
            "../parser_service/ids.py",
        ),
        "task3_kafka.ipynb": (
            "../scripts/init_kafka_topics.sh",
            "../parser_service/schemas.py",
        ),
        "task4_neo4j.ipynb": ("../neo4j/verification.cypher",),
        "task5_mongodb.ipynb": (
            "../spark_jobs/metadata_stream_to_mongo.py",
        ),
        "task6_replay.ipynb": (
            "../scripts/run_stage3_evidence.sh",
            "../neo4j/cleanup_stale.cypher",
        ),
    }

    for chapter, paths in expected_sources.items():
        source = _notebook_source(chapter)
        assert "## Key implementation excerpts" in source
        for relative_path in paths:
            directive = f"```{{literalinclude}} {relative_path}"
            assert directive in source, f"{chapter} does not show {relative_path}"

        included = re.findall(r"\{literalinclude\}\s+([^\n]+)", source)
        for relative_path in included:
            assert (BOOK / relative_path).resolve().is_file(), (
                f"{chapter} includes missing source {relative_path}"
            )


def test_hybrid_evidence_cells_expose_raw_proof_instead_of_only_manifests() -> None:
    expected_output = {
        "task2_parser.ipynb": (
            "metadata sample:",
            "stable identity proof:",
        ),
        "task4_neo4j.ipynb": (
            "connector status: RUNNING",
            "raw Neo4j query evidence:",
        ),
        "task5_mongodb.ipynb": (
            "raw MongoDB query evidence:",
            "checkpoint offsets:",
        ),
        "task6_replay.ipynb": ("source patch:",),
    }

    for chapter, markers in expected_output.items():
        output = _notebook_output(chapter)
        for marker in markers:
            assert marker in output, f"{chapter} output does not contain {marker}"


def test_every_notebook_code_cell_is_executed_visible_and_error_free() -> None:
    for path in sorted(BOOK.glob("task*.ipynb")):
        notebook = json.loads(path.read_text(encoding="utf-8"))
        code_cells = [
            cell for cell in notebook["cells"] if cell["cell_type"] == "code"
        ]
        assert code_cells, f"{path.name} contains no code cells"

        for cell in code_cells:
            assert cell.get("execution_count") is not None
            assert cell.get("outputs")
            assert all(
                output.get("output_type") != "error"
                for output in cell.get("outputs", [])
            )
            tags = cell.get("metadata", {}).get("tags", [])
            assert "remove-input" not in tags
            assert "hide-input" not in tags


def test_publication_workflow_watches_hybrid_source_and_contract_inputs() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    for tracked_input in (
        '      - "parser_service/**"',
        '      - "spark_jobs/**"',
        '      - "scripts/**"',
        '      - "neo4j/**"',
        '      - "mongodb/**"',
        '      - "schemas/**"',
        '      - "docker-compose.yml"',
        '      - "tests/**"',
        '      - "pyproject.toml"',
        '      - "README.md"',
        '      - "docs/**"',
        '      - "openspec/**"',
    ):
        assert tracked_input in source


def test_public_contract_requires_hybrid_source_and_raw_evidence() -> None:
    spec = FINAL_SPEC.read_text(encoding="utf-8").lower()

    assert "source excerpt" in spec
    assert "raw evidence" in spec
    assert "without duplicating the complete implementation" in spec


def test_compose_documentation_describes_the_full_selected_source_run() -> None:
    compose = COMPOSE.read_text(encoding="utf-8")

    assert "full selected-source Stage 2 ingestion" in compose
    assert "Five-file Stage 2 ingestion" not in compose
    assert "selected-file Stage 2 ingestion" not in compose
