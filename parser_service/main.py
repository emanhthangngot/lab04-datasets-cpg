"""CLI entry point for the Lab04 parser service."""

from __future__ import annotations

import argparse
from pathlib import Path

from .config import build_context
from .discover import discover_python_files
from .parser import process_file
from .producer import build_producer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lab04 incremental CPG parser")
    parser.add_argument("--repo", required=True, help="Path to cloned repository")
    parser.add_argument("--mode", choices=["full", "sample", "file"], default="full")
    parser.add_argument("--file", help="File path for --mode file")
    parser.add_argument("--dry-run", action="store_true", help="Do not connect to Kafka")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = Path(args.repo).resolve()
    context = build_context(repo_root)
    producer = build_producer(context.bootstrap_servers, dry_run=args.dry_run)

    try:
        if args.mode == "file":
            if not args.file:
                raise SystemExit("--file is required when --mode file")
            files = [Path(args.file).resolve()]
        else:
            files = discover_python_files(repo_root)
            if args.mode == "sample":
                files = files[:5]

        for file_path in files:
            metadata = process_file(file_path, producer, context)
            print(metadata)

        producer.flush(timeout=60)
    finally:
        producer.close(timeout=30)


if __name__ == "__main__":
    main()
