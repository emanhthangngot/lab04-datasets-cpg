---
title: "Complete Stage 4 Final Submission Contract"
description: "Make Stage 4 self-contained against the assignment and remove premature completion claims."
status: in-progress
priority: P1
effort: "1 session plus manual Moodle submission"
tags: [stage4, openspec, publication, submission]
created: 2026-07-21
---

# Complete Stage 4 Final Submission Contract

## Overview

Strengthen the final-publication capability, tests, and acceptance records while preserving Stage 3 runtime contracts and evidence. Local work stops at a truthful submission-ready state; only the student can perform the Moodle submission.

## Goals

| # | Goal | Priority |
|---|------|----------|
| 1 | Cover every assignment submission requirement in Stage 4 | P1 |
| 2 | Make publication/submission/completion states non-circular | P1 |
| 3 | Verify static contracts and repository gates | P1 |

## Phases

| # | Phase | Status |
|---|-------|--------|
| 1 | [Phase 1: Tests and contract gaps](./phase-01-start.md) | Completed |
| 2 | [Phase 2: Align acceptance records](./phase-02-align-acceptance-records.md) | Completed |
| 3 | [Phase 3: Verify and review](./phase-03-strengthen-stage-4-contract.md) | In progress (external actions pending) |

## Success Criteria

- [x] Canonical Stage 4 spec maps all assignment lines 69-96 to observable scenarios.
- [x] Moodle checkbox/date/URL are required before whole-assignment completion.
- [x] No file claims Moodle submission occurred before the user performs it.
- [x] Focused tests, full tests, OpenSpec strict, manifest, syntax, diff, and book-build gates pass locally.
- [x] Manual external steps are clearly separated from locally completed work.

## Progress

Local implementation and validation are complete. The overall plan remains
`in-progress` because the current source has not completed archived task 9.5
(reviewed commit, deployment, and repeated live acceptance), and Moodle tasks
9.6-9.8 require a student action and submission record.

## Remaining Blockers

1. Publish the current prepared changes through a reviewed branch, record the
   deployed source commit, and repeat the nine-page/asset live review.
2. Submit exactly `https://emanhthangngot.github.io/lab04-datasets-cpg/` to
   Moodle and record the checked item, submission date, and exact URL.

<!-- slug: complete-stage-4-final-submission-contract -->
