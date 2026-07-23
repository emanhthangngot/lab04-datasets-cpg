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
) -> tuple[int, int, dict[str, Any]]:
    baseline_documents = before.get("documents_by_file_id")
    _require(isinstance(baseline_documents, dict), "MongoDB baseline file map invalid")
    expected_documents = len(baseline_documents)
    _require(expected_documents > 0, "MongoDB baseline must contain metadata documents")

    for label, payload in (
        ("MongoDB before", before),
        ("MongoDB after restart", restarted),
        ("MongoDB after replay", after),
    ):
        _require_exact(payload.get("documents"), expected_documents, f"{label} document count")
        _require_exact(
            payload.get("duplicate_file_id_groups"), 0, f"{label} duplicate file_id groups"
        )
        documents = payload.get("documents_by_file_id")
        _require(
            isinstance(documents, dict) and len(documents) == expected_documents,
            f"{label} file map invalid",
        )

    baseline = baseline_documents
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
    _require_exact(unchanged, expected_documents - 1, "unchanged MongoDB document count")
    return unchanged, expected_documents, replayed[file_id]


def _build_manifest(root: Path) -> dict[str, Any]:
    replay = _replay_dir(root)
    _check_artifacts(replay)
    data = {name: _read_json(replay / name) for name in JSON_ARTIFACTS}
    run = data["run_metadata.json"]

    _require_exact(run.get("dataset_repo"), "huggingface/datasets", "dataset repo")
    _require_exact(run.get("target_file"), TARGET_FILE, "replay target")
    _require(
        bool(re.fullmatch(r"[0-9a-f]{16}", str(run.get("file_id", "")))),
        "invalid replay file_id",
    )
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

    unchanged_documents, document_count, _replay_document = _validate_mongodb(
        data["mongodb_before.json"],
        data["mongodb_after_restart.json"],
        data["mongodb_after_replay.json"],
        run,
    )

    kafka_before = data["kafka_offsets_before.json"]
    kafka_after = data["kafka_offsets_after.json"]
    kafka_graph_counts = data["kafka_graph_counts_after.json"]
    required_kafka = {
        "cpg.nodes",
        "cpg.edges",
        "cpg.metadata",
        "cpg.errors",
        "unique_node_ids",
        "unique_edge_ids",
    }
    _require_exact(set(kafka_before), required_kafka, "Kafka baseline fields")
    _require_exact(set(kafka_after), required_kafka, "Kafka replay fields")
    _require_exact(
        kafka_graph_counts,
        {
            "node_events": kafka_after["cpg.nodes"],
            "unique_node_ids": kafka_after["unique_node_ids"],
            "edge_events": kafka_after["cpg.edges"],
            "unique_edge_ids": kafka_after["unique_edge_ids"],
        },
        "Kafka replay graph counts",
    )
    kafka_delta = {
        topic: kafka_after[topic] - kafka_before[topic]
        for topic in ("cpg.nodes", "cpg.edges", "cpg.metadata", "cpg.errors")
    }
    _require_exact(kafka_delta["cpg.metadata"], 1, "Kafka metadata replay delta")
    _require_exact(kafka_delta["cpg.errors"], 0, "Kafka error replay delta")
    _require(kafka_delta["cpg.nodes"] > 0, "Kafka replay emitted no node events")
    _require(kafka_delta["cpg.edges"] >= 0, "Kafka edge replay delta is invalid")
    _require(kafka_after["unique_node_ids"] >= kafka_before["unique_node_ids"], "unique nodes regressed")
    _require(kafka_after["unique_edge_ids"] >= kafka_before["unique_edge_ids"], "unique edges regressed")

    spark_before = data["spark_checkpoint_before.json"]
    spark_restarted = data["spark_checkpoint_after_restart.json"]
    spark_after = data["spark_checkpoint_after_replay.json"]
    baseline_offset = kafka_before["cpg.metadata"]
    _require_exact(baseline_offset, document_count, "baseline metadata/document count")
    _require_exact(
        spark_before.get("metadata_offset"), baseline_offset, "Spark baseline checkpoint"
    )
    _require_exact(
        spark_restarted.get("metadata_offset"), baseline_offset, "Spark restart checkpoint"
    )
    _require_exact(
        spark_after.get("metadata_offset"), baseline_offset + 1, "Spark replay checkpoint"
    )

    neo4j_before = data["neo4j_before.json"]
    neo4j_pre = data["neo4j_pre_cleanup.json"]
    neo4j_after = data["neo4j_after.json"]
    _require_exact(neo4j_before.get("duplicate_node_groups"), 0, "baseline duplicate nodes")
    _require_exact(neo4j_before.get("duplicate_edge_groups"), 0, "baseline duplicate edges")
    _require_exact(
        neo4j_before.get("explicit_nodes"), kafka_before["unique_node_ids"], "baseline Neo4j nodes"
    )
    _require_exact(neo4j_before.get("edges"), kafka_before["unique_edge_ids"], "baseline Neo4j edges")
    _require_exact(
        neo4j_pre.get("explicit_nodes"), kafka_after["unique_node_ids"], "pre-cleanup Neo4j nodes"
    )
    _require_exact(neo4j_pre.get("edges"), kafka_after["unique_edge_ids"], "pre-cleanup Neo4j edges")
    _require_exact(
        neo4j_after.get("target_nodes"), kafka_delta["cpg.nodes"], "final target nodes"
    )
    _require_exact(
        neo4j_after.get("target_edges"), kafka_delta["cpg.edges"], "final target edges"
    )
    _require_exact(
        neo4j_after.get("explicit_nodes"),
        neo4j_pre["explicit_nodes"] - neo4j_pre["stale_nodes"],
        "final Neo4j node cleanup",
    )
    _require_exact(
        neo4j_after.get("edges"),
        neo4j_pre["edges"] - neo4j_pre["stale_edges"],
        "final Neo4j edge cleanup",
    )
    for key in ("stale_nodes", "stale_edges", "old_run_entities", "duplicate_node_groups", "duplicate_edge_groups"):
        _require_exact(neo4j_after.get(key), 0, f"final Neo4j {key}")
    _require_exact(
        neo4j_after.get("placeholders"), neo4j_before.get("placeholders"), "placeholder count"
    )

    cleanup_text = (replay / "neo4j_cleanup.txt").read_text(encoding="utf-8")
    edge_match = re.search(r"stale_edges_deleted=(\d+)", cleanup_text)
    node_match = re.search(r"stale_nodes_deleted=(\d+)", cleanup_text)
    _require(bool(edge_match and node_match), "Neo4j cleanup counts are missing")
    stale_deleted = {"nodes": int(node_match.group(1)), "edges": int(edge_match.group(1))}
    _require_exact(
        stale_deleted,
        {"nodes": neo4j_pre["stale_nodes"], "edges": neo4j_pre["stale_edges"]},
        "Neo4j stale deletion",
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
            "metadata_offset_before": baseline_offset,
            "metadata_offset_after_restart": baseline_offset,
            "metadata_offset_after_replay": baseline_offset + 1,
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
            "documents_before": document_count,
            "documents_after_restart": document_count,
            "documents_after_replay": document_count,
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
