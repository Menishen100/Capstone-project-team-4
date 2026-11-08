# Team 4 Week 12 Progress Report

## Multi-Feature Steganalysis Toolkit

**Team:** Afriyie Menishen (Team Leader), Arthur Coleman, and Exzavier Pickering  
**Reporting period:** Week 12  
**Planned milestone:** Investigate held-out error cases and payload-rate
robustness; add regression tests without changing the locked evaluation.

## 1. Milestone achieved

The team completed the Week 12 error-analysis and robustness milestone. All
work preserves the Week 10 locked configuration: Chi-square weight `0.00`, RS
weight `0.70`, DH weight `0.30`, and decision threshold `0.70`. The official
Week 11 predictions and metrics remain unchanged.

## 2. Completed work

- Menishen produced the descriptive held-out error table from the 40 official
  Week 11 prediction rows. It preserves the TP `9`, TN `16`, FP `4`, and FN
  `11` outcome counts and records signed distance from the fixed threshold.
- Arthur documented Chi-square and RS behavior across the frozen error groups
  and added regression tests for the exact FN/FP source IDs, a known FN score,
  RS inversion, Chi-square normalization, and group means.
- Exzavier analyzed DH scores by TP/TN/FP/FN outcome and ran a separate,
  reproducible randomized-LSB experiment on 20 clean sources at payload rates
  `0.10`, `0.25`, `0.50`, `0.75`, and `1.00` (100 experimental stego images).
  Detection rates rose from `25%` at `0.10` to `100%` at `0.75` and `1.00`.
- The focused Week 12 regression and robustness suite passed **22 tests**:
  `test_week12_error_analysis.py`, `test_week12_arthur_regression.py`,
  `test_week12_dh_errors.py`, and `test_payload_robustness.py`.

## 3. Safeguards and interpretation

The payload experiment is separate from the official paired dataset and does
not replace the held-out result. Week 12 did not alter detector algorithms,
preprocessing, score direction, weights, or threshold. The results describe
the locked statistical ensemble: lower-payload randomized LSB samples are more
difficult to detect, while the experiment shows stronger detection at higher
payload rates.

## 4. Contributions of each team member

| Team member | Week 12 contribution |
| --- | --- |
| **Afriyie Menishen — Team Leader** | Produced the held-out error-case analysis and integrated the completion evidence. |
| **Arthur Coleman — Member A** | Produced the Chi-square/RS error analysis and regression protections for the official result. |
| **Exzavier Pickering — Member B** | Produced the DH error analysis, payload-rate robustness experiment, plots, CSV, and tests. |
| **All members** | Preserved the immutable Week 11 evaluation and confirmed the Week 12 acceptance evidence. |

## 5. Supporting evidence

- [Week 12 held-out error analysis](../week12-error-analysis.md)
- [Arthur's Week 12 detector analysis](../week12-arthur-error-analysis.md)
- [Exzavier's Week 12 payload robustness report](../week12-payload-robustness.md)
- [Payload robustness results](../../data/week12_payload_robustness.csv)
- [Week 12 meeting minutes](../../minutes/week12_meeting_minutes.md)
