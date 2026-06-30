"""Lab-level call edge extraction scaffold."""

from __future__ import annotations

import ast
from typing import Iterable


def collect_local_defs(tree: ast.AST) -> set[str]:
    """Collect local function/class names for basic call resolution."""

    return {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    }


def get_callee_name(func: ast.AST) -> str | None:
    """Return a simple callee name from a Call.func node."""

    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def extract_call_edges_gen(*, tree: ast.AST, file_id: str, file_path: str, context) -> Iterable[dict]:
    """Yield CALL_RESOLVED or CALL_UNRESOLVED edges.

    TODO: Connect Call nodes to local definitions when possible; otherwise emit
    CALL_UNRESOLVED with callee properties for evidence.
    """

    return iter(())
