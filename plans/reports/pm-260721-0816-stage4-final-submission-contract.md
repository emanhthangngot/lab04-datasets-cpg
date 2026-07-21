# Stage 4 Final Submission Contract — Project Management Report

Date: 2026-07-21  
Overall status: **IN PROGRESS**

## Progress

- Phase 1 is complete: Stage 4 contract gaps are covered by focused regression
  tests and the canonical specification has a concrete Purpose.
- Phase 2 is complete: acceptance records consistently distinguish the prior
  verified publication (`7ae8a832`) from the current unpublished update, and
  Moodle remains pending.
- Phase 3 local gates are complete, but the phase remains in progress while
  external deployment/live review and Moodle actions are outstanding.

## Verification

| Gate | Result |
|---|---|
| Focused Stage 4 tests | 11 passed |
| Full Python tests | 141 passed |
| OpenSpec strict validation | 5 passed, 0 failed |
| Stage 3 replay manifest | pass |
| Scaffold checks | pass |
| `git diff --check` | pass |
| Jupyter Book build | Jupyter Book 1.0.3, succeeded |
| Code review | 9.5/10, approved |

## Remaining External Work

- [ ] Archived task 9.5: commit the prepared changes through a reviewed branch,
  deploy that exact source commit, and repeat live acceptance.
- [ ] Archived task 9.6: submit exactly
  `https://emanhthangngot.github.io/lab04-datasets-cpg/` to Moodle.
- [ ] Archived task 9.7: record the checked Moodle item, submission date, and
  exact submitted root URL.
- [ ] Archived task 9.8: mark the whole assignment `COMPLETE` only after both
  `PUBLICATION_DEPLOYED` and `SUBMISSION_RECORDED` are true.

## Blockers

The current working-tree content cannot be called deployed or live-reviewed
until task 9.5 is performed. Moodle submission requires the student and is not
automated or inferred from the presence of the URL. Accordingly, neither the
plan nor Phase 3 is marked complete.
