"""Runtime configuration for the Lab04 parser service.

TODO: Extend validation when real deployment config stabilizes. The parser runs
inside Docker Compose by default, so `broker:9092` is the normal bootstrap
server. Use `KAFKA_BOOTSTRAP_EXTERNAL` only when deliberately running on host.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from uuid import uuid4


@dataclass(frozen=True)
class ParserContext:
    repo_root: Path
    repo_name: str
    commit_sha: str
    run_id: str
    schema_version: str
    bootstrap_servers: str


def build_context(repo_root: Path, run_id: str | None = None) -> ParserContext:
    """Build parser context from environment and CLI inputs."""

    # TODO: Replace unknown commit fallback with `git -C repo_root rev-parse HEAD`
    # once clone workflow is guaranteed to exist in every run.
    commit_sha = os.environ.get("COMMIT_SHA", "unknown")
    return ParserContext(
        repo_root=repo_root,
        repo_name=os.environ.get("REPO_NAME", "huggingface/datasets"),
        commit_sha=commit_sha,
        run_id=run_id or os.environ.get("RUN_ID", uuid4().hex),
        schema_version=os.environ.get("SCHEMA_VERSION", "1.0"),
        bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "broker:9092"),
    )
