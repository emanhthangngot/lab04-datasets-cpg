#!/usr/bin/env bash
set -euo pipefail

# Backward-compatible entry point retained for the Lab04 quickstart.
# Stage 3 requires a clean baseline and strict evidence, so the canonical
# workflow owns the source mutation, replay, cleanup, and restoration steps.

exec bash scripts/run_stage3_evidence.sh "$@"
