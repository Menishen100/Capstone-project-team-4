# Arthur Week 11 — Held-Out Metric Verification

## Scope

This verification consumes Menishen's official Week 11 per-image prediction
CSV and metrics JSON. It does not load images, invoke detectors, change scores,
or tune the locked configuration. The official files were available on
`main` on October 31, 2026, and the verifier passed against them.

## Checks performed

- Metadata contains exactly 20 unique `held_out_test` sources, and the result
  contains exactly 40 rows: one clean and one stego image for every source.
- Labels and predictions use `clean`/`stego`; result source IDs match the held-
  out metadata set, excluding development and validation data.
- The selected configuration is Chi 0.00, RS 0.70, DH 0.30, threshold 0.70.
- Each row's normalized fields are checked with the official Week 9 functions
  in `src/ensemble/normalization.py`. Ensemble scores and output labels are
  recalculated with `combine_detector_scores` in `src/ensemble/voting.py` using
  the locked configuration.
- Accuracy, precision, recall, F1, TP, TN, FP, and FN are recomputed. Confusion
  counts must sum to 40.

The checker uses the existing official normalization and voting code rather
than maintaining a separate interpretation. It verifies the supplied raw and
normalized score columns and the official result summaries independently.

## Official held-out verification result

Command: `python -m src.evaluation.heldout_metrics`

Result: **passed** on all 40 official prediction rows. The file contains 20
clean and 20 stego images from the 20 held-out metadata sources, with one of
each class per source. The locked weights and threshold match the Week 10
configuration.

| Check | Independently verified result |
| --- | ---: |
| TP | 9 |
| TN | 16 |
| FP | 4 |
| FN | 11 |
| Accuracy | 0.6250 |
| Precision | 0.6923 |
| Recall | 0.4500 |
| F1 | 0.5455 |

The reported and recomputed results agree. The confusion counts sum to 40.
These results are recorded as observed; no weights, threshold, detector
behavior, or predictions were changed.

## Run

After Menishen's official result files are available at their suggested paths:

```powershell
python -m src.evaluation.heldout_metrics
```

Or supply paths explicitly:

```powershell
python -m src.evaluation.heldout_metrics --predictions data/week11_heldout_predictions.csv --metrics data/week11_heldout_metrics.json --metadata data/metadata.csv
```

The focused unit tests use synthetic, hand-checkable examples. They test all
four confusion cells and metric arithmetic, the 40-row paired held-out
structure, locked settings, official score/prediction parity, and rejection of
non-held-out IDs and incorrect summaries:

```powershell
python -m pytest tests/test_heldout_metrics.py -q
```

