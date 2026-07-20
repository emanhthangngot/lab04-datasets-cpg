"""Pytest configuration for Lab04 repository tests."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DummyContext:
    repo_root: Path
    repo_name: str = "huggingface/datasets"
    commit_sha: str = "test-sha"
    run_id: str = "test-run"
    schema_version: str = "1.0"
    bootstrap_servers: str = "broker:9092"
