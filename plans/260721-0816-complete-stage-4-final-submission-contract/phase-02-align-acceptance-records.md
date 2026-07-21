---
phase: 2
title: "Align Acceptance Records"
status: completed
priority: P1
effort: "small"
dependencies: [1]
---

# Phase 2: Align Acceptance Records

## Overview

Remove premature whole-assignment completion claims and preserve verified deployment evidence without claiming Moodle submission.

## Requirements

- Functional: trackers identify technical publication as passed and Moodle as pending.
- Non-functional: existing verified workflow/SHA/URL evidence remains intact.

## Implementation Steps

1. Reconcile book index, README, and team tracker terminology.
2. Label `7ae8a83` as the verified publication source, not the immutable final tip.
3. Keep Moodle unchecked until the user confirms actual submission.
4. Ensure archive tasks describe required post-edit deployment/live review.

## Todo

- [x] No `COMPLETE` claim while Moodle is pending.
- [x] Active/archive links are consistent.
- [x] Submission record template captures checkbox/date/exact URL.

## Success Criteria

- [x] All acceptance records describe the same current state.

## Completion Record

Completed locally on 2026-07-21. README, book index, team trackers, and the
archived Stage 4 checklist consistently separate technical publication from
Moodle submission. After the later `main` deployment, the current state is
`PUBLICATION_DEPLOYED`; Moodle status, submission date, and exact URL remain
`PENDING`.
