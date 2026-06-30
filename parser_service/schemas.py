"""Event schema builders for Kafka messages.

All builders enforce the Lab04 invariants that events carry schema/run context
and node/edge properties are maps, never null.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .ids import make_content_hash


def utc_now() -> str:
    """Return an ISO UTC event timestamp."""

    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def common_fields(context: Any, file_id: str, file_path: str, event_time: str | None = None) -> dict:
    """Build common event fields.

    TODO: Replace `Any` with ParserContext import if circular import concerns are
    resolved by the final implementation.
    """

    return {
        "schema_version": context.schema_version,
        "event_time": event_time or utc_now(),
        "repo": context.repo_name,
        "commit_sha": context.commit_sha,
        "run_id": context.run_id,
        "file_id": file_id,
        "file_path": file_path,
    }


def build_node_event(
    *,
    context: Any,
    file_id: str,
    file_path: str,
    node_id: str,
    node_type: str,
    scope_path: str,
    lineno: int | None,
    col_offset: int | None,
    end_lineno: int | None,
    end_col_offset: int | None,
    properties: dict | None = None,
) -> dict:
    event = common_fields(context, file_id, file_path)
    event.update(
        {
            "op": "upsert",
            "id": node_id,
            "node_type": node_type,
            "scope_path": scope_path,
            "lineno": lineno,
            "col_offset": col_offset,
            "end_lineno": end_lineno,
            "end_col_offset": end_col_offset,
            "properties": properties or {},
        }
    )
    return event


def build_edge_event(
    *,
    context: Any,
    file_id: str,
    file_path: str,
    edge_id: str,
    source_id: str,
    target_id: str,
    edge_type: str,
    properties: dict | None = None,
) -> dict:
    event = common_fields(context, file_id, file_path)
    event.update(
        {
            "op": "upsert",
            "id": edge_id,
            "source_id": source_id,
            "target_id": target_id,
            "edge_type": edge_type,
            "properties": properties or {},
        }
    )
    return event


def build_metadata_event(
    *,
    context: Any,
    file_id: str,
    file_path: str,
    source: str,
    num_ast_nodes: int,
    num_cfg_edges: int,
    num_dfg_edges: int,
    num_call_edges: int,
    parse_duration_ms: int,
    status: str,
) -> dict:
    num_total_edges = num_cfg_edges + num_dfg_edges + num_call_edges
    event = common_fields(context, file_id, file_path)
    event.update(
        {
            "file_size": len(source.encode("utf-8")),
            "content_hash": make_content_hash(source),
            "num_ast_nodes": num_ast_nodes,
            "num_cfg_edges": num_cfg_edges,
            "num_dfg_edges": num_dfg_edges,
            "num_call_edges": num_call_edges,
            "num_total_edges": num_total_edges,
            "parse_duration_ms": parse_duration_ms,
            "status": status,
        }
    )
    return event


def build_error_event(*, context: Any, file_id: str, file_path: str, error: Exception) -> dict:
    event = common_fields(context, file_id, file_path)
    event.update({"status": "failed", "error_type": type(error).__name__, "message": str(error)})
    return event
