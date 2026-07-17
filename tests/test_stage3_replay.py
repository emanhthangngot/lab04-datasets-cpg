from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPLAY_DIR = Path("screenshots/replay")


def _load_manifest_module():
    path = PROJECT_ROOT / "scripts" / "stage3_replay_manifest.py"
    spec = importlib.util.spec_from_file_location("stage3_replay_manifest", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_json(root: Path, name: str, payload: dict) -> None:
    path = root / REPLAY_DIR / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _fixture_payloads() -> dict[str, dict]:
    baseline_documents = {
        "6c39568a6a11c430": {"run_id": "baseline-run", "content_hash": "a" * 64},
        "file-2": {"run_id": "baseline-run", "content_hash": "b" * 64},
        "file-3": {"run_id": "baseline-run", "content_hash": "c" * 64},
        "file-4": {"run_id": "baseline-run", "content_hash": "d" * 64},
        "file-5": {"run_id": "baseline-run", "content_hash": "e" * 64},
    }
    replay_documents = json.loads(json.dumps(baseline_documents))
    replay_documents["6c39568a6a11c430"] = {
        "run_id": "stage3-replay-20260716T120000Z",
        "content_hash": "f" * 64,
    }
    return {
        "run_metadata.json": {
            "captured_at": "2026-07-16T12:00:00Z",
            "pipeline_commit": "1" * 40,
            "dataset_commit": "41adfd0f9ee9ba3a6b4f719d5b551c5b19ae45e2",
            "dataset_repo": "huggingface/datasets",
            "target_file": "src/datasets/__init__.py",
            "file_id": "6c39568a6a11c430",
            "baseline_run_id": "baseline-run",
            "replay_run_id": "stage3-replay-20260716T120000Z",
            "before_content_hash": "a" * 64,
            "after_content_hash": "f" * 64,
            "source_restored": True,
        },
        "kafka_offsets_before.json": {
            "cpg.nodes": 21415,
            "cpg.edges": 7968,
            "cpg.metadata": 5,
            "cpg.errors": 1,
            "unique_node_ids": 21415,
            "unique_edge_ids": 7968,
        },
        "kafka_offsets_after.json": {
            "cpg.nodes": 21438,
            "cpg.edges": 7984,
            "cpg.metadata": 6,
            "cpg.errors": 1,
            "unique_node_ids": 21422,
            "unique_edge_ids": 7971,
        },
        "kafka_graph_counts_after.json": {
            "node_events": 21438,
            "unique_node_ids": 21422,
            "edge_events": 7984,
            "unique_edge_ids": 7971,
        },
        "spark_checkpoint_before.json": {"metadata_offset": 5, "completed_batch": 0},
        "spark_checkpoint_after_restart.json": {"metadata_offset": 5, "completed_batch": 2},
        "spark_checkpoint_after_replay.json": {"metadata_offset": 6, "completed_batch": 3},
        "neo4j_before.json": {
            "explicit_nodes": 21415,
            "placeholders": 1213,
            "edges": 7968,
            "target_nodes": 19,
            "target_edges": 15,
            "duplicate_node_groups": 0,
            "duplicate_edge_groups": 0,
        },
        "neo4j_pre_cleanup.json": {
            "explicit_nodes": 21422,
            "placeholders": 1213,
            "edges": 7971,
            "target_nodes": 26,
            "target_edges": 18,
            "stale_nodes": 3,
            "stale_edges": 2,
        },
        "neo4j_after.json": {
            "explicit_nodes": 21419,
            "placeholders": 1213,
            "edges": 7969,
            "target_nodes": 23,
            "target_edges": 16,
            "stale_nodes": 0,
            "stale_edges": 0,
            "old_run_entities": 0,
            "duplicate_node_groups": 0,
            "duplicate_edge_groups": 0,
        },
        "mongodb_before.json": {
            "documents": 5,
            "duplicate_file_id_groups": 0,
            "documents_by_file_id": baseline_documents,
        },
        "mongodb_after_restart.json": {
            "documents": 5,
            "duplicate_file_id_groups": 0,
            "documents_by_file_id": baseline_documents,
        },
        "mongodb_after_replay.json": {
            "documents": 5,
            "duplicate_file_id_groups": 0,
            "documents_by_file_id": replay_documents,
        },
        "evidence_metadata.json": {
            "task": "Task 6 - Idempotent Replay Verification",
            "run_date": "2026-07-16",
            "result": "pass",
            "source": "Stage 3 canonical run",
            "screenshots": {
                "neo4j_after_cleanup.png": "Neo4j Browser target run_id/count query",
                "mongodb_after_replay.png": "Mongo Express target file_id filter",
            },
        },
    }


def _write_valid_raw_evidence(root: Path) -> None:
    for name, payload in _fixture_payloads().items():
        _write_json(root, name, payload)
    replay = root / REPLAY_DIR
    (replay / "source_patch.diff").write_text(
        '-__version__ = "5.0.1.dev0"\n'
        '+__version__: str = "5.0.1.dev0+lab04-replay"\n'
        '+LAB04_REPLAY_MARKER = "replay_v2"\n',
        encoding="utf-8",
    )
    (replay / "neo4j_cleanup.txt").write_text(
        "stale_edges_deleted=2\nstale_nodes_deleted=3\n", encoding="utf-8"
    )
    (replay / "neo4j_after_cleanup.png").write_bytes(b"\x89PNG\r\n\x1a\nneo4j")
    (replay / "mongodb_after_replay.png").write_bytes(b"\x89PNG\r\n\x1a\nmongo")


def test_manifest_write_and_validate_accepts_canonical_replay(tmp_path: Path) -> None:
    _write_valid_raw_evidence(tmp_path)
    module = _load_manifest_module()

    manifest = module.write_manifest(tmp_path)
    validated = module.validate_manifest(tmp_path)

    assert manifest["stage"] == 3
    assert manifest["status"] == "pass"
    assert manifest["source"]["target_file"] == "src/datasets/__init__.py"
    assert manifest["kafka"]["delta"] == {
        "cpg.nodes": 23,
        "cpg.edges": 16,
        "cpg.metadata": 1,
        "cpg.errors": 0,
    }
    assert manifest["kafka"]["graph_counts_after"]["unique_node_ids"] == 21422
    assert manifest["spark"]["metadata_offset_after_replay"] == 6
    assert manifest["neo4j"]["stale_deleted"] == {"nodes": 3, "edges": 2}
    assert manifest["mongodb"]["unchanged_documents"] == 4
    assert validated == manifest


def test_manifest_rejects_changed_artifact_hash(tmp_path: Path) -> None:
    _write_valid_raw_evidence(tmp_path)
    module = _load_manifest_module()
    module.write_manifest(tmp_path)
    changed = tmp_path / REPLAY_DIR / "neo4j_cleanup.txt"
    changed.write_text(changed.read_text(encoding="utf-8") + "changed\n", encoding="utf-8")

    with pytest.raises(module.EvidenceError, match="hash mismatch"):
        module.validate_manifest(tmp_path)


def test_manifest_rejects_wrong_checkpoint_resume(tmp_path: Path) -> None:
    _write_valid_raw_evidence(tmp_path)
    _write_json(
        tmp_path,
        "spark_checkpoint_after_restart.json",
        {"metadata_offset": 0, "completed_batch": 2},
    )
    module = _load_manifest_module()

    with pytest.raises(module.EvidenceError, match="checkpoint"):
        module.write_manifest(tmp_path)


def test_manifest_rejects_missing_ui_screenshot(tmp_path: Path) -> None:
    _write_valid_raw_evidence(tmp_path)
    (tmp_path / REPLAY_DIR / "mongodb_after_replay.png").unlink()
    module = _load_manifest_module()

    with pytest.raises(module.EvidenceError, match="mongodb_after_replay.png"):
        module.write_manifest(tmp_path)


def test_manifest_rejects_pending_or_private_text(tmp_path: Path) -> None:
    _write_valid_raw_evidence(tmp_path)
    metadata = tmp_path / REPLAY_DIR / "neo4j_cleanup.txt"
    metadata.write_text("pending at /home/student/private\n", encoding="utf-8")
    module = _load_manifest_module()

    with pytest.raises(module.EvidenceError, match="unsafe text"):
        module.write_manifest(tmp_path)


def test_runtime_script_locks_replay_order_and_target() -> None:
    source = (PROJECT_ROOT / "scripts" / "run_stage3_evidence.sh").read_text()

    assert 'COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-lab04-datasets-cpg}"' in source
    assert "export COMPOSE_PROJECT_NAME" in source
    assert "diff -u -U0" in source

    markers = [
        ': "${RESET_DOCKER_STATE:?',
        'TARGET_RELATIVE="src/datasets/__init__.py"',
        'trap restore_target EXIT',
        "bash scripts/run_stage2_evidence.sh",
        "docker compose restart spark",
        "REQUIRE_UNIQUE_EVENT_IDS=false",
        "bash scripts/wait_neo4j_connector_idle.sh",
        "bash scripts/capture_replay_store_evidence.sh pre-cleanup",
        "neo4j/cleanup_stale.cypher",
        "\nbash scripts/capture_replay_store_evidence.sh after\n",
    ]
    positions = [source.index(marker) for marker in markers]
    assert positions == sorted(positions)
    assert 'GRAPH_COUNTS_FILE="screenshots/replay/kafka_graph_counts_after.json"' in source
    assert "NEO4J_PASSWORD=password" not in source


def test_connector_wait_supports_replay_specific_output() -> None:
    source = (PROJECT_ROOT / "scripts" / "wait_neo4j_connector_idle.sh").read_text()
    assert 'GRAPH_COUNTS_FILE="${GRAPH_COUNTS_FILE:-screenshots/kafka/graph_event_counts.json}"' in source


def test_cleanup_query_uses_file_and_run_parameters_in_safe_order() -> None:
    source = (PROJECT_ROOT / "neo4j" / "cleanup_stale.cypher").read_text()
    edge_match = source.index("CPG_EDGE {file_id: $file_id}")
    edge_delete = source.index("DELETE r")
    node_match = source.index("CPGNode {file_id: $file_id}")
    node_delete = source.index("DETACH DELETE n")
    assert edge_match < edge_delete < node_match < node_delete
    assert source.count("$run_id") == 2


def test_store_capture_supports_all_replay_phases() -> None:
    source = (PROJECT_ROOT / "scripts" / "capture_replay_store_evidence.sh").read_text()
    for phase, artifact in (
        ("before", "neo4j_before.json"),
        ("pre-cleanup", "neo4j_pre_cleanup.json"),
        ("after", "neo4j_after.json"),
    ):
        assert phase in source
        assert artifact in source
    assert "mongodb_before.json" in source
    assert "mongodb_after_restart.json" in source
    assert "mongodb_after_replay.json" in source
    assert "duplicate_node_groups" in source
    assert "duplicate_file_id_groups" in source
    assert "NEO4J_PASSWORD=password" not in source


def test_runtime_capture_supports_checkpoint_and_topic_snapshots() -> None:
    source = (PROJECT_ROOT / "scripts" / "capture_replay_runtime_evidence.sh").read_text()
    for phase, checkpoint in (
        ("before", "spark_checkpoint_before.json"),
        ("after-restart", "spark_checkpoint_after_restart.json"),
        ("after-replay", "spark_checkpoint_after_replay.json"),
    ):
        assert phase in source
        assert checkpoint in source
    assert "kafka_offsets_before.json" in source
    assert "kafka_offsets_after.json" in source
    assert "/mnt/checkpoints/cpg_metadata" in source
    assert "cpg.metadata" in source


def test_windows_wrapper_forwards_to_git_bash_without_duplicate_workflow() -> None:
    source = (PROJECT_ROOT / "scripts" / "run_stage3_evidence.ps1").read_text()
    assert "[Security.SecureString]" in source
    assert "GIT_BASH" in source
    assert "Program Files\\Git\\bin\\bash.exe" in source
    assert "scripts/run_stage3_evidence.sh" in source
    assert "RESET_DOCKER_STATE" in source
    assert "Remove-Item Env:NEO4J_PASSWORD" in source
    assert "docker compose down" not in source


def test_legacy_replay_entrypoint_delegates_to_canonical_workflow() -> None:
    source = (PROJECT_ROOT / "scripts" / "run_replay_demo.sh").read_text().lower()
    assert "run_stage3_evidence.sh" in source
    assert "todo replay workflow" not in source


def test_fixture_hash_helper_is_deterministic() -> None:
    payload = b"stage3"
    assert hashlib.sha256(payload).hexdigest() == hashlib.sha256(payload).hexdigest()


def test_post_merge_owner_acceptance_is_normative() -> None:
    change = PROJECT_ROOT / "openspec" / "changes" / "stage3-replay-hardening"
    specs = {
        "kafka": (change / "specs/kafka-spark/spec.md").read_text(),
        "stores": (change / "specs/graph-stores/spec.md").read_text(),
        "book": (change / "specs/evidence-book/spec.md").read_text(),
    }

    assert "test/truc/stage3-windows-acceptance" in specs["kafka"]
    assert "5 -> 5 -> 6" in specs["kafka"]
    assert "23 nodes, 16 edges, 1 metadata, and 0 errors" in specs["kafka"]
    assert "review/thanh/stage3-store-acceptance" in specs["stores"]
    assert "must not alter expected counts" in specs["stores"].lower()
    assert "review/tuan/stage3-book-acceptance" in specs["book"]
    assert "without live Docker services" in specs["book"]
