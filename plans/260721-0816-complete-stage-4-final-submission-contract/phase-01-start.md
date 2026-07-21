---
phase: 1
title: "Tests and Contract Gaps"
status: completed
priority: P1
effort: "small"
dependencies: []
---

# Phase 1: Tests and Contract Gaps

## Overview

Add regression tests first, then expand the active/archive and canonical Stage 4 specifications to be self-contained against the assignment.

## Requirements

- Functional: per-task content, Architecture, public repository, and Moodle completion contracts are explicit.
- Non-functional: Stage 1-3 runtime/schema/evidence contracts remain unchanged.

## Implementation Steps

1. Add focused static assertions for missing final-submission requirements.
2. Run focused tests and prove the assertions fail.
3. Update delta/canonical spec, design, proposal, and tasks consistently.
4. Run focused tests and OpenSpec strict validation.

## Todo

- [x] Tests fail before contract edits and pass afterward.
- [x] Canonical Purpose is no longer generated `TBD`.
- [x] Completion requires Moodle checkbox, date, and exact URL.

## Success Criteria

- [x] Every authoritative assignment condition is traceable in Stage 4.
- [x] Observable scenarios distinguish publication, submission, and completion.

## Completion Record

Completed locally on 2026-07-21. The focused Stage 4 suite passes with 11 tests,
the canonical `final-publication` specification has a concrete Purpose, and the
archive/canonical contracts require the Moodle checkbox, date, and exact root
URL before whole-assignment completion.
