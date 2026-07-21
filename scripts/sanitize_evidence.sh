#!/usr/bin/env bash
set -euo pipefail

for file in "$@"; do
  [ -f "$file" ] || continue
  sed -i \
    -e 's/"neo4j\.authentication\.basic\.password"[[:space:]]*:[[:space:]]*"[^"]*"/"neo4j.authentication.basic.password": "***REDACTED***"/g' \
    -e 's/"neo4j\.authentication\.basic\.username"[[:space:]]*:[[:space:]]*"[^"]*"/"neo4j.authentication.basic.username": "***REDACTED***"/g' \
    "$file"
done
