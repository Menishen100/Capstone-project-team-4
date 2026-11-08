# Team 4 Week 12 Meeting Minutes

> **Editing rule:** Only the team leader may edit this file.

## Meeting 16

- **Dates:** November 3 and November 5, 2026
- **Time:** 8:30 PM to 9:30 PM EST
- **Location / format:** Fayetteville / Phone
- **Attendees:** Arthur Coleman, Exzavier Pickering, Afriyie Menishen

### Agenda and planned tasks

| Task | Owner | Due date | Status |
| --- | --- | --- | --- |
| Analyze the official held-out false positives and false negatives without retuning | Afriyie Menishen | November 5, 2026 | Completed |
| Review Chi-square and RS behavior for the frozen Week 11 error groups and add regression protections | Arthur Coleman | November 5, 2026 | Completed |
| Analyze DH error groups and evaluate locked-ensemble robustness across payload rates | Exzavier Pickering | November 5, 2026 | Completed |
| Confirm no Week 12 investigation changes the official held-out result | All team members | November 5, 2026 | Completed |

### Results and decisions

- Menishen completed the descriptive analysis of all 40 official Week 11
  prediction rows. The protected outcome counts remain TP `9`, TN `16`, FP
  `4`, and FN `11`.
- Arthur completed the detector-specific Chi-square/RS analysis and regression
  tests that freeze the official FN/FP source populations, a known FN score,
  and existing score-direction behavior.
- Exzavier completed DH outcome-group analysis and a reproducible payload-rate
  experiment with 20 source images at five randomized-LSB rates, for 100
  separate experimental stego images. The locked ensemble detected `25%` at
  payload `0.10`, `45%` at `0.25`, `75%` at `0.50`, and `100%` at `0.75` and
  `1.00`.
- The focused Week 12 suite passed 22 tests across error-case, Arthur
  regression, DH error-analysis, and payload-robustness coverage.
- The team confirmed that the Week 10 configuration stays locked: Chi-square
  `0.00`, RS `0.70`, DH `0.30`, and threshold `0.70`. The Week 11 prediction
  CSV and metrics remain the official final held-out result.

### Next meeting

- **Date and time:** November 10 and November 12, 2026, 8:30 PM to 9:30 PM EST
- **Focus:** Begin Week 13 release-candidate work: polish the CLI, review user
  documentation, and complete an end-to-end usability check.
- **Data safeguard:** Do not use Week 12 observations to recalibrate detector
  scores, ensemble weights, or the locked decision threshold.
