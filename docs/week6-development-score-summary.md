# Week 6 Preliminary Development-Set Scores

## Scope and reproducibility

This is a descriptive Week 6 run across the **development split only**:
60 clean images and their 60 matched LSB-stego images. The validation and
held-out-test splits were not read by the runner.

Command:

```powershell
python -m src.evaluation.run_preliminary_scores
```

Output: `data/development_detector_scores.csv`

The output has 120 rows, all with `split=development` and `status=complete`.
Each row records the common score from all three detectors, the Chi-square
p-value, RS statistic, DH raw roughness, and JSON-form detector diagnostics.

## Descriptive score table

These values are descriptive only. No detector was ranked, no decision
threshold was chosen, and no normalization or ensemble calibration was done.

| Detector score | Clean mean | Stego mean | Clean median | Stego median | Clean range | Stego range |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Chi-square | 0.140474 | 0.188673 | 0.000000 | 0.000000 | 0.000000–0.999962 | 0.000000–1.000000 |
| RS | 0.368833 | 0.290116 | 0.329166 | 0.252701 | 0.121168–0.885328 | 0.092035–0.758024 |
| Difference Histogram | 0.340618 | 0.309736 | 0.368276 | 0.326926 | 0.079907–0.599817 | 0.079933–0.542192 |

## Run summary

```text
Development scoring complete
Clean images scored: 60
Stego images scored: 60
Total images scored: 120
Chi-square errors: 0
RS errors: 0
DH errors: 0
```

Interpretation of relative score behavior, false positives/negatives, score
normalization, and threshold selection is intentionally deferred to Week 7
and later validation work.
