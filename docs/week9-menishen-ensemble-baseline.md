# Week 9 Ensemble and Equal-Weight Baseline

## Purpose

This document records Menishen's Week 9 integration deliverable: an
explainable weighted-voting module and a reproducible equal-weight baseline.
It builds on the score-direction alignment contributed by Arthur and Exzavier.

## Baseline configuration

`src/ensemble/voting.py` defines `EQUAL_WEIGHT_BASELINE`:

| Detector | Raw score preparation | Baseline weight |
| --- | --- | ---: |
| Chi-square | Unchanged | 1/3 |
| RS | `1 - raw_score` | 1/3 |
| Difference Histogram | `1 - raw_score` | 1/3 |

The ensemble score is the weighted sum of the three direction-aligned scores.
The Week 9 baseline reports `Suspicious` when the score is at least `0.50` and
otherwise reports `Clean`. The result includes raw scores, normalized scores,
weights, each weighted contribution, threshold, configuration name, and a
`calibrated: false` marker.

The `0.50` threshold is a reproducible baseline choice, not a final operating
threshold or probability claim. Week 10 will select final weights and threshold
from the approved development/validation workflow. The held-out test split is
not read or used by this module.

## Reproducible use

```python
from src.ensemble.voting import combine_detector_scores

result = combine_detector_scores(
    {"chi_square": 0.30, "rs": 0.20, "dh": 0.80}
)
print(result["label"])
print(result["ensemble_score"])
```

The example direction-aligns the inputs to `0.30`, `0.80`, and `0.20`, giving
an equal-weight baseline score of `0.433333...` and the label `Clean`.

## Test coverage

`tests/test_ensemble_voting.py` verifies:

- direction alignment and equal weighting;
- score calculation and threshold boundary behavior;
- reproducible custom weights for later calibration;
- missing or invalid detector scores;
- invalid weights and thresholds; and
- explanatory diagnostics and the uncalibrated status marker.

Run the focused tests with:

```powershell
.venv\Scripts\python.exe -m pytest tests/test_ensemble_normalization.py tests/test_ensemble_input_validation.py tests/test_ensemble_voting.py -v
```
