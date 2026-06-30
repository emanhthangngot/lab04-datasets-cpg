"""Discover Python source files for the selected upstream repository."""

from __future__ import annotations

from pathlib import Path


EXCLUDED_PARTS = {
    "tests",
    "docs",
    "notebooks",
    "benchmarks",
    "templates",
    "__pycache__",
}


def discover_python_files(repo_root: Path) -> list[Path]:
    """Return sorted `src/datasets/**/*.py` files, excluding non-core folders.

    TODO: Capture total discovered and selected counts in notebook 01.
    Do not exclude `src/datasets/utils`; it is core library code.
    """

    source_root = repo_root / "src" / "datasets"
    selected_files: list[Path] = []

    for path in sorted(repo_root.rglob("*.py")):
        if path.name == "setup.py":
            continue
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        if source_root in path.parents or path == source_root:
            selected_files.append(path)

    return selected_files
