# Week 14 Final Release Checklist

## Menishen final integration audit

**Audit target:** merged `main` at `ba49c19`, containing Arthur's final QA
(PR #72) and Exzavier's final documentation/reproducibility work (PR #73).

- [x] Full source code, tests, dataset assets, generation workflow, and docs present
- [x] Declared requirements installed in a fresh virtual environment
- [x] `pip check` reported no broken requirements
- [x] Full test suite passed: **281 passed**
- [x] CLI help and documented clean/stego examples passed
- [x] Optional GUI launched and displayed a completed analysis result
- [x] README commands, local documentation links, and example paths verified
- [x] Dataset metadata and generation/reproducibility workflow present
- [x] Locked configuration preserved: Chi-square `0.00`, RS `0.70`, DH `0.30`, threshold `0.70`
- [x] Official Week 11 metrics and predictions preserved; no held-out recalibration occurred
- [x] Arthur and Exzavier Week 14 contributions merged to `main`
- [x] All three members have identifiable, meaningful Week 14 contributions
- [x] Release audit, Week 14 report, and Meeting 18 minutes completed
- [x] Main branch release content reviewed for tracked temporary artifacts and broken local documentation links
- [ ] Merge Menishen's final-release audit commit into `main`
- [ ] Create and push annotated tag `v1.0-final` as the final release action

The final two items remain unchecked in this committed file because the tag
must be created only after this audit record is merged into `main`. The tag
will be the final repository mutation and will point to the fully audited
release commit.

See [Menishen's final release audit](week14-menishen-final-release-audit.md)
for commands, observations, and the preserved official configuration.
