import ast
from pathlib import Path

from parser_service.call_extractor import extract_call_edges_gen
from parser_service.cfg_extractor import extract_cfg_edges_gen
from parser_service.dfg_extractor import extract_dfg_edges_gen
from tests.conftest import DummyContext


def test_dfg_evaluation_order_no_self_loop(tmp_path: Path) -> None:
    context = DummyContext(repo_root=tmp_path)
    source = "x = 1\nx = x + 1\n"
    tree = ast.parse(source)

    edges = list(
        extract_dfg_edges_gen(
            tree=tree,
            file_id="file",
            file_path="src/datasets/config.py",
            context=context,
        )
    )

    # We expect exactly one DFG edge from the first assignment (x = 1) to the RHS use of x
    assert len(edges) == 1
    edge = edges[0]
    assert edge["edge_type"] == "DFG_DEF_USE"
    assert edge["source_id"] != edge["target_id"]


def test_cfg_unreachable_dead_code_no_next(tmp_path: Path) -> None:
    context = DummyContext(repo_root=tmp_path)
    source = "def run():\n    return 1\n    x = 2\n"
    tree = ast.parse(source)

    edges = list(
        extract_cfg_edges_gen(
            tree=tree,
            file_id="file",
            file_path="src/datasets/config.py",
            context=context,
        )
    )

    cfg_next_edges = [e for e in edges if e["edge_type"] == "CFG_NEXT"]
    # There should be no CFG_NEXT edge because return 1 is the first statement,
    # and the next statement is dead code (so zip loop breaks).
    assert len(cfg_next_edges) == 0


def test_call_method_collision_resolution(tmp_path: Path) -> None:
    context = DummyContext(repo_root=tmp_path)
    source = (
        "class A:\n"
        "    def foo(self):\n"
        "        pass\n"
        "    def bar(self):\n"
        "        self.foo()\n"
        "class B:\n"
        "    def foo(self):\n"
        "        pass\n"
    )
    tree = ast.parse(source)

    edges = list(
        extract_call_edges_gen(
            tree=tree,
            file_id="file",
            file_path="src/datasets/config.py",
            context=context,
        )
    )

    resolved_calls = [e for e in edges if e["edge_type"] == "CALL_RESOLVED"]
    assert len(resolved_calls) == 1
    call_edge = resolved_calls[0]
    assert call_edge["properties"]["resolution"] == "local"

    foo_a = [
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef)
        and n.name == "foo"
        and getattr(n, "parent", None)
        and n.parent.name == "A"
    ][0]
    from parser_service.ids import make_node_id

    expected_target_id = make_node_id("file", foo_a, "foo")
    assert call_edge["target_id"] == expected_target_id
