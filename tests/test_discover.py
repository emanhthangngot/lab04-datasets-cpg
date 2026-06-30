from pathlib import Path

from parser_service.discover import discover_python_files


def touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("x = 1\n", encoding="utf-8")


def test_discover_keeps_src_datasets_utils(tmp_path: Path) -> None:
    repo = tmp_path / "datasets"
    keep = repo / "src" / "datasets" / "utils" / "py_utils.py"
    touch(keep)
    touch(repo / "src" / "datasets" / "features" / "features.py")
    touch(repo / "tests" / "test_utils.py")
    touch(repo / "docs" / "conf.py")
    touch(repo / "setup.py")

    selected = [p.relative_to(repo).as_posix() for p in discover_python_files(repo)]

    assert "src/datasets/utils/py_utils.py" in selected
    assert "src/datasets/features/features.py" in selected
    assert "tests/test_utils.py" not in selected
    assert "docs/conf.py" not in selected
    assert "setup.py" not in selected
