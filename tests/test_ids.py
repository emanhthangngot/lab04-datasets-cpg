import ast

from parser_service.ids import make_content_hash, make_edge_id, make_file_id, make_node_id


def test_file_and_content_hash_are_deterministic() -> None:
    assert make_file_id("huggingface/datasets", "src/datasets/config.py") == make_file_id(
        "huggingface/datasets", "src/datasets/config.py"
    )
    assert make_content_hash("x = 1\n") == make_content_hash("x = 1\n")


def test_node_and_edge_ids_are_deterministic() -> None:
    tree = ast.parse("def load():\n    return 1\n")
    func = tree.body[0]
    file_id = make_file_id("huggingface/datasets", "src/datasets/config.py")

    assert make_node_id(file_id, func, "load") == make_node_id(file_id, func, "load")
    assert make_edge_id("a", "b", "CFG_NEXT") == make_edge_id("a", "b", "CFG_NEXT")
