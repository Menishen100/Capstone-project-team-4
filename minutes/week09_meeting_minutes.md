# Team 4 Week 9 Meeting Minutes

> **Editing rule:** Only the team leader may edit this file.

## Meeting 13

- **Dates:** October 12 and October 14, 2026
- **Time:** 8:30 PM to 9:30 PM EST
- **Location / format:** Fayetteville / Phone
- **Attendees:** Arthur Coleman, Exzavier Pickering, Afriyie Menishen

### Agenda and planned tasks

| Task | Owner | Due date | Status |
| --- | --- | --- | --- |
| Review the Week 9 weighted-voting ensemble implementation and equal-weight baseline | Afriyie Menishen | October 14, 2026 | Completed |
| Review score-direction alignment for Chi-square, RS, and Difference Histogram inputs | Arthur Coleman, Exzavier Pickering, Afriyie Menishen | October 14, 2026 | Completed |
| Verify the baseline does not calibrate on the held-out test split | All team members | October 14, 2026 | Completed |
| Identify Week 10 calibration inputs and plot support needed for weight/threshold selection | Afriyie Menishen, Exzavier Pickering | October 14, 2026 | Completed |

### Results and decisions

- Menishen opened a pull request for the explainable weighted-voting module.
  The baseline uses equal one-third weights and a documented 0.50 decision
  threshold; it is explicitly marked as uncalibrated.
- The implementation validates detector scores and returns the raw scores,
  direction-aligned scores, normalized weights, weighted contributions,
  ensemble score, and `Clean`/`Suspicious` baseline label.
- Arthur's score-direction work keeps Chi-square unchanged and inverts RS so
  that all detector inputs use the same higher-is-more-suspicious convention.
- Exzavier's score-direction work inverts Difference Histogram scores and
  validates ensemble inputs.
- The full test suite recorded for the pull-request review passed 191 tests.
- The team agreed that the equal-weight model is a reproducible Week 9
  baseline, not a calibrated final classifier. The baseline configuration does
  not use validation or held-out-test outcomes to select its weights or
  threshold.
- The team preserved the approved data-split safeguards. Calibration is
  deferred to Week 10 and will use development and validation data only.

### Next meeting

- **Date and time:** October 20 and October 22, 2026, 8:30 PM to 9:30 PM EST
- **Focus:** Begin Week 10 work: run a reproducible grid search for ensemble
  weights and threshold using development and validation data only; preserve
  the held-out test split for final evaluation.
