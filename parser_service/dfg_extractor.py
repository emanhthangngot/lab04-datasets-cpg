"""Lab-level DFG extraction."""

from __future__ import annotations

import ast
from typing import Iterable

from .ids import make_edge_id, make_node_id
from .schemas import build_edge_event


def _node_scope(node: ast.AST) -> str:
    return getattr(node, "name", "<module>") if not isinstance(node, ast.Module) else "<module>"


def _node_id(file_id: str, node: ast.AST) -> str:
    return make_node_id(file_id, node, _node_scope(node))


def _target_names(node: ast.AST) -> set[str]:
    if isinstance(node, ast.Name):
        return {node.id}
    names: set[str] = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Name):
            names.add(child.id)
    return names


def _assignment_targets(node: ast.AST) -> set[str]:
    if isinstance(node, ast.Assign):
        names: set[str] = set()
        for target in node.targets:
            names.update(_target_names(target))
        return names
    if isinstance(node, (ast.AnnAssign, ast.AugAssign)):
        return _target_names(node.target)
    return set()


def _walk_body(statements: list[ast.stmt]) -> Iterable[ast.AST]:
    for statement in statements:
        yield statement
        if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        for child in ast.iter_child_nodes(statement):
            if child is not statement:
                yield from ast.walk(child)


def _statement_scopes(tree: ast.AST) -> Iterable[list[ast.stmt]]:
    module_body = getattr(tree, "body", None)
    if isinstance(module_body, list):
        yield module_body
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            yield node.body


def extract_dfg_edges_gen(*, tree: ast.AST, file_id: str, file_path: str, context) -> Iterable[dict]:
    """Yield intra-scope DFG_DEF_USE edges from assignments to later name loads."""

    for statements in _statement_scopes(tree):
        latest_defs: dict[str, str] = {}
        for node in _walk_body(statements):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) and node.id in latest_defs:
                source_id = latest_defs[node.id]
                target_id = _node_id(file_id, node)
                yield build_edge_event(
                    context=context,
                    file_id=file_id,
                    file_path=file_path,
                    edge_id=make_edge_id(source_id, target_id, "DFG_DEF_USE"),
                    source_id=source_id,
                    target_id=target_id,
                    edge_type="DFG_DEF_USE",
                    properties={"extractor": "dfg", "variable": node.id},
                )

            targets = _assignment_targets(node)
            if targets:
                assignment_id = _node_id(file_id, node)
                for name in targets:
                    latest_defs[name] = assignment_id
