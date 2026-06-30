"""Lab-level CFG extraction scaffold."""

from __future__ import annotations

import ast
from typing import Iterable


def extract_cfg_edges_gen(*, tree: ast.AST, file_id: str, file_path: str, context) -> Iterable[dict]:
    """Yield CFG edge events.

    TODO: Implement sequential statement edges plus If/Loop/Return edges:
    CFG_NEXT, CFG_TRUE, CFG_FALSE, CFG_LOOP_BODY, CFG_LOOP_BACK, CFG_RETURN.
    """

    return iter(())
