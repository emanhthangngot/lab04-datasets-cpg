---
phase: 3
title: "Verify and Review"
status: in-progress
priority: P1
effort: "small"
dependencies: [1, 2]
---

# Phase 3: Verify and Review

## Overview

Run local contract gates, review the complete diff, and hand off the remaining external Moodle/deployment actions truthfully.

## Requirements

- Functional: focused and full validation pass.
- Non-functional: no runtime/schema/evidence regression and no user changes are lost.

## Implementation Steps

1. Run focused Stage 4 tests.
2. Run full checks, OpenSpec strict, manifest, syntax, and diff validation.
3. Review changed contracts and acceptance claims.
4. Update plan status and produce completion/handoff report.

## Todo

- [x] Zero test/OpenSpec/manifest failures in local verification.
- [x] No contradiction between target content and current claims.
- [x] External steps are explicitly pending.
- [x] Complete task 9.5: commit the reviewed local changes, deploy the resulting
  source commit, and repeat live acceptance.
- [ ] Complete tasks 9.6-9.8: submit the exact Pages root URL to Moodle, record
  the date and URL, then mark the whole assignment complete.

## Success Criteria

- [x] Local implementation passes focused/full tests, strict OpenSpec,
  manifest, scaffold, diff, and Jupyter Book build gates.
- [x] Local code review approved the prepared changes at 9.5/10.
- [x] The current source commit is deployed and live-review approved.
- [ ] Moodle submission is recorded and the whole assignment is complete.

## Verification Record

Local checks run on 2026-07-21:

- focused Stage 4 tests: 12 passed;
- full Python suite: 142 passed;
- strict OpenSpec: 5 passed, 0 failed;
- Stage 3 replay manifest: pass;
- scaffold checks and `git diff --check`: pass;
- Jupyter Book 1.0.3 build: succeeded.
- code review: 9.5/10, approved.

Current update deployment and live review completed on 2026-07-21:

- source commit: `ebf9100e266a8352d7a292fd138aeb02649f9246`;
- publication workflow:
  https://github.com/emanhthangngot/lab04-datasets-cpg/actions/runs/29794123254
  — conclusion `success`;
- Pages deploy:
  https://github.com/emanhthangngot/lab04-datasets-cpg/actions/runs/29794146923
  — conclusion `success`;
- live root, Architecture, Task 1-6, Reflection, and required images returned
  HTTP 200.

The phase remains in progress because manual Moodle actions in tasks 9.6-9.8 are
still pending.
