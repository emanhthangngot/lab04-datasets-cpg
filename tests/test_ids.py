import ast

import pytest

from parser_service.ast_extractor import SUPPORTED_NODE_TYPES
from parser_service.ids import (
    assign_parents,
    get_scope_path,
    make_content_hash,
    make_edge_id,
    make_file_id,
    make_node_id,
)


def test_file_and_content_hash_are_deterministic() -> None:
    assert make_file_id("huggingface/datasets", "src/datasets/config.py") == make_file_id(
        "huggingface/datasets", "src/datasets/config.py"
    )
    assert make_content_hash("x = 1\n") == make_content_hash("x = 1\n")


def test_node_and_edge_ids_are_deterministic() -> None:
    tree = ast.parse("def load():\n    return 1\n")
    assign_parents(tree)
    func = tree.body[0]
    file_id = make_file_id("huggingface/datasets", "src/datasets/config.py")

    assert make_node_id(file_id, func, "load") == make_node_id(file_id, func, "load")
    assert make_edge_id("a", "b", "CFG_NEXT") == make_edge_id("a", "b", "CFG_NEXT")


def _supported_node_ids(source: str) -> list[str]:
    tree = ast.parse(source)
    assign_parents(tree)
    return [
        make_node_id("file", node, get_scope_path(node))
        for node in ast.walk(tree)
        if isinstance(node, SUPPORTED_NODE_TYPES)
    ]


def test_structural_node_ids_are_stable_across_identical_parses() -> None:
    source = "result = obj.value + fn(1)\n"
    assert _supported_node_ids(source) == _supported_node_ids(source)


def test_supported_nodes_have_unique_ids_even_with_same_coordinates() -> None:
    tree = ast.parse("result = obj.left + obj.right + fn(1) + fn(1)\n")
    assign_parents(tree)

    supported = [
        node for node in ast.walk(tree) if isinstance(node, SUPPORTED_NODE_TYPES)
    ]
    for node in supported:
        node.lineno = 1
        node.col_offset = 0

    ids = [make_node_id("file", node, get_scope_path(node)) for node in supported]
    assert len(ids) == len(set(ids))


def test_same_named_definitions_in_one_scope_have_unique_ids() -> None:
    tree = ast.parse("def load():\n    pass\ndef load():\n    pass\n")
    assign_parents(tree)
    functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

    ids = [make_node_id("file", node, get_scope_path(node)) for node in functions]
    assert len(ids) == 2
    assert len(set(ids)) == 2


def test_make_node_id_requires_structural_metadata() -> None:
    tree = ast.parse("value = 1\n")
    assignment = tree.body[0]

    with pytest.raises(ValueError, match="assign_parents"):
        make_node_id("file", assignment, "<module>")
