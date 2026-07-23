import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "book"


def _notebook(task: int, slug: str) -> dict:
    path = BOOK / f"task{task}_{slug}.ipynb"
    assert path.is_file(), f"missing canonical chapter: {path.relative_to(ROOT)}"
    return json.loads(path.read_text())


def test_tasks_1_to_5_are_canonical_executed_notebooks() -> None:
    slugs = ("repository", "parser", "kafka", "neo4j", "mongodb")
    for task, slug in enumerate(slugs, start=1):
        notebook = _notebook(task, slug)
        code_cells = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
        assert code_cells
        assert all(cell.get("execution_count") is not None for cell in code_cells)
        assert all(cell.get("outputs") for cell in code_cells)
        source = "\n".join("".join(cell["source"]) for cell in notebook["cells"])
        assert "## Reflection" in source
        assert "screenshots/stage2_manifest.json" in source
        assert "pending" not in source.lower()
        assert not (BOOK / f"task{task}_{slug}.md").exists()


def test_duplicate_task_1_to_5_notebooks_are_removed() -> None:
    for task in range(1, 6):
        assert not list((ROOT / "notebooks").glob(f"0{task}_*.ipynb"))


def test_store_chapters_reference_real_evidence() -> None:
    neo4j = json.dumps(_notebook(4, "neo4j"))
    mongodb = json.dumps(_notebook(5, "mongodb"))
    manifest = json.loads((ROOT / "screenshots" / "stage2_manifest.json").read_text())
    assert "node_count.txt" in neo4j
    assert str(manifest["metrics"]["neo4j"]["total_nodes"]) in neo4j
    assert "metadata_evidence.txt" in mongodb
    assert str(manifest["metrics"]["mongodb"]["documents"]) in mongodb


def test_architecture_page_embeds_editable_diagram_and_explains_routes() -> None:
    source = (BOOK / "architecture.md").read_text()
    assert "_static/cpg_pipeline.svg" in source
    assert (BOOK / "_static" / "cpg_pipeline.svg").is_file()
    assert "Spark is not between Kafka and Neo4j" in source
    assert "Pending" not in source


def test_task_6_is_a_canonical_manifest_backed_notebook() -> None:
    notebook = _notebook(6, "replay")
    source = "\n".join("".join(cell["source"]) for cell in notebook["cells"])
    assert "stage3_replay_manifest.json" in source
    assert "neo4j_after_cleanup.png" in source
    assert "mongodb_after_replay.png" in source
    assert "## Reflection" in source
    assert "pending" not in source.lower()
    assert not (BOOK / "task6_replay.md").exists()
    assert not (ROOT / "notebooks" / "06_idempotent_replay.ipynb").exists()
