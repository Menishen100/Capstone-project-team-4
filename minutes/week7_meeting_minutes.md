# Team 4 Week 7 Meeting Minutes

> **Editing rule:** Only the team leader may edit this file.

## Meeting 11

- **Dates:** September 28 and October 1, 2026
- **Time:** 8:30 PM to 9:30 PM EST
- **Location / format:** Fayetteville / Phone
- **Attendees:** Arthur Coleman, Exzavier Pickering, Afriyie Menishen

### Agenda and tasks

| Task | Owner | Due date | Status |
| --- | --- | --- | --- |
| Analyze Chi-square and RS development scores; record candidate error cases | Arthur Coleman | October 1, 2026 | Completed |
| Analyze Difference Histogram score normalization, diagnostics, and candidate error cases | Exzavier Pickering | October 1, 2026 | Completed |
| Produce the combined preliminary validation summary and preprocessing decision record | Afriyie Menishen | October 1, 2026 | Completed |
| Review the Week 7 work, confirm split isolation, and run the full test suite | All team members | October 1, 2026 | Completed |

### Results and decisions

- Arthur completed the Chi-square and RS development-score review. The review
  records descriptive clean/stego statistics and threshold-free candidate cases
  without selecting a production threshold or ensemble weight.
- Exzavier completed the Difference Histogram development-score review. The
  review verified the existing bounded normalization formula, inspected paired
  clean/stego behavior and DH diagnostics, and recorded candidate cases.
- Menishen completed the development-only preliminary validation summary. It
  combines all three detector observations, records candidate false-positive
  and false-negative cases by source ID and filename, and documents the
  normalization and preprocessing decisions.
- The team retained the existing shared preprocessing behavior: preserve native
  grayscale/RGB images, avoid resizing/filtering/pixel-value normalization, and
  do not introduce a pixel-changing adjustment without evidence.
- The team retained the current bounded prototype scores for descriptive work
  only. Final direction transformations, thresholds, ensemble weighting, ROC,
  AUC, validation selection, and held-out evaluation remain scheduled for later
  weeks.
- The review used the 60 clean and 60 stego development images only; validation
  and held-out-test data were not used.
- The full repository test suite passed with 123 tests after the DH review test
  was made pytest-discoverable.

### Next meeting

- **Dates:** October 6 and October 8, 2026
- **Time:** 8:30 PM to 9:30 PM EST
- **Focus:** Complete the Week 8 plan: package the midterm evidence, including
  the dataset description, three working detectors, supporting test evidence,
  and the midterm report/demo materials.
