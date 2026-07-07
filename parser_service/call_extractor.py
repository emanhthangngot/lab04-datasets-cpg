"""Lab-level call edge extraction."""

from __future__ import annotations

import ast
from typing import Iterable

from .ids import make_edge_id, make_external_target_id, make_node_id
from .schemas import build_edge_event


def _node_scope(node: ast.AST) -> str:
    return getattr(node, "name", "<module>") if not isinstance(node, ast.Module) else "<module>"


def _node_id(file_id: str, node: ast.AST) -> str:
    return make_node_id(file_id, node, _node_scope(node))


def collect_local_defs(tree: ast.AST, file_id: str | None = None) -> dict[str, str] | set[str]:
    """Collect local function/class names for basic call resolution.

    When ``file_id`` is omitted, return only names for compatibility with older
    scaffold callers. Stage 2 call extraction passes ``file_id`` and receives
    emitted node IDs.
    """

    defs = {
        node.name: make_node_id(file_id, node, node.name) if file_id else node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    }
    return defs if file_id else set(defs)


def get_callee_name(func: ast.AST) -> str | None:
    """Return a dotted callee name from a Call.func node when possible."""

    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        base = get_callee_name(func.value)
        return f"{base}.{func.attr}" if base else func.attr
    return None


def extract_call_edges_gen(*, tree: ast.AST, file_id: str, file_path: str, context) -> Iterable[dict]:
    """Yield CALL_RESOLVED or CALL_UNRESOLVED edges for ast.Call nodes."""

    local_defs = collect_local_defs(tree, file_id=file_id)
    assert isinstance(local_defs, dict)

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        callee_name = get_callee_name(node.func) or "unknown"
        simple_name = callee_name.rsplit(".", 1)[-1]
        source_id = _node_id(file_id, node)

        if simple_name in local_defs:
            edge_type = "CALL_RESOLVED"
            target_id = local_defs[simple_name]
            properties = {
                "extractor": "call",
                "target_name": callee_name,
                "resolution": "local",
            }
        else:
            edge_type = "CALL_UNRESOLVED"
            target_id = make_external_target_id(callee_name)
            properties = {
                "extractor": "call",
                "target_name": callee_name,
                "resolution": "unresolved",
            }

        yield build_edge_event(
            context=context,
            file_id=file_id,
            file_path=file_path,
            edge_id=make_edge_id(source_id, target_id, edge_type),
            source_id=source_id,
            target_id=target_id,
            edge_type=edge_type,
            properties=properties,
        )
