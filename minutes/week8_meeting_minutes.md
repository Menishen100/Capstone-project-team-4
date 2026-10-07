# Team 4 Week 8 Meeting Minutes

> **Editing rule:** Only the team leader may edit this file.

## Meeting 12

- **Dates:** October 6 and October 8, 2026
- **Time:** 8:30 PM to 9:30 PM EST
- **Location / format:** Fayetteville / Phone
- **Attendees:** Arthur Coleman, Exzavier Pickering, Afriyie Menishen

### Agenda and tasks

| Task | Owner | Due date | Status |
| --- | --- | --- | --- |
| Package Chi-square and RS midterm evidence, including diagnostics, limitations, and focused test proof | Arthur Coleman | October 8, 2026 | Completed |
| Package Difference Histogram, LSB embedder, and paired-dataset midterm evidence, including reproducibility and focused test proof | Exzavier Pickering | October 8, 2026 | Completed |
| Assemble the integrated midterm report, demo checklist, and full-suite evidence | Afriyie Menishen | October 8, 2026 | Completed |
| Verify dataset counts/split isolation and full repository test status | All team members | October 8, 2026 | Completed |

### Results and decisions

- Arthur completed the Week 8 Chi-square and RS evidence package. It documents
  each detector's purpose, inputs, bounded score, diagnostics, relevant tests,
  Week 7 development-only observations, and current limitations. Arthur's
  focused test run covered Chi-square, RS, and the Week 7 review safeguards.
- Exzavier completed the Week 8 Difference Histogram, LSB embedder, and
  dataset evidence package. It records the DH diagnostics and prototype score,
  deterministic LSB generation behavior, metadata fields, pair mapping, and
  the clean/stego dataset structure.
- The team confirmed that the dataset contains 100 clean PNG images, 100
  matching stego PNG images, and 100 pair-metadata rows. The pair split remains
  60 development, 20 validation, and 20 held-out-test pairs. Clean/stego
  counterparts remain in the same split.
- Menishen assembled the Week 8 midterm report and demo checklist. The demo
  sequence covers repository structure, metadata, one read-only run of all
  three detectors, development-only score evidence, component evidence, and
  full automated verification.
- The integrated full test suite completed successfully with 123 passing tests
  in 16.66 seconds. The result is recorded as midterm integration evidence.
- The team agreed that the Week 8 package demonstrates working prototypes and
  reproducible evidence, not a final calibrated classifier. No weighted
  ensemble, final threshold, ROC/AUC result, or held-out-test result was
  claimed or selected.
- The team kept the existing preprocessing decision: preserve `L` and `RGB`
  inputs and do not resize, filter, normalize, or otherwise change pixels
  before statistical analysis.

### Next meeting

- **Date and time:** To be scheduled.
- **Focus:** Begin Week 9 work from the approved plan: implement the
  weighted-voting ensemble and a reproducible equal-weight baseline. The team
  will use the existing detector outputs and will not use the held-out test
  split for calibration.
