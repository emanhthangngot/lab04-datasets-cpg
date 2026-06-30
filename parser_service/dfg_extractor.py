"""Lab-level DFG extraction scaffold."""

from __future__ import annotations

import ast
from typing import Iterable


def extract_dfg_edges_gen(*, tree: ast.AST, file_id: str, file_path: str, context) -> Iterable[dict]:
    """Yield DFG_DEF_USE edges.

    TODO: Track local assignment definitions and later Name loads inside each
    function/module scope. Keep this intra-procedural for the lab report.
    """

    return iter(())
