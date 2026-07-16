from pathlib import Path

import pytest

from parser_service.config import EXPECTED_REPO_NAME, ParserContext
from parser_service.discover import discover_python_files
from parser_service.parser import process_file
from parser_service.producer import DryRunProducer


def test_five_file_sample_emits_unique_node_and_edge_ids() -> None:
    repo_root = Path("data/datasets").resolve()
    if not (repo_root / "src" / "datasets").is_dir():
        pytest.skip("huggingface/datasets clone is not available")

    context = ParserContext(
        repo_root=repo_root,
        repo_name=EXPECTED_REPO_NAME,
        commit_sha="test-sha",
        run_id="identity-test-run",
        schema_version="1.0",
        bootstrap_servers="broker:9092",
    )
    producer = DryRunProducer()
    metadata = [
        process_file(path, producer, context)
        for path in discover_python_files(repo_root)[:5]
    ]

    node_events = [
        value for topic, _, value in producer.messages if topic == "cpg.nodes"
    ]
    edge_events = [
        value for topic, _, value in producer.messages if topic == "cpg.edges"
    ]
    node_ids = [event["id"] for event in node_events]
    edge_ids = [event["id"] for event in edge_events]

    assert len(node_ids) == len(set(node_ids))
    assert len(edge_ids) == len(set(edge_ids))
    assert sum(item["num_ast_nodes"] for item in metadata) == len(node_events)
    assert sum(item["num_total_edges"] for item in metadata) == len(edge_events)
    assert all(
        event["source_id"] != event["target_id"]
        for event in edge_events
        if event["edge_type"] == "CFG_NEXT"
    )
