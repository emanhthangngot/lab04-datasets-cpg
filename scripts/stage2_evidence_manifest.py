#!/usr/bin/env python3
"""Build and validate the public Stage 2 evidence manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any


EXPECTED_REPO = "huggingface/datasets"
EVIDENCE_FOLDERS = ("kafka", "neo4j", "mongodb", "spark")
COMMAND_BY_FOLDER = {
    "kafka": "bash scripts/capture_kafka_evidence.sh",
    "neo4j": "bash scripts/capture_store_evidence.sh",
    "mongodb": "bash scripts/capture_store_evidence.sh",
    "spark": "bash scripts/capture_spark_evidence.sh",
}
TASK_BY_FOLDER = {"kafka": 3, "neo4j": 4, "mongodb": 5, "spark": 5}


class EvidenceError(ValueError):
    """Raised when Stage 2 evidence is incomplete or inconsistent."""


def _require_sha(name: str, value: str) -> None:
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        raise EvidenceError(f"{name} must be a 40-character lowercase Git SHA")


def _read_json_lines(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise EvidenceError(f"missing evidence artifact: {path}")
    records = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise EvidenceError(f"invalid JSON in {path}:{line_number}: {exc}") from exc
    return records


def _single(values: set[Any], label: str) -> Any:
    if len(values) != 1:
        raise EvidenceError(f"expected one {label}, found {sorted(repr(value) for value in values)}")
    return next(iter(values))


def _count_file(path: Path) -> int:
    matches = re.findall(r"(?m)^\s*(\d+)\s*$", path.read_text(encoding="utf-8"))
    if not matches:
        raise EvidenceError(f"missing numeric count in {path}")
    return int(matches[-1])


def _extract_int(text: str, label: str) -> int:
    match = re.search(rf"(?m)^{re.escape(label)}:\s*(\d+)\s*$", text)
    if not match:
        raise EvidenceError(f"missing {label!r} in MongoDB evidence")
    return int(match.group(1))


def _spark_offset(path: Path) -> int:
    for line in reversed(path.read_text(encoding="utf-8").splitlines()):
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "cpg.metadata" in payload:
            offsets = payload["cpg.metadata"]
            return max(int(value) for value in offsets.values())
    raise EvidenceError(f"missing cpg.metadata offset in {path}")


def _artifact_records(root: Path, captured_at: str) -> list[dict[str, Any]]:
    records = []
    screenshots = root / "screenshots"
    for folder in EVIDENCE_FOLDERS:
        for path in sorted((screenshots / folder).glob("*")):
            if not path.is_file() or path.name == ".gitkeep":
                continue
            records.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "task": TASK_BY_FOLDER[folder],
                    "command": COMMAND_BY_FOLDER[folder],
                    "captured_at": captured_at,
                    "result": "pass",
                    "source": "Stage 2 clean run",
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
            )
    return records


def build_manifest(
    root: Path,
    *,
    pipeline_commit: str,
    dataset_commit: str,
    captured_at: str,
) -> dict[str, Any]:
    """Build a validated Stage 2 manifest from sanitized evidence artifacts."""

    root = root.resolve()
    _require_sha("pipeline_commit", pipeline_commit)
    _require_sha("dataset_commit", dataset_commit)
    kafka = root / "screenshots" / "kafka"
    neo4j = root / "screenshots" / "neo4j"
    mongodb = root / "screenshots" / "mongodb"
    spark = root / "screenshots" / "spark"

    samples = {
        "nodes": _read_json_lines(kafka / "sample_cpg_nodes.json"),
        "edges": _read_json_lines(kafka / "sample_cpg_edges.json"),
        "metadata": _read_json_lines(kafka / "sample_cpg_metadata.json"),
        "errors": _read_json_lines(kafka / "sample_cpg_errors.json"),
    }
    all_events = [event for events in samples.values() for event in events]
    repos = {event.get("repo") for event in all_events}
    commit_shas = {event.get("commit_sha") for event in all_events}
    if repos != {EXPECTED_REPO}:
        raise EvidenceError(f"unexpected repo values: {sorted(repr(repo) for repo in repos)}")
    if "unknown" in commit_shas or commit_shas != {dataset_commit}:
        raise EvidenceError(
            f"unexpected commit_sha values: {sorted(repr(value) for value in commit_shas)}"
        )
    if len(samples["metadata"]) != 5:
        raise EvidenceError("Stage 2 requires exactly 5 metadata events")
    if len(samples["errors"]) != 1:
        raise EvidenceError("Stage 2 requires exactly 1 parser error event")

    parser_run_id = _single({event.get("run_id") for event in samples["metadata"]}, "parser run_id")
    error_run_id = _single({event.get("run_id") for event in samples["errors"]}, "error run_id")
    graph = json.loads((kafka / "graph_event_counts.json").read_text(encoding="utf-8"))
    if graph["node_events"] != graph["unique_node_ids"]:
        raise EvidenceError("Kafka node event IDs are not unique")
    if graph["edge_events"] != graph["unique_edge_ids"]:
        raise EvidenceError("Kafka edge event IDs are not unique")

    ast_nodes = sum(int(event["num_ast_nodes"]) for event in samples["metadata"])
    cfg_edges = sum(int(event["num_cfg_edges"]) for event in samples["metadata"])
    dfg_edges = sum(int(event["num_dfg_edges"]) for event in samples["metadata"])
    call_edges = sum(int(event["num_call_edges"]) for event in samples["metadata"])
    total_edges = sum(int(event["num_total_edges"]) for event in samples["metadata"])
    if ast_nodes != graph["node_events"] or total_edges != graph["edge_events"]:
        raise EvidenceError("Kafka graph totals do not match parser metadata totals")
    if total_edges != cfg_edges + dfg_edges + call_edges:
        raise EvidenceError("parser edge category totals are inconsistent")

    neo4j_metrics = {
        "total_nodes": _count_file(neo4j / "node_count.txt"),
        "explicit_nodes": _count_file(neo4j / "non_placeholder_count.txt"),
        "placeholders": _count_file(neo4j / "placeholder_count.txt"),
        "edges": _count_file(neo4j / "edge_count.txt"),
        "duplicate_node_groups": 0,
        "duplicate_edge_groups": 0,
    }
    if neo4j_metrics["total_nodes"] != neo4j_metrics["explicit_nodes"] + neo4j_metrics["placeholders"]:
        raise EvidenceError("Neo4j total node count does not equal explicit nodes plus placeholders")
    if neo4j_metrics["explicit_nodes"] != graph["unique_node_ids"] or neo4j_metrics["edges"] != graph["unique_edge_ids"]:
        raise EvidenceError("Neo4j persisted totals do not match unique Kafka IDs")
    if "No duplicate nodes found" not in (neo4j / "duplicate_nodes.txt").read_text(encoding="utf-8"):
        raise EvidenceError("Neo4j duplicate node evidence is not empty")
    if "No duplicate edges found" not in (neo4j / "duplicate_edges.txt").read_text(encoding="utf-8"):
        raise EvidenceError("Neo4j duplicate edge evidence is not empty")

    mongo_text = (mongodb / "metadata_evidence.txt").read_text(encoding="utf-8")
    mongo_metrics = {
        "documents": _extract_int(mongo_text, "file_metadata count"),
        "unique_file_ids": _extract_int(mongo_text, "unique file_id count"),
        "unique_file_paths": _extract_int(mongo_text, "unique file_path count"),
        "duplicate_file_id_groups": 0,
    }
    if set(mongo_metrics.values()) != {0, 5} or any(
        mongo_metrics[key] != 5
        for key in ("documents", "unique_file_ids", "unique_file_paths")
    ):
        raise EvidenceError("MongoDB evidence does not contain five unique metadata documents")
    if f'"{EXPECTED_REPO}"' not in mongo_text or not re.search(r"duplicate file_id check ---\s*\[\]", mongo_text):
        raise EvidenceError("MongoDB repository or duplicate evidence is invalid")

    connector = json.loads((kafka / "connector_status.json").read_text(encoding="utf-8"))
    if connector.get("connector", {}).get("state") != "RUNNING" or any(
        task.get("state") != "RUNNING" for task in connector.get("tasks", [])
    ):
        raise EvidenceError("Neo4j connector or task is not RUNNING")
    metadata_offset = _spark_offset(spark / "checkpoint_offsets.txt")
    if metadata_offset != len(samples["metadata"]):
        raise EvidenceError("Spark checkpoint offset does not match metadata event count")
    if not (spark / "checkpoint_commits.txt").read_text(encoding="utf-8").strip():
        raise EvidenceError("Spark checkpoint commit evidence is empty")

    return {
        "schema_version": "1.0",
        "stage": 2,
        "status": "pass",
        "run": {
            "captured_at": captured_at,
            "pipeline_commit": pipeline_commit,
            "dataset_repo": EXPECTED_REPO,
            "dataset_commit": dataset_commit,
            "parser_run_id": parser_run_id,
            "error_run_id": error_run_id,
        },
        "metrics": {
            "kafka": {
                **graph,
                "metadata_events": len(samples["metadata"]),
                "error_events": len(samples["errors"]),
                "ast_nodes": ast_nodes,
                "cfg_edges": cfg_edges,
                "dfg_edges": dfg_edges,
                "call_edges": call_edges,
                "total_edges": total_edges,
            },
            "neo4j": neo4j_metrics,
            "mongodb": mongo_metrics,
            "spark": {"metadata_offset": metadata_offset, "completed_batch": 0},
        },
        "artifacts": _artifact_records(root, captured_at),
    }


def write_manifest(
    root: Path,
    output: Path,
    *,
    pipeline_commit: str,
    dataset_commit: str,
    captured_at: str,
) -> dict[str, Any]:
    manifest = build_manifest(
        root,
        pipeline_commit=pipeline_commit,
        dataset_commit=dataset_commit,
        captured_at=captured_at,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def validate_manifest(root: Path, manifest_path: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    current_artifacts = _artifact_records(root.resolve(), manifest["run"]["captured_at"])
    if current_artifacts != manifest.get("artifacts"):
        raise EvidenceError("Stage 2 manifest does not match current artifacts")
    rebuilt = build_manifest(
        root,
        pipeline_commit=manifest["run"]["pipeline_commit"],
        dataset_commit=manifest["run"]["dataset_commit"],
        captured_at=manifest["run"]["captured_at"],
    )
    if rebuilt != manifest:
        raise EvidenceError("Stage 2 manifest does not match current evidence metrics")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("write", "validate"))
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, default=Path("screenshots/stage2_manifest.json"))
    parser.add_argument("--pipeline-commit")
    parser.add_argument("--dataset-commit")
    parser.add_argument("--captured-at")
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else args.root / args.output

    try:
        if args.command == "write":
            missing = [
                name
                for name, value in (
                    ("--pipeline-commit", args.pipeline_commit),
                    ("--dataset-commit", args.dataset_commit),
                    ("--captured-at", args.captured_at),
                )
                if not value
            ]
            if missing:
                parser.error(f"write requires {', '.join(missing)}")
            write_manifest(
                args.root,
                output,
                pipeline_commit=args.pipeline_commit,
                dataset_commit=args.dataset_commit,
                captured_at=args.captured_at,
            )
        else:
            validate_manifest(args.root, output)
    except EvidenceError as exc:
        parser.exit(1, f"ERROR: {exc}\n")


if __name__ == "__main__":
    main()
