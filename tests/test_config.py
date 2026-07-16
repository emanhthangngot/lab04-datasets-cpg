from pathlib import Path

import pytest

from parser_service.config import EXPECTED_REPO_NAME, build_context


def test_build_context_uses_locked_repository_name(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.delenv("REPO_NAME", raising=False)

    context = build_context(tmp_path, run_id="test-run")

    assert context.repo_name == EXPECTED_REPO_NAME == "huggingface/datasets"


def test_build_context_rejects_mixed_repository_identity(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("REPO_NAME", "local-sample/datasets")

    with pytest.raises(
        ValueError,
        match=(
            "expected 'huggingface/datasets', got 'local-sample/datasets'"
        ),
    ):
        build_context(tmp_path, run_id="test-run")
