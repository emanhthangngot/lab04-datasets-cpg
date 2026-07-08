"""Lab-level CFG extraction."""

from __future__ import annotations

import ast
from typing import Iterable

from .ids import get_scope_path, make_edge_id, make_node_id
from .schemas import build_edge_event


def _node_id(file_id: str, node: ast.AST) -> str:
    return make_node_id(file_id, node, get_scope_path(node))


def _edge(
    *,
    source: ast.AST,
    target: ast.AST,
    edge_type: str,
    file_id: str,
    file_path: str,
    context,
) -> dict:
    source_id = _node_id(file_id, source)
    target_id = _node_id(file_id, target)
    return build_edge_event(
        context=context,
        file_id=file_id,
        file_path=file_path,
        edge_id=make_edge_id(source_id, target_id, edge_type),
        source_id=source_id,
        target_id=target_id,
        edge_type=edge_type,
        properties={"extractor": "cfg"},
    )


def _statement_lists(tree: ast.AST) -> Iterable[list[ast.stmt]]:
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(body, list) and body:
            yield body
        orelse = getattr(node, "orelse", None)
        if isinstance(orelse, list) and orelse:
            yield orelse


def extract_cfg_edges_gen(*, tree: ast.AST, file_id: str, file_path: str, context) -> Iterable[dict]:
    """Yield CFG edge events for common Python statement flow."""

    for statements in _statement_lists(tree):
        for current, following in zip(statements, statements[1:]):
            if isinstance(current, (ast.Return, ast.Break, ast.Continue)):
                break
            yield _edge(
                source=current,
                target=following,
                edge_type="CFG_NEXT",
                file_id=file_id,
                file_path=file_path,
                context=context,
            )

    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            if node.body:
                yield _edge(
                    source=node,
                    target=node.body[0],
                    edge_type="CFG_TRUE",
                    file_id=file_id,
                    file_path=file_path,
                    context=context,
                )
            if node.orelse:
                yield _edge(
                    source=node,
                    target=node.orelse[0],
                    edge_type="CFG_FALSE",
                    file_id=file_id,
                    file_path=file_path,
                    context=context,
                )
        elif isinstance(node, (ast.For, ast.While)) and node.body:
            yield _edge(
                source=node,
                target=node.body[0],
                edge_type="CFG_LOOP_BODY",
                file_id=file_id,
                file_path=file_path,
                context=context,
            )
            if not isinstance(node.body[-1], (ast.Return, ast.Break, ast.Continue)):
                yield _edge(
                    source=node.body[-1],
                    target=node,
                    edge_type="CFG_LOOP_BACK",
                    file_id=file_id,
                    file_path=file_path,
                    context=context,
                )
        elif isinstance(node, ast.Return):
            source_id = _node_id(file_id, node)
            target_id = f"{file_id}:function_exit"
            yield build_edge_event(
                context=context,
                file_id=file_id,
                file_path=file_path,
                edge_id=make_edge_id(source_id, target_id, "CFG_RETURN"),
                source_id=source_id,
                target_id=target_id,
                edge_type="CFG_RETURN",
                properties={"extractor": "cfg", "target": "function_exit"},
            )

