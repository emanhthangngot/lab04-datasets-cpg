import json
from pathlib import Path

import pytest

import scripts.stage2_evidence_manifest as manifest_tool


ROOT = Path(__file__).resolve().parents[1]


def test_stage2_manifest_tool_exists() -> None:
    assert (ROOT / "scripts" / "stage2_evidence_manifest.py").is_file()


def test_kafka_capture_uses_topic_specific_sample_counts() -> None:
    source = (ROOT / "scripts" / "capture_kafka_evidence.sh").read_text()
    assert 'local sample_count="$2"' in source
    assert '--max-messages "$sample_count"' in source
    assert 'capture_samples cpg.nodes "$SAMPLE_COUNT"' in source
    assert 'capture_samples cpg.edges "$SAMPLE_COUNT"' in source
    assert 'capture_samples cpg.metadata "$METADATA_CAPTURE_COUNT"' in source
    assert "METADATA_CAPTURE_COUNT:?" in source
    assert "capture_samples cpg.errors 1" in source


def test_stage2_runtime_processes_the_full_discovered_repository() -> None:
    source = (ROOT / "scripts" / "run_stage2_evidence.sh").read_text()

    assert "discover_python_files" in source
    assert 'export EXPECTED_MONGO_COUNT="$EXPECTED_FILE_COUNT"' in source
    assert 'export METADATA_CAPTURE_COUNT="$EXPECTED_FILE_COUNT"' in source
    assert "--mode full" in source
    assert "--mode sample" not in source


def test_mongo_express_profile_is_isolated_and_read_only() -> None:
    source = (ROOT / "docker-compose.yml").read_text()
    block = source[source.index("  mongo-express:") : source.index("\n  spark-checkpoint-init:")]
    assert "mongo-express:1.0.2-20-alpine3.19" in block
    assert 'profiles: ["evidence-ui"]' in block
    assert '"127.0.0.1:8081:8081"' in block
    assert 'ME_CONFIG_OPTIONS_READONLY: "true"' in block
    assert 'ME_CONFIG_BASICAUTH: "false"' in block


def test_connector_wait_captures_machine_readable_graph_counts() -> None:
    source = (ROOT / "scripts" / "wait_neo4j_connector_idle.sh").read_text()
    assert "screenshots/kafka/graph_event_counts.json" in source
    assert '"node_events"' in source
    assert '"unique_node_ids"' in source
    assert '"edge_events"' in source
    assert '"unique_edge_ids"' in source


def test_runbook_writes_and_validates_manifest_after_sanitization() -> None:
    source = (ROOT / "scripts" / "run_stage2_evidence.sh").read_text()
    sanitize_index = source.index(">>> Step 11: Sanitizing credentials")
    manifest_index = source.index("stage2_evidence_manifest.py write")
    assert manifest_index > sanitize_index
    assert 'PIPELINE_COMMIT_SHA="$(git rev-parse HEAD)"' in source
    assert 'CAPTURED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"' in source
    assert "stage2_evidence_manifest.py validate" in source


def _write_json_lines(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record) + "\n" for record in records))


