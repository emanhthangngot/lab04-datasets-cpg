"""Lab-level AST node extraction."""

from __future__ import annotations

import ast
from typing import Iterable

from .ids import assign_parents, get_scope_path, make_function_exit_id, make_node_id
from .schemas import build_node_event


# Semantic AST records that may participate in the CPG. Marker-only nodes such
# as ast.Load and ast.Add are deliberately excluded because they carry no
# independent source location and are represented by their parent properties.
SUPPORTED_NODE_TYPES = (
    ast.Module,
    ast.stmt,
    ast.expr,
    ast.comprehension,
    ast.keyword,
    ast.arg,
    ast.alias,
    ast.arguments,
    ast.withitem,
    ast.ExceptHandler,
    ast.match_case,
    ast.pattern,
    ast.TypeIgnore,
)


def _node_properties(node: ast.AST) -> dict:
    """Return compact explanatory properties without embedding source text."""

    properties = {}
    for field in ("name", "id", "arg", "attr", "module"):
        value = getattr(node, field, None)
        if isinstance(value, str):
            properties[field] = value
    if isinstance(node, ast.Constant) and isinstance(
        node.value, (str, int, float, bool, type(None))
    ):
        properties["value"] = node.value
    return properties


def extract_ast_nodes_gen(*, tree: ast.AST, file_id: str, file_path: str, context) -> Iterable[dict]:
    """Yield semantic AST nodes plus one synthetic exit node per function."""

    assign_parents(tree)

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
            properties=_node_properties(node),
        )

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield build_node_event(
                context=context,
                file_id=file_id,
                file_path=file_path,
                node_id=make_function_exit_id(file_id, node),
                node_type="FunctionExit",
                scope_path=get_scope_path(node),
                lineno=getattr(node, "end_lineno", None),
                col_offset=getattr(node, "end_col_offset", None),
                end_lineno=getattr(node, "end_lineno", None),
                end_col_offset=getattr(node, "end_col_offset", None),
                properties={"synthetic": True, "function": node.name},
            )
