"""Runtime configuration for the Lab04 parser service.

The parser runs inside Docker Compose by default, so `broker:9092` is the
normal bootstrap server. Deployment validation is intentionally limited to the
lab contract. Use `KAFKA_BOOTSTRAP_EXTERNAL` only for deliberate host runs.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from uuid import uuid4


EXPECTED_REPO_NAME = "huggingface/datasets"


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

    # Canonical runs supply COMMIT_SHA explicitly. The fallback keeps isolated
    # local tests usable when clone metadata is intentionally absent.
    commit_sha = os.environ.get("COMMIT_SHA", "unknown")
    repo_name = os.environ.get("REPO_NAME", EXPECTED_REPO_NAME)
    if repo_name != EXPECTED_REPO_NAME:
        raise ValueError(
            "Invalid REPO_NAME: "
            f"expected {EXPECTED_REPO_NAME!r}, got {repo_name!r}"
        )

    return ParserContext(
        repo_root=repo_root,
        repo_name=repo_name,
        commit_sha=commit_sha,
        run_id=run_id or os.environ.get("RUN_ID", uuid4().hex),
        schema_version=os.environ.get("SCHEMA_VERSION", "1.0"),
        bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "broker:9092"),
    )
