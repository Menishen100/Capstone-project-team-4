# Week 7 Preliminary Validation Summary

## 1. Development set used

This review used 120 completed rows from `data/development_detector_scores.csv`: 60 clean and 60 matched LSB-stego images in `split=development`. Validation and held-out-test rows were excluded.

## 2. Score normalization approach

All three current prototype outputs are already bounded in `[0, 1]`. For this descriptive Week 7 review, the team retained those native bounded values and recorded the raw direction observation instead of applying an arbitrary rescale or selecting a threshold. Any final direction transformation, threshold, or ensemble calibration remains deferred to the planned validation-based work in Weeks 9–10.

## 3. Detector observations

| Detector | Clean mean | Stego mean | Clean median | Stego median | Direction observation | Candidate FP | Candidate FN |
| --- | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| Chi-square | 0.140474 | 0.188673 | 0.000000 | 0.000000 | higher-stego-on-average | 0 | 0 |
| RS | 0.368833 | 0.290116 | 0.329166 | 0.252701 | lower-stego-on-average | 2 | 2 |
| Difference Histogram | 0.340618 | 0.309736 | 0.368276 | 0.326926 | lower-stego-on-average | 3 | 0 |

## 4. False-positive and false-negative candidates

Because no production threshold is selected in Week 7, these are threshold-free range-extreme candidates, not final classification errors. A candidate false positive is a clean score above every observed stego score for that detector; a candidate false negative is a stego score below every observed clean score.

### Chi-square

- Candidate false positives: None
- Candidate false negatives: None

### RS

- Candidate false positives: `source-033` / `pair_033_clean.png`, `source-039` / `pair_039_clean.png`
- Candidate false negatives: `source-008` / `pair_008_stego.png`, `source-012` / `pair_012_stego.png`

### Difference Histogram

- Candidate false positives: `source-006` / `pair_006_clean.png`, `source-032` / `pair_032_clean.png`, `source-057` / `pair_057_clean.png`
- Candidate false negatives: None

## 5. Preprocessing review and decision

The team reviewed the shared preprocessing path. It preserves native `L` and `RGB` images, converts unsupported Pillow modes to RGB, and does not resize, filter, normalize pixel values, or otherwise alter pixels before statistical analysis. The Week 6 rows completed without preprocessing failures, and the Week 7 review found no evidence supporting a pixel-changing adjustment. The team therefore retains the existing preprocessing behavior for the next stage.

## 6. Decisions carried forward

- Retain native grayscale/RGB handling and no-resize/no-filter preprocessing.
- Keep the native bounded scores for descriptive investigation only.
- Do not claim a detector ranking, select a production threshold, or tune an ensemble from this development-only review.
- Revisit score direction and normalization with the later validation-based calibration workflow, especially for RS and Difference Histogram because their stego means are lower in this development run.

## 7. Known limitations

This summary uses one controlled LSB dataset and development data only. Candidate cases are score-range flags, not final false-positive/false-negative rates. ROC/AUC, final thresholds, weighted voting, validation selection, and held-out-test evaluation remain out of scope for Week 7.
