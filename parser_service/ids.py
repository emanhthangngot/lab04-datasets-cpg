"""Stable identifier helpers for Lab04 CPG events."""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path


def short_hash(raw: str, n: int = 16) -> str:
    """Return a deterministic short SHA-256 hash."""

    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:n]


def normalize_relative_path(path: Path, repo_root: Path) -> str:
    """Normalize a path relative to the cloned repository root."""

    return path.relative_to(repo_root).as_posix()


def assign_parents(tree: ast.AST) -> None:
    """Walk the AST and set a ``_parent`` attribute on every child node.

    This enables scope-aware lookups without modifying the public ``parent``
    attribute that ``call_extractor`` already sets.  The helper is idempotent
    — calling it twice on the same tree is harmless.
    """

    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            child._parent = parent  # type: ignore[attr-defined]


def get_scope_path(node: ast.AST) -> str:
    """Return a fully-qualified scope path such as ``<module>.A.foo``.

    Walks ``_parent`` pointers (set by :func:`assign_parents`) upward,
    collecting class / function names.  Falls back to the node's own name
    when parent pointers are absent.
    """

    parts: list[str] = []
    curr = node
    while curr is not None:
        if isinstance(curr, ast.Module):
            parts.append("<module>")
            break
        if isinstance(curr, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            parts.append(curr.name)
        curr = getattr(curr, "_parent", None)
    if not parts:
        # Fallback when parent pointers were not assigned
        return getattr(node, "name", "<module>")
    return ".".join(reversed(parts))


def make_file_id(repo_name: str, relative_path: str) -> str:
    """Stable file ID used as Kafka key and replay cleanup selector."""

    return short_hash(f"{repo_name}:{relative_path}")


def make_content_hash(source: str) -> str:
    """Hash file content for metadata and replay evidence."""

    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def extract_assignment_target(node: ast.AST) -> str:
    """Best-effort assignment target text for stable assignment node IDs."""

    try:
        if isinstance(node, ast.Assign) and node.targets:
            return ast.unparse(node.targets[0])
        if isinstance(node, ast.AnnAssign):
            return ast.unparse(node.target)
        if isinstance(node, ast.AugAssign):
            return ast.unparse(node.target)
    except Exception:
        return "unknown"
    return "unknown"


def make_node_id(file_id: str, node: ast.AST, scope_path: str) -> str:
    """Create a lab-level stable node ID.

    TODO: Revisit ID strategy if extraction becomes function-level incremental.
    """

    node_type = type(node).__name__
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        raw = f"{file_id}:{scope_path}:{node_type}:{node.name}"
    elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
        raw = f"{file_id}:{scope_path}:{node_type}:{extract_assignment_target(node)}:{getattr(node, 'lineno', -1)}"
    else:
        raw = f"{file_id}:{scope_path}:{node_type}:{getattr(node, 'lineno', -1)}:{getattr(node, 'col_offset', -1)}"
    return short_hash(raw)


def make_edge_id(source_id: str, target_id: str, edge_type: str) -> str:
    """Create a stable edge ID from endpoints and type."""

    return short_hash(f"{source_id}:{target_id}:{edge_type}")


def make_external_target_id(target_name: str) -> str:
    """Create a deterministic target ID for unresolved external calls."""

    normalized = ".".join(part for part in target_name.strip().split(".") if part)
    return f"external:{normalized or 'unknown'}"
