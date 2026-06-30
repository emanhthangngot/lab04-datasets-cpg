"""Local verification helpers for notebooks and scripts."""

from __future__ import annotations


def metadata_total_is_consistent(metadata: dict) -> bool:
    """Return True when metadata total edge count matches component counts."""

    return metadata.get("num_total_edges") == (
        metadata.get("num_cfg_edges", 0)
        + metadata.get("num_dfg_edges", 0)
        + metadata.get("num_call_edges", 0)
    )
