# Week 10 Ensemble Calibration Results

## Scope and data protection

This is Menishen's Week 10 calibration result. It evaluates only the approved
development and validation splits from `data/metadata.csv`:

| Split | Images used | Purpose |
| --- | ---: | --- |
| Development | 120 (60 clean, 60 stego) | Report candidate behavior |
| Validation | 40 (20 clean, 20 stego) | Select the Week 10 configuration |
| Held-out test | 0 | Not read, scored, or used |

The runner filters metadata to `development` and `validation` before loading
images. `ScoredImage` rejects every other split, including `held_out_test`.
The result is a calibration choice, **not** a final project-performance claim.

## Reproducible search design

Run the search from the repository root:

```powershell
.venv\Scripts\python.exe -m src.evaluation.grid_search_ensemble --output data\week10_grid_search_results.csv
```

The runner scores the current detector outputs, direction-aligns them through
the Week 9 ensemble boundary (Chi-square unchanged; RS and DH inverted), and
evaluates the following fixed candidate grid:

- weights: every non-negative triple in increments of `0.10` that sums to
  `1.00` — 66 combinations;
- thresholds: `0.30` through `0.70` inclusive in increments of `0.05` — 9
  values; and
- total configurations: 594.

The selection rule is fixed before inspecting results: maximize **validation
F1**. Exact ties are resolved by validation recall, validation precision,
validation accuracy, threshold closest to `0.50`, then lexicographically
smallest `(Chi-square, RS, DH)` weights. Development metrics are retained in
the CSV for transparency but never select or break ties between configurations.

## Selected configuration

| Setting | Selected value |
| --- | ---: |
| Chi-square weight | 0.00 |
| RS weight | 0.70 |
| Difference Histogram weight | 0.30 |
| Decision threshold | 0.70 |

## Validation metrics

| Metric | Validation result |
| --- | ---: |
| Accuracy | 0.7500 |
| Precision | 0.7273 |
| Recall | 0.8000 |
| F1 | 0.7619 |

For transparency, the selected configuration's development metrics are:
accuracy `0.5833`, precision `0.5926`, recall `0.5333`, and F1 `0.5614`.
These development figures are not final metrics and are not used as a
selection tie-breaker.

## Result table and verification

The complete reproducible candidate table is
`data/week10_grid_search_results.csv`. It records rank, selection status,
weights, threshold, development metrics, validation metrics, and the number of
rows used from each allowed split. Row 1 is the selected configuration.

Unit tests for the runner cover normalized weight generation, inclusive
threshold generation, positive-class metric calculation, single-result
selection, held-out-row rejection, output CSV structure, and display output:

```powershell
.venv\Scripts\python.exe -m pytest tests/test_grid_search_ensemble.py -v -p no:cacheprovider
```

The focused grid-search test suite completed with **7 passing tests**. The calibration run
produced 594 candidate rows and selected exactly one configuration.

![Menishen Week 10 grid-search calibration evidence](assets/week10-progress/menishen-grid-search-calibration.svg)

*Figure 1. Menishen Week 10 ensemble grid-search calibration and selected
validation configuration. This evidence reports validation results only; the
held-out test split remains untouched.*

## Work deferred to other roles and later weeks

Arthur's Week 10 metric/selection verification and Exzavier's validation plots
remain separate contributions. Week 11 is the first scheduled held-out
evaluation; no held-out confusion matrix, ROC curve, AUC, or final project
accuracy has been produced here.
