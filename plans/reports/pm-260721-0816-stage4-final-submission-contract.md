# Stage 4 Final Submission Contract — Project Management Report

Date: 2026-07-21  
Overall status: **IN PROGRESS**

## Progress

- Phase 1 is complete: Stage 4 contract gaps are covered by focused regression
  tests and the canonical specification has a concrete Purpose.
- Phase 2 is complete: acceptance records consistently distinguish technical
  publication from Moodle submission.
- Phase 3 publication gates are complete for source
  `ebf9100e266a8352d7a292fd138aeb02649f9246`; Moodle remains pending.

## Verification

| Gate | Result |
|---|---|
| Focused Stage 4 tests | 12 passed |
| Full Python tests | 142 passed |
| OpenSpec strict validation | 5 passed, 0 failed |
| Stage 3 replay manifest | pass |
| Scaffold checks | pass |
| `git diff --check` | pass |
| Jupyter Book build | Jupyter Book 1.0.3, succeeded |
| Code review | 9.5/10, approved |

## Remaining External Work

- [x] Archived task 9.5: commit the prepared changes, deploy that exact source
  commit, and repeat live acceptance.
- [ ] Archived task 9.6: submit exactly
  `https://emanhthangngot.github.io/lab04-datasets-cpg/` to Moodle.
- [ ] Archived task 9.7: record the checked Moodle item, submission date, and
  exact submitted root URL.
- [ ] Archived task 9.8: mark the whole assignment `COMPLETE` only after both
  `PUBLICATION_DEPLOYED` and `SUBMISSION_RECORDED` are true.

## Blockers

Moodle submission requires the student and is not automated or inferred from the
presence of the URL. Accordingly, the whole assignment is not marked `COMPLETE`.
