"""Lab-level AST node extraction."""

from __future__ import annotations

import ast
from typing import Iterable

from .ids import get_scope_path, make_node_id
from .schemas import build_node_event


SUPPORTED_NODE_TYPES = (
    ast.Module,
    ast.Import,
    ast.ImportFrom,
    ast.ClassDef,
    ast.FunctionDef,
    ast.AsyncFunctionDef,
    ast.Assign,
    ast.AnnAssign,
    ast.AugAssign,
    ast.Return,
    ast.If,
    ast.For,
    ast.While,
    ast.Try,
    ast.With,
    ast.Call,
    ast.Name,
    ast.Attribute,
    ast.Constant,
    ast.BinOp,
    ast.Compare,
)


def extract_ast_nodes_gen(*, tree: ast.AST, file_id: str, file_path: str, context) -> Iterable[dict]:
    """Yield AST node events.

    TODO: Improve `scope_path` tracking for nested classes/functions. Current
    scaffold keeps scope coarse so downstream schema work can proceed.
    """

    for node in ast.walk(tree):
        if not isinstance(node, SUPPORTED_NODE_TYPES):
            continue
        scope_path = get_scope_path(node)
        node_id = make_node_id(file_id, node, scope_path)
        yield build_node_event(
            context=context,
            file_id=file_id,
            file_path=file_path,
            node_id=node_id,
            node_type=type(node).__name__,
            scope_path=scope_path,
            lineno=getattr(node, "lineno", None),
            col_offset=getattr(node, "col_offset", None),
            end_lineno=getattr(node, "end_lineno", None),
            end_col_offset=getattr(node, "end_col_offset", None),
            properties={"name": getattr(node, "name", None)} if hasattr(node, "name") else {},
        )
