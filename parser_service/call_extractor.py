"""Lab-level call edge extraction."""

from __future__ import annotations

import ast
from typing import Iterable

from .ids import assign_parents, get_scope_path, make_edge_id, make_external_target_id, make_node_id
from .schemas import build_edge_event


def _node_id(file_id: str, node: ast.AST) -> str:
    return make_node_id(file_id, node, get_scope_path(node))


def collect_local_defs(tree: ast.AST, file_id: str | None = None) -> dict[str, str] | set[str]:
    """Collect local function/class names for basic call resolution.

    When ``file_id`` is omitted, return only names for compatibility with older
    scaffold callers. Stage 2 call extraction passes ``file_id`` and receives
    emitted node IDs.
    """

    # Populate parent pointers for lexical scoping lookup
    assign_parents(tree)

    defs = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            name = node.name
            node_id = make_node_id(file_id, node, get_scope_path(node)) if file_id else name
            if name not in defs:
                defs[name] = node_id
    return defs if file_id else set(defs)


def get_callee_name(func: ast.AST) -> str | None:
    """Return a dotted callee name from a Call.func node when possible."""

    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        base = get_callee_name(func.value)
        return f"{base}.{func.attr}" if base else func.attr
    return None


def is_local_variable(name: str, scope: ast.AST) -> bool:
    """Check if the given name is defined as a parameter or assigned variable inside this scope.

    This does not recurse into nested function/class definitions to respect lexical boundaries.
    """

    if isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef)):
        args = scope.args
        all_args = list(args.args) + list(args.kwonlyargs)
        if args.vararg:
            all_args.append(args.vararg)
        if args.kwarg:
            all_args.append(args.kwarg)
        if any(arg.arg == name for arg in all_args if arg is not None):
            return True

    body = getattr(scope, "body", None)
    if isinstance(body, list):
        for node in body:
            # Skip checking inside nested function/class definitions
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for t in targets:
                    for child in ast.walk(t):
                        if isinstance(child, ast.Name) and child.id == name:
                            return True
    return False


def resolve_call_target(
    node: ast.Call,
    local_defs: dict[str, str],
    tree: ast.AST,
    file_id: str,
) -> str | None:
    """Resolve call target using scope-aware lexical lookup walking up parents."""

    callee_name = get_callee_name(node.func) or "unknown"
    simple_name = callee_name.rsplit(".", 1)[-1]

    # Walk up parent scopes
    curr = getattr(node, "_parent", None)
    while curr:
        if isinstance(curr, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef, ast.Module)):
            # If the name is masked as a local variable or parameter, the call is unresolved
            if is_local_variable(simple_name, curr):
                return None

            body = getattr(curr, "body", None)
            if isinstance(body, list):
                for body_node in body:
                    if isinstance(body_node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and body_node.name == simple_name:
                        return make_node_id(file_id, body_node, get_scope_path(body_node))
        curr = getattr(curr, "_parent", None)

    # Fallback to flat local_defs
    if simple_name in local_defs:
        return local_defs[simple_name]

    return None


def extract_call_edges_gen(*, tree: ast.AST, file_id: str, file_path: str, context) -> Iterable[dict]:
    """Yield CALL_RESOLVED or CALL_UNRESOLVED edges for ast.Call nodes."""

    local_defs = collect_local_defs(tree, file_id=file_id)
    assert isinstance(local_defs, dict)

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        callee_name = get_callee_name(node.func) or "unknown"
        source_id = _node_id(file_id, node)

        resolved_id = resolve_call_target(node, local_defs, tree, file_id)

        if resolved_id:
            edge_type = "CALL_RESOLVED"
            target_id = resolved_id
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

