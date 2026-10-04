# Week 7 — Difference Histogram Normalization and Error Analysis

## Purpose

This Week 7 review analyzed Difference Histogram (DH) development-set results
from `data/development_detector_scores.csv`.

The review examined normalization, clean/stego score behavior, candidate error
cases, DH diagnostics, RGB/grayscale behavior, and preprocessing consistency.

Only development data was used. No final threshold, ROC/AUC evaluation,
ensemble weighting, or final performance claim was produced.

## Development Data

The review included 60 clean and 60 paired stego images:

- 50 RGB pairs
- 10 grayscale pairs

Clean and stego images were matched using `source_id`.

## Normalization

The current transformation is:

`score = raw_roughness / (1.0 + raw_roughness)`

Results:

- All scores were within [0.0, 1.0].
- Normalization mismatches: 0.

The normalization formula was applied consistently.

## Clean vs. Stego Scores

| Measurement | Clean | Stego |
|---|---:|---:|
| Mean score | 0.340618 | 0.309736 |
| Median score | 0.368276 | 0.326926 |
| Minimum score | 0.079907 | 0.079933 |
| Maximum score | 0.599817 | 0.542192 |
| Mean raw roughness | 0.582664 | 0.491702 |

Of the 60 pairs:

- 59 stego images had lower scores.
- 1 stego image had a higher score.
- 0 pairs were equal.

The only stego-higher case was `source-012`:

- Clean: 0.079907
- Stego: 0.079933
- Change: +0.000026

This was effectively a near-tie.

The development results do not support the current provisional assumption
that higher DH scores always indicate greater steganographic suspicion.

## Candidate Error Cases

Candidate cases use opposite-class score-range extremes and are not final
classification errors because no final threshold exists.

### Candidate False Positives

Three clean images scored higher than every stego image:

| File | Mode | Score | Raw Roughness | Zero-Difference Fraction | Variation |
|---|---|---:|---:|---:|---:|
| `pair_006_clean.png` | RGB | 0.599817 | 1.498857 | 0.738429 | 192806.000 |
| `pair_032_clean.png` | RGB | 0.590590 | 1.442542 | 0.705520 | 184472.333 |
| `pair_057_clean.png` | L | 0.549923 | 1.221841 | 0.598698 | 156337.000 |

These cases had unusually high zero-difference fractions and histogram
variation.

### Candidate False Negatives

No candidate false negatives were found.

Candidate false-negative count: `0`

## Diagnostic Findings

| Diagnostic | Clean | Stego |
|---|---:|---:|
| Mean zero-difference fraction | 0.284844 | 0.240478 |
| Mean variation | 74291.655556 | 62695.977778 |
| Mean central total | 127246.200000 | 127243.661111 |

Stego images showed lower zero-difference fractions and histogram variation,
while central totals stayed nearly unchanged.

This is consistent with randomized LSB changes moving some adjacent-pixel
differences away from zero.

## RGB and Grayscale Review

| Image Mode | Clean Mean Score | Stego Mean Score |
|---|---:|---:|
| RGB | 0.340734 | 0.309075 |
| Grayscale | 0.340036 | 0.313040 |

These values are descriptive only. No mode-specific threshold was selected.

## Preprocessing Review

For each 256 × 256 channel, the expected number of horizontal and vertical
adjacent-pixel differences is:

`130560`

Results:

- All histogram totals matched 130560.
- Histogram total mismatches: 0.
- Grayscale used `L`.
- RGB used `R`, `G`, and `B`.

No preprocessing change was justified by the development results.

## Changes Made

Week 7 added DH development analysis for:

- normalization verification,
- clean/stego statistics,
- paired score direction,
- candidate FP/FN cases,
- diagnostic values,
- RGB/grayscale comparison,
- preprocessing consistency.

No Chi-square or RS code was changed.

## Testing

Run:

`python -m pytest tests/test_review_dh.py -v --basetemp=.pytest_tmp`

Updated result:

`7 passed`

The tests cover normalization, development filtering, score statistics,
candidate cases, RGB/grayscale summaries, diagnostics, source pairing,
histogram consistency, formatting, and command-line execution.

## Limitations

This analysis uses development data only.

Candidate FP/FN cases are range-extreme cases rather than final
classification errors.

No validation data, held-out test data, final threshold, or final ROC/AUC
evaluation was used.

## Conclusion and Recommendation

The DH normalization formula worked correctly, but 59 of 60 stego images
received lower scores than their paired clean images.

The diagnostics suggest that LSB embedding generally reduced the
zero-difference fraction and histogram variation. Three clean images also
produced unusually high DH scores.

The DH statistic appears internally consistent, but its suspiciousness
direction should be reviewed during later calibration.

No detector-direction change should be made from Week 7 development analysis
alone.
