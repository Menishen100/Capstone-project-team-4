# Week 12 Held-Out Error Analysis

This report is generated from the official `data/week11_heldout_predictions.csv`
without rescoring images. The error-case table is
[`data/week12_error_cases.csv`](../data/week12_error_cases.csv), with one row
for each of the 11 false negatives and 4 false positives. It includes raw and
normalized detector scores plus signed distance from the unchanged 0.70
threshold.

## Confusion groups

| Outcome | Count |
|---|---:|
| True positive | 9 |
| True negative | 16 |
| False positive | 4 |
| False negative | 11 |

False-negative IDs: source-081, source-082, source-085, source-090, source-091,
source-092, source-094, source-097, source-098, source-099, source-100.

False-positive IDs: source-083, source-084, source-088, source-096.

## Findings

Ten of 15 errors are within 0.10 of threshold; six are within 0.05. For the
false negatives specifically, six are within 0.10 and two within 0.05. Other
misses are farther below threshold, so the errors are not all borderline.
Arthur's score comparison finds mean normalized RS suspiciousness of 0.5745
for FNs versus 0.7592 for TPs; Chi-square's mean FN score is 0.0941 but its
locked weight is 0.00. FP rows have mean normalized RS 0.7239 and normalized DH
0.7798, consistent with elevated detector suspiciousness on those clean
images.

Payload-rate robustness and whether low payload degrades detection require
Exzavier's separate Week 12 experiment. The Week 11 held-out set has no payload
rate dimension. Source difficulty across conditions also cannot be concluded
from one pair per source.

## Locked configuration

Chi-square weight 0.00, RS weight 0.70, DH weight 0.30, threshold 0.70. This
week is diagnostic only: no threshold or weights were reselected, no detector
formula or normalization changed, and official Week 11 predictions and metrics
were not edited. See [Arthur's detailed score analysis](week12-arthur-error-analysis.md).

Evidence caption: **Menishen Week 12 – Held-out error-case analysis and
robustness integration evidence.** Payload integration remains pending the
separate robustness experiment.
