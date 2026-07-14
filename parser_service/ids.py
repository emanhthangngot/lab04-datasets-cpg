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
    """Assign parent pointers and deterministic structural paths.

    Structural paths follow AST field names and list indexes, for example
    ``$.body[0].value``. They are unique within one parsed tree and stable when
    the same source content is parsed again. The helper is idempotent, so each
    extractor may safely call it before generating identifiers.
    """

    tree._cpg_path = "$"  # type: ignore[attr-defined]

    def visit(parent: ast.AST) -> None:
        parent_path = parent._cpg_path  # type: ignore[attr-defined]
        for field_name, value in ast.iter_fields(parent):
            if isinstance(value, ast.AST):
                value._parent = parent  # type: ignore[attr-defined]
                value._cpg_path = f"{parent_path}.{field_name}"  # type: ignore[attr-defined]
                visit(value)
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    if not isinstance(child, ast.AST):
                        continue
                    child._parent = parent  # type: ignore[attr-defined]
                    child._cpg_path = (  # type: ignore[attr-defined]
                        f"{parent_path}.{field_name}[{index}]"
                    )
                    visit(child)

    visit(tree)


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
    """Create a unique, replay-stable ID from the node's structural path."""

    node_type = type(node).__name__
    structural_path = getattr(node, "_cpg_path", None)
    if structural_path is None:
        raise ValueError(
            "AST structural path is missing; call assign_parents(tree) before "
            "generating node IDs"
        )

    # Keep scope_path in the public signature for extractor compatibility. The
    # structural path already includes the node's exact location in the tree;
    # scope remains an event property used for explanation and call resolution.
    del scope_path
    raw = f"{file_id}:{node_type}:{structural_path}"
    return short_hash(raw)


def make_edge_id(source_id: str, target_id: str, edge_type: str) -> str:
    """Create a stable edge ID from endpoints and type."""

    return short_hash(f"{source_id}:{target_id}:{edge_type}")


def make_external_target_id(target_name: str) -> str:
    """Create a deterministic target ID for unresolved external calls."""

    normalized = ".".join(part for part in target_name.strip().split(".") if part)
    return f"external:{normalized or 'unknown'}"
