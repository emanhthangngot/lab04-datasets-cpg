from pathlib import Path

from parser_service.schemas import build_edge_event, build_metadata_event, build_node_event
from tests.conftest import DummyContext


def test_node_and_edge_properties_are_never_null(tmp_path: Path) -> None:
    context = DummyContext(repo_root=tmp_path)

    node = build_node_event(
        context=context,
        file_id="file",
        file_path="src/datasets/config.py",
        node_id="node",
        node_type="Module",
        scope_path="<module>",
        lineno=None,
        col_offset=None,
        end_lineno=None,
        end_col_offset=None,
        properties=None,
    )
    edge = build_edge_event(
        context=context,
        file_id="file",
        file_path="src/datasets/config.py",
        edge_id="edge",
        source_id="a",
        target_id="b",
        edge_type="CFG_NEXT",
        properties=None,
    )

    assert node["properties"] == {}
    assert edge["properties"] == {}


def test_common_fields_are_present(tmp_path: Path) -> None:
    context = DummyContext(repo_root=tmp_path)
    metadata = build_metadata_event(
        context=context,
        file_id="file",
        file_path="src/datasets/config.py",
        source="x = 1\n",
        num_ast_nodes=1,
        num_cfg_edges=2,
        num_dfg_edges=3,
        num_call_edges=4,
        parse_duration_ms=5,
        status="success",
    )

    for field in ["schema_version", "event_time", "repo", "commit_sha", "run_id", "file_id", "file_path"]:
        assert field in metadata
