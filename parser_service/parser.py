"""Orchestrate per-file parsing and event emission."""

from __future__ import annotations

import ast
import gc
import time
from pathlib import Path

from .ast_extractor import extract_ast_nodes_gen
from .call_extractor import extract_call_edges_gen
from .cfg_extractor import extract_cfg_edges_gen
from .dfg_extractor import extract_dfg_edges_gen
from .ids import make_file_id, normalize_relative_path
from .schemas import build_error_event, build_metadata_event


def iter_edge_events(*, tree: ast.AST, file_id: str, file_path: str, context):
    """Yield all edge events from CFG, DFG, and CALL extractors."""

    yield from extract_cfg_edges_gen(tree=tree, file_id=file_id, file_path=file_path, context=context)
    yield from extract_dfg_edges_gen(tree=tree, file_id=file_id, file_path=file_path, context=context)
    yield from extract_call_edges_gen(tree=tree, file_id=file_id, file_path=file_path, context=context)


def process_file(file_path: Path, producer, context) -> dict:
    """Process one Python file and flush producer after that file.

    TODO: Complete CFG/DFG/CALL extractors, then this function will emit all
    required event categories for the lab.
    """

    start_time = time.time()
    source = ""
    tree = None

    try:
        relative_path = normalize_relative_path(file_path, context.repo_root)
        file_id = make_file_id(context.repo_name, relative_path)
        source = file_path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=relative_path)

        node_count = 0
        cfg_count = 0
        dfg_count = 0
        call_count = 0

        for node_event in extract_ast_nodes_gen(
            tree=tree, file_id=file_id, file_path=relative_path, context=context
        ):
            producer.send("cpg.nodes", key=file_id, value=node_event)
            node_count += 1

        for edge_event in iter_edge_events(
            tree=tree, file_id=file_id, file_path=relative_path, context=context
        ):
            producer.send("cpg.edges", key=file_id, value=edge_event)
            edge_type = edge_event["edge_type"]
            if edge_type.startswith("CFG"):
                cfg_count += 1
            elif edge_type.startswith("DFG"):
                dfg_count += 1
            elif edge_type.startswith("CALL"):
                call_count += 1

        metadata = build_metadata_event(
            context=context,
            file_id=file_id,
            file_path=relative_path,
            source=source,
            num_ast_nodes=node_count,
            num_cfg_edges=cfg_count,
            num_dfg_edges=dfg_count,
            num_call_edges=call_count,
            parse_duration_ms=int((time.time() - start_time) * 1000),
            status="success",
        )
        producer.send("cpg.metadata", key=file_id, value=metadata)
        producer.flush(timeout=30)
        return metadata

    except SyntaxError as error:
        relative_path = str(file_path)
        file_id = make_file_id(context.repo_name, relative_path)
        error_event = build_error_event(
            context=context, file_id=file_id, file_path=relative_path, error=error
        )
        producer.send("cpg.errors", key=file_id, value=error_event)
        producer.flush(timeout=30)
        return error_event

    finally:
        del tree
        gc.collect()