def _write_stage2_fixture(root: Path, commit_sha: str) -> None:
    kafka = root / "screenshots" / "kafka"
    neo4j = root / "screenshots" / "neo4j"
    mongodb = root / "screenshots" / "mongodb"
    spark = root / "screenshots" / "spark"
    for directory in (kafka, neo4j, mongodb, spark):
        directory.mkdir(parents=True)

    common = {
        "schema_version": "1.0",
        "event_time": "2026-07-16T07:05:49.457Z",
        "repo": "huggingface/datasets",
        "commit_sha": commit_sha,
        "run_id": "parser-run",
        "file_id": "file",
        "file_path": "src/datasets/example.py",
    }
    _write_json_lines(kafka / "sample_cpg_nodes.json", [{**common, "id": "node"}])
    _write_json_lines(
        kafka / "sample_cpg_edges.json",
        [{**common, "id": "edge", "edge_type": "CFG_NEXT"}],
    )
    metadata = [
        {
            **common,
            "file_id": f"file-{index}",
            "file_path": f"src/datasets/file_{index}.py",
            "num_ast_nodes": index + 1,
            "num_cfg_edges": 1,
            "num_dfg_edges": 2,
            "num_call_edges": 3,
            "num_total_edges": 6,
        }
        for index in range(5)
    ]
    _write_json_lines(kafka / "sample_cpg_metadata.json", metadata)
    _write_json_lines(
        kafka / "sample_cpg_errors.json",
        [{**common, "run_id": "error-run", "status": "failed"}],
    )
    (kafka / "graph_event_counts.json").write_text(
        json.dumps(
            {
                "node_events": 15,
                "unique_node_ids": 15,
                "edge_events": 30,
                "unique_edge_ids": 30,
            }
        )
    )
    (kafka / "connector_status.json").write_text(
        json.dumps(
            {
                "connector": {"state": "RUNNING"},
                "tasks": [{"id": 0, "state": "RUNNING"}],
            }
        )
    )

    for name, header, value in (
        ("node_count.txt", "node_count", 17),
        ("non_placeholder_count.txt", "non_placeholder_count", 15),
        ("placeholder_count.txt", "placeholder_count", 2),
        ("edge_count.txt", "edge_count", 30),
    ):
        (neo4j / name).write_text(f"{header}\n{value}\n")
    (neo4j / "duplicate_nodes.txt").write_text("No duplicate nodes found\n")
    (neo4j / "duplicate_edges.txt").write_text("No duplicate edges found\n")

    (mongodb / "metadata_evidence.txt").write_text(
        "file_metadata count: 5\n"
        "unique file_id count: 5\n"
        "unique file_path count: 5\n"
        'repo values: ["huggingface/datasets"]\n'
        "--- duplicate file_id check ---\n[]\n"
    )
    (spark / "checkpoint_offsets.txt").write_text(
        'v1\n{"cpg.metadata":{"0":5}}\n'
    )
    (spark / "checkpoint_commits.txt").write_text(
        'v1\n{"nextBatchWatermarkMs":0}\n'
    )


def test_build_manifest_derives_metrics_and_artifact_hashes(tmp_path: Path) -> None:
    commit_sha = "a" * 40
    _write_stage2_fixture(tmp_path, commit_sha)

    manifest = manifest_tool.build_manifest(
        tmp_path,
        pipeline_commit="b" * 40,
        dataset_commit=commit_sha,
        captured_at="2026-07-16T07:05:00Z",
        expected_file_count=5,
    )

    assert manifest["run"]["parser_run_id"] == "parser-run"
    assert manifest["run"]["error_run_id"] == "error-run"
    assert manifest["run"]["files_processed"] == 5
    assert manifest["metrics"]["kafka"] == {
        "node_events": 15,
        "unique_node_ids": 15,
        "edge_events": 30,
        "unique_edge_ids": 30,
        "metadata_events": 5,
        "error_events": 1,
        "ast_nodes": 15,
        "cfg_edges": 5,
        "dfg_edges": 10,
        "call_edges": 15,
        "total_edges": 30,
    }
    assert manifest["metrics"]["neo4j"]["total_nodes"] == 17
    assert manifest["metrics"]["mongodb"]["documents"] == 5
    assert manifest["metrics"]["spark"]["metadata_offset"] == 5
    assert manifest["artifacts"]
    assert all(len(artifact["sha256"]) == 64 for artifact in manifest["artifacts"])


def test_build_manifest_rejects_partial_repository_evidence(tmp_path: Path) -> None:
    commit_sha = "a" * 40
    _write_stage2_fixture(tmp_path, commit_sha)

    with pytest.raises(manifest_tool.EvidenceError, match="discovered source-file count"):
        manifest_tool.build_manifest(
            tmp_path,
            pipeline_commit="b" * 40,
            dataset_commit=commit_sha,
            captured_at="2026-07-16T07:05:00Z",
            expected_file_count=223,
        )


def test_build_manifest_rejects_unknown_commit_sha(tmp_path: Path) -> None:
    _write_stage2_fixture(tmp_path, "unknown")

    with pytest.raises(manifest_tool.EvidenceError, match="commit_sha"):
        manifest_tool.build_manifest(
            tmp_path,
            pipeline_commit="b" * 40,
            dataset_commit="a" * 40,
            captured_at="2026-07-16T07:05:00Z",
        )


def test_validate_manifest_detects_modified_artifact(tmp_path: Path) -> None:
    commit_sha = "a" * 40
    _write_stage2_fixture(tmp_path, commit_sha)
    output = tmp_path / "screenshots" / "stage2_manifest.json"
    manifest_tool.write_manifest(
        tmp_path,
        output,
        pipeline_commit="b" * 40,
        dataset_commit=commit_sha,
        captured_at="2026-07-16T07:05:00Z",
    )
    (tmp_path / "screenshots" / "neo4j" / "node_count.txt").write_text(
        "node_count\n999\n"
    )

    with pytest.raises(manifest_tool.EvidenceError, match="does not match"):
        manifest_tool.validate_manifest(tmp_path, output)
