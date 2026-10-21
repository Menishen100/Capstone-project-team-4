# Arthur Week 10 - Calibration Verification

## Scope

This is an independent verification layer for the ensemble calibration work. It
does not run a competing grid search, change detector algorithms, or use the
held-out test split. Its metric example is synthetic and hand-calculated.

## Implemented safeguards

- `classification_metrics` treats `stego` as positive and reports accuracy,
  precision, recall, and F1. Undefined precision/recall/F1 are reported as zero.
- `predictions_from_scores` uses `score >= threshold` for stego and validates
  both threshold and normalized score ranges.
- `validate_weights` requires exactly the chi, RS, and DH weights, finite and
  non-negative, summing to 1.
- `ensemble_score` consumes normalized [0, 1] detector inputs and inverts raw
  RS as `1 - rs_raw` before applying the weighted vote. Chi-square must be
  normalized to suspiciousness (`1 - p_value`) before this function. DH's
  normalized [0, 1] score is consumed directly.
- `validation_rows` refuses any row whose split is not explicitly
  `validation`, including held-out test rows.
- `verify_selected_configuration` requires the selected weights and threshold
  to match a row in the search results.

## Hand calculation

For truth `[clean, stego, stego, clean]` and predictions
`[clean, stego, clean, clean]`, TP=1, TN=2, FP=0, FN=1. Expected metrics:
are accuracy 3/4 = 0.75, precision 1, recall 1/2 = 0.5, and F1 2/3. A unit
test checks these values directly.

Threshold boundary checks confirm 0.49 is clean, 0.50 is stego, and 0.51 is
stego at threshold 0.50.

## Integration status

The workspace currently contains Week 7 detector snapshots and a development
score CSV. It does not contain the Week 9 ensemble implementation or Menishen's
Week 10 grid-search output. Therefore the following remain pending integration
checks against the official pipeline: chi-square normalization parity, actual
RS direction parity with Week 9, its DH input adapter, validation metric
recalculation, and membership of the official selected row. No official
configuration or validation performance is claimed here.

## Run the verification tests

From `arthur-week7`, run:

```text
python -m pytest tests/test_calibration_metrics.py -q
```

The held-out dataset is not loaded by these tests.
