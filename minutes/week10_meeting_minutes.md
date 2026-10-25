# Team 4 Week 10 Meeting Minutes

> **Editing rule:** Only the team leader may edit this file.

## Meeting 14

- **Dates:** October 20 and October 22, 2026
- **Time:** 8:30 PM to 9:30 PM EST
- **Location / format:** Fayetteville / Phone
- **Attendees:** Arthur Coleman, Exzavier Pickering, Afriyie Menishen

### Agenda and planned tasks

| Task | Owner | Due date | Status |
| --- | --- | --- | --- |
| Run the Week 10 ensemble weight and threshold grid search using only development and validation data | Afriyie Menishen | October 22, 2026 | Completed |
| Independently verify calibration metrics, weight/threshold validation, and selected-row safeguards | Arthur Coleman | October 22, 2026 | Completed |
| Produce validation-only plots and compare the equal-weight baseline with the selected configuration | Exzavier Pickering | October 22, 2026 | Completed |
| Confirm that held-out-test rows are excluded from calibration and plotting | All team members | October 22, 2026 | Completed |

### Results and decisions

- Menishen completed a reproducible grid search over 594 configurations: 66
  normalized weight triples and 9 decision thresholds. The workflow reads only
  the development and validation splits before loading images.
- The selected validation configuration is Chi-square `0.00`, RS `0.70`, DH
  `0.30`, with a decision threshold of `0.70`.
- The selected validation metrics are accuracy `0.7500`, precision `0.7273`,
  recall `0.8000`, and F1 `0.7619`. The team recorded these as calibration
  results, not final project-performance claims.
- Arthur completed independent checks for positive-class metrics, inclusive
  threshold behavior, valid normalized weights, selected-row membership, and
  validation-only input handling. These checks reject held-out rows.
- Exzavier completed validation F1 and accuracy plots for the selected weights
  and a validation-only comparison between the equal-weight baseline and the
  selected configuration. The plots support the already documented selection;
  they do not perform another search or choose a new threshold.
- The team confirmed that 120 development rows and 40 validation rows were
  used for Week 10 work, while zero held-out rows were read, scored, or used.
- After installing the declared Matplotlib dependency, the merged Week 10
  repository test suite passed **218 tests**.
- The team locked the Week 10 selected configuration for the next stage. It
  must not be changed using held-out-test outcomes.

### Next meeting

- **Date and time:** October 27 and October 29, 2026, 8:30 PM to 9:30 PM EST
- **Focus:** Begin Week 11 held-out evaluation using the locked Week 10
  configuration. Calculate accuracy, precision, recall, F1, ROC, AUC, and
  confusion matrices, and prepare the corresponding metrics tables and plots.
- **Data safeguard:** Do not re-tune detector weights, score direction, or the
  decision threshold using held-out-test results.
