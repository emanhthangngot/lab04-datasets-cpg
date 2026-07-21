#!/usr/bin/env python3
"""Build and validate the strict Stage 3 replay evidence manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


REPLAY_RELATIVE = Path("screenshots/replay")
MANIFEST_NAME = "stage3_replay_manifest.json"
TARGET_FILE = "src/datasets/__init__.py"
TARGET_FILE_ID = "6c39568a6a11c430"
DATASET_COMMIT = "41adfd0f9ee9ba3a6b4f719d5b551c5b19ae45e2"

JSON_ARTIFACTS = (
    "run_metadata.json",
    "kafka_offsets_before.json",
    "kafka_offsets_after.json",
    "kafka_graph_counts_after.json",
    "spark_checkpoint_before.json",
    "spark_checkpoint_after_restart.json",
    "spark_checkpoint_after_replay.json",
    "neo4j_before.json",
    "neo4j_pre_cleanup.json",
    "neo4j_after.json",
    "mongodb_before.json",
    "mongodb_after_restart.json",
    "mongodb_after_replay.json",
    "evidence_metadata.json",
)
TEXT_ARTIFACTS = ("source_patch.diff", "neo4j_cleanup.txt")
PNG_ARTIFACTS = ("neo4j_after_cleanup.png", "mongodb_after_replay.png")
REQUIRED_ARTIFACTS = JSON_ARTIFACTS + TEXT_ARTIFACTS + PNG_ARTIFACTS
CANONICAL_TEXT_ARTIFACTS = frozenset(JSON_ARTIFACTS + TEXT_ARTIFACTS)

EXPECTED_KAFKA_BEFORE = {
    "cpg.nodes": 21415,
    "cpg.edges": 7968,
    "cpg.metadata": 5,
    "cpg.errors": 1,
    "unique_node_ids": 21415,
    "unique_edge_ids": 7968,
}
EXPECTED_KAFKA_AFTER = {
    "cpg.nodes": 21438,
    "cpg.edges": 7984,
    "cpg.metadata": 6,
    "cpg.errors": 1,
    "unique_node_ids": 21422,
    "unique_edge_ids": 7971,
}
EXPECTED_NEO4J_BEFORE = {
    "explicit_nodes": 21415,
    "placeholders": 1213,
    "edges": 7968,
    "target_nodes": 19,
    "target_edges": 15,
    "duplicate_node_groups": 0,
    "duplicate_edge_groups": 0,
}
EXPECTED_NEO4J_PRE_CLEANUP = {
    "explicit_nodes": 21422,
    "placeholders": 1213,
    "edges": 7971,
    "target_nodes": 26,
    "target_edges": 18,
    "stale_nodes": 3,
    "stale_edges": 2,
}
EXPECTED_NEO4J_AFTER = {
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
}


class EvidenceError(ValueError):
    """Raised when replay evidence cannot support a Stage 3 pass claim."""


def _replay_dir(root: Path) -> Path:
    return root / REPLAY_RELATIVE


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise EvidenceError(f"invalid JSON artifact {path.name}: {error}") from error
    if not isinstance(value, dict):
        raise EvidenceError(f"JSON artifact {path.name} must contain an object")
    return value


def _sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.name in CANONICAL_TEXT_ARTIFACTS:
        payload = payload.replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise EvidenceError(message)


def _require_exact(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise EvidenceError(f"{label} mismatch: expected {expected!r}, got {actual!r}")


def _check_artifacts(replay: Path) -> None:
    for name in REQUIRED_ARTIFACTS:
        path = replay / name
        if not path.is_file():
            raise EvidenceError(f"missing required replay artifact: {name}")
        if path.stat().st_size == 0:
            raise EvidenceError(f"empty replay artifact: {name}")

    unsafe = re.compile(
        r"(?i)(\bpending\b|NEO4J_PASSWORD\s*=|password\s*=|/home/[^\s]+|[A-Z]:\\Users\\[^\s]+)"
    )
    for name in JSON_ARTIFACTS + TEXT_ARTIFACTS:
        text = (replay / name).read_text(encoding="utf-8", errors="replace")
        match = unsafe.search(text)
        if match:
            raise EvidenceError(f"unsafe text in {name}: {match.group(0)!r}")

    for name in PNG_ARTIFACTS:
        if not (replay / name).read_bytes().startswith(b"\x89PNG\r\n\x1a\n"):
            raise EvidenceError(f"invalid PNG evidence: {name}")


def _validate_mongodb(
    before: dict[str, Any], restarted: dict[str, Any], after: dict[str, Any], run: dict[str, Any]
) -> int:
    for label, payload in (
        ("MongoDB before", before),
        ("MongoDB after restart", restarted),
        ("MongoDB after replay", after),
    ):
        _require_exact(payload.get("documents"), 5, f"{label} document count")
        _require_exact(
            payload.get("duplicate_file_id_groups"), 0, f"{label} duplicate file_id groups"
        )
        documents = payload.get("documents_by_file_id")
        _require(isinstance(documents, dict) and len(documents) == 5, f"{label} file map invalid")

    baseline = before["documents_by_file_id"]
    _require_exact(restarted["documents_by_file_id"], baseline, "MongoDB checkpoint restart")
    replayed = after["documents_by_file_id"]
    file_id = run["file_id"]
    _require(file_id in baseline and file_id in replayed, "MongoDB target file_id is missing")
    _require_exact(baseline[file_id]["run_id"], run["baseline_run_id"], "baseline run_id")
    _require_exact(replayed[file_id]["run_id"], run["replay_run_id"], "replay run_id")
    _require_exact(
        baseline[file_id]["content_hash"], run["before_content_hash"], "baseline content_hash"
    )
    _require_exact(
        replayed[file_id]["content_hash"], run["after_content_hash"], "replay content_hash"
    )
    _require(
        run["before_content_hash"] != run["after_content_hash"],
        "replay content_hash must change",
    )

    unchanged = 0
    for current_file_id, baseline_document in baseline.items():
        if current_file_id == file_id:
            continue
        _require_exact(
            replayed.get(current_file_id), baseline_document, f"unchanged MongoDB file {current_file_id}"
        )
        unchanged += 1
    _require_exact(unchanged, 4, "unchanged MongoDB document count")
    return unchanged


def _build_manifest(root: Path) -> dict[str, Any]:
    replay = _replay_dir(root)
    _check_artifacts(replay)
    data = {name: _read_json(replay / name) for name in JSON_ARTIFACTS}
    run = data["run_metadata.json"]

    _require_exact(run.get("dataset_commit"), DATASET_COMMIT, "dataset commit")
    _require_exact(run.get("dataset_repo"), "huggingface/datasets", "dataset repo")
    _require_exact(run.get("target_file"), TARGET_FILE, "replay target")
    _require_exact(run.get("file_id"), TARGET_FILE_ID, "replay file_id")
    _require(bool(run.get("source_restored")), "source was not restored")
    _require(
        run.get("baseline_run_id") and run.get("replay_run_id")
        and run["baseline_run_id"] != run["replay_run_id"],
        "baseline and replay run_id values must be non-empty and different",
    )
    for key in ("pipeline_commit", "dataset_commit"):
        _require(bool(re.fullmatch(r"[0-9a-f]{40}", str(run.get(key, "")))), f"invalid {key}")
    for key in ("before_content_hash", "after_content_hash"):
        _require(bool(re.fullmatch(r"[0-9a-f]{64}", str(run.get(key, "")))), f"invalid {key}")

    kafka_before = data["kafka_offsets_before.json"]
    kafka_after = data["kafka_offsets_after.json"]
    kafka_graph_counts = data["kafka_graph_counts_after.json"]
    _require_exact(kafka_before, EXPECTED_KAFKA_BEFORE, "Kafka baseline")
    _require_exact(kafka_after, EXPECTED_KAFKA_AFTER, "Kafka replay")
    _require_exact(
        kafka_graph_counts,
        {
            "node_events": 21438,
            "unique_node_ids": 21422,
            "edge_events": 7984,
            "unique_edge_ids": 7971,
        },
        "Kafka replay graph counts",
    )
    kafka_delta = {
        topic: kafka_after[topic] - kafka_before[topic]
        for topic in ("cpg.nodes", "cpg.edges", "cpg.metadata", "cpg.errors")
    }
    _require_exact(
        kafka_delta,
        {"cpg.nodes": 23, "cpg.edges": 16, "cpg.metadata": 1, "cpg.errors": 0},
        "Kafka replay delta",
    )

    spark_before = data["spark_checkpoint_before.json"]
    spark_restarted = data["spark_checkpoint_after_restart.json"]
    spark_after = data["spark_checkpoint_after_replay.json"]
    _require_exact(spark_before.get("metadata_offset"), 5, "Spark baseline checkpoint")
    _require_exact(spark_restarted.get("metadata_offset"), 5, "Spark restart checkpoint")
    _require_exact(spark_after.get("metadata_offset"), 6, "Spark replay checkpoint")

    neo4j_before = data["neo4j_before.json"]
    neo4j_pre = data["neo4j_pre_cleanup.json"]
    neo4j_after = data["neo4j_after.json"]
    _require_exact(neo4j_before, EXPECTED_NEO4J_BEFORE, "Neo4j baseline")
    _require_exact(neo4j_pre, EXPECTED_NEO4J_PRE_CLEANUP, "Neo4j pre-cleanup")
    _require_exact(neo4j_after, EXPECTED_NEO4J_AFTER, "Neo4j final")

    cleanup_text = (replay / "neo4j_cleanup.txt").read_text(encoding="utf-8")
    edge_match = re.search(r"stale_edges_deleted=(\d+)", cleanup_text)
    node_match = re.search(r"stale_nodes_deleted=(\d+)", cleanup_text)
    _require(bool(edge_match and node_match), "Neo4j cleanup counts are missing")
    stale_deleted = {"nodes": int(node_match.group(1)), "edges": int(edge_match.group(1))}
    _require_exact(stale_deleted, {"nodes": 3, "edges": 2}, "Neo4j stale deletion")

    unchanged_documents = _validate_mongodb(
        data["mongodb_before.json"],
        data["mongodb_after_restart.json"],
        data["mongodb_after_replay.json"],
        run,
    )

    metadata = data["evidence_metadata.json"]
    _require_exact(metadata.get("result"), "pass", "evidence result")
    screenshots = metadata.get("screenshots", {})
    _require_exact(set(screenshots), set(PNG_ARTIFACTS), "UI screenshot metadata")

    artifact_hashes = {
        (REPLAY_RELATIVE / name).as_posix(): _sha256(replay / name)
        for name in REQUIRED_ARTIFACTS
    }
    return {
        "schema_version": "1.0",
        "stage": 3,
        "status": "pass",
        "run": {
            key: run[key]
            for key in (
                "captured_at",
                "pipeline_commit",
                "dataset_commit",
                "dataset_repo",
                "baseline_run_id",
                "replay_run_id",
            )
        },
        "source": {
            "target_file": run["target_file"],
            "file_id": run["file_id"],
            "before_content_hash": run["before_content_hash"],
            "after_content_hash": run["after_content_hash"],
            "source_restored": True,
        },
        "kafka": {
            "before": kafka_before,
            "after": kafka_after,
            "graph_counts_after": kafka_graph_counts,
            "delta": kafka_delta,
        },
        "spark": {
            "metadata_offset_before": 5,
            "metadata_offset_after_restart": 5,
            "metadata_offset_after_replay": 6,
            "completed_batch_before": spark_before.get("completed_batch"),
            "completed_batch_after_restart": spark_restarted.get("completed_batch"),
            "completed_batch_after_replay": spark_after.get("completed_batch"),
        },
        "neo4j": {
            "before": neo4j_before,
            "pre_cleanup": neo4j_pre,
            "after": neo4j_after,
            "stale_deleted": stale_deleted,
        },
        "mongodb": {
            "documents_before": 5,
            "documents_after_restart": 5,
            "documents_after_replay": 5,
            "unchanged_documents": unchanged_documents,
            "duplicate_file_id_groups": 0,
        },
        "artifacts": artifact_hashes,
    }


def write_manifest(root: Path | str = Path(".")) -> dict[str, Any]:
    root_path = Path(root)
    manifest = _build_manifest(root_path)
    output = _replay_dir(root_path) / MANIFEST_NAME
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def validate_manifest(root: Path | str = Path(".")) -> dict[str, Any]:
    root_path = Path(root)
    manifest_path = _replay_dir(root_path) / MANIFEST_NAME
    if not manifest_path.is_file():
        raise EvidenceError(f"missing replay manifest: {MANIFEST_NAME}")
    manifest = _read_json(manifest_path)
    hashes = manifest.get("artifacts")
    _require(isinstance(hashes, dict), "manifest artifacts map is missing")
    for relative, expected_hash in hashes.items():
        path = root_path / relative
        if not path.is_file():
            raise EvidenceError(f"manifest artifact is missing: {relative}")
        actual_hash = _sha256(path)
        if actual_hash != expected_hash:
            raise EvidenceError(
                f"artifact hash mismatch for {relative}: expected {expected_hash}, got {actual_hash}"
            )
    expected = _build_manifest(root_path)
    _require_exact(manifest, expected, "Stage 3 replay manifest")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("write", "validate"))
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    if args.command == "write":
        result = write_manifest(args.root)
    else:
        result = validate_manifest(args.root)
    print(json.dumps({"stage": result["stage"], "status": result["status"]}))


if __name__ == "__main__":
    main()
