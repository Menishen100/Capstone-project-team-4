# Arthur Week 11 — Held-Out Metric Verification

## Scope

This verification consumes Menishen's official Week 11 per-image prediction
CSV and metrics JSON. It does not load images, invoke detectors, change scores,
or tune the locked configuration. The official artifacts are not yet present in
this workspace, so the checker is ready to run after those files are integrated.

## Checks performed

- Metadata contains exactly 20 unique `held_out_test` sources, and the result
  contains exactly 40 rows: one clean and one stego image for every source.
- Labels and predictions use `clean`/`stego`; result source IDs match the held-
  out metadata set, excluding development and validation data.
- The selected configuration is Chi 0.00, RS 0.70, DH 0.30, threshold 0.70.
- Every reported ensemble score is recalculated using the repository's existing
  `ensemble_score` helper, including its Week 9 RS inversion convention. The
  existing threshold helper is used to verify binary predictions.
- Accuracy, precision, recall, F1, TP, TN, FP, and FN are recomputed. Confusion
  counts must sum to 40.

The checker deliberately verifies the score columns supplied by the official
runner rather than independently recalculating detector normalization. This
keeps Arthur's role as result verification and avoids a second evaluation path.

## Run

After Menishen's official result files are available at their suggested paths:

```powershell
python -m src.evaluation.heldout_metrics
```

Or supply paths explicitly:

```powershell
python -m src.evaluation.heldout_metrics --predictions data/week11_heldout_predictions.csv --metrics data/week11_heldout_metrics.json --metadata data/metadata.csv
```

The focused unit tests use a synthetic, hand-checkable example and do not read
the held-out images or claim final held-out performance:

```powershell
python -m pytest tests/test_heldout_metrics.py -q
```

The official held-out verification cannot be reported as passed until the
official prediction CSV and metrics JSON are supplied and checked.
