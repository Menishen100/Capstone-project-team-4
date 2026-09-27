# Team 4 Week 6 Meeting Minutes

> **Editing rule:** Only the team leader may edit this file.

## Meeting 10

- **Dates:** September 22 and September 24, 2026
- **Time:** 8:30 PM to 9:30 PM EST
- **Location / format:** Fayetteville / Phone
- **Attendees:** Arthur Coleman, Exzavier Pickering, Afriyie Menishen

### Agenda and tasks

| Task | Owner | Due date | Status |
| --- | --- | --- | --- |
| Expand Chi-square and RS diagnostic output and unit tests | Arthur Coleman | September 24, 2026 | Completed |
| Expand Difference Histogram diagnostic output and unit tests | Exzavier Pickering | September 24, 2026 | Completed |
| Run preliminary development-set scores and produce a score table and defect list | Afriyie Menishen | September 24, 2026 | Completed |
| Review the integrated Week 6 work and run the full test suite | All team members | September 24, 2026 | Completed |

### Results and decisions

- Arthur completed the Chi-square and RS diagnostic/test expansion. The
  diagnostics now include the counts and sample/channel information needed to
  interpret each prototype result, and the tests cover valid inputs, invalid
  inputs, deterministic behavior, score bounds, and input preservation.
- Exzavier completed the Difference Histogram diagnostic/test expansion.
  Coverage includes shared-API behavior, grayscale and RGB channel diagnostics,
  invalid inputs, repeatability, input preservation, and checks against the
  100-clean/100-stego dataset.
- Menishen completed the development-only scoring runner, score table,
  descriptive score summary, and defect list. The run scored 60 clean and 60
  stego images, creating 120 complete records with no Chi-square, RS, or DH
  execution errors.
- The team verified that the runner uses only `split=development`; validation
  and held-out-test images were not used in the preliminary run.
- The full repository test suite passed with 105 tests.
- The team recorded no Week 6 execution defects. It also recorded that detector
  score normalization, threshold selection, and false-positive/false-negative
  analysis remain scheduled for Week 7 rather than being performed early.

### Next meeting

- **Dates and time:** To be confirmed by the team.
- **Focus:** Complete the Week 7 plan: normalize the prototype scores, inspect
  false positives and false negatives on the appropriate development work,
  refine preprocessing where evidence supports it, and document all decisions.
