from pathlib import Path

from parser_service.schemas import build_metadata_event
from parser_service.verification import metadata_total_is_consistent
from tests.conftest import DummyContext


def test_metadata_total_edges_is_explicit_sum(tmp_path: Path) -> None:
    context = DummyContext(repo_root=tmp_path)
    metadata = build_metadata_event(
        context=context,
        file_id="file",
        file_path="src/datasets/config.py",
        source="x = 1\n",
        num_ast_nodes=10,
        num_cfg_edges=2,
        num_dfg_edges=3,
        num_call_edges=4,
        parse_duration_ms=5,
        status="success",
    )

    assert metadata["num_total_edges"] == 9
    assert metadata_total_is_consistent(metadata)
