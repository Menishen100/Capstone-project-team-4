# Week 9 Chi-square and RS Ensemble Score Direction

## 1. Purpose

Prepare the existing bounded Chi-square and RS scores for later ensemble input
by making higher normalized values mean greater suspicion. This is score-
direction alignment, not final calibration.

## 2. Existing Chi-square score meaning

`ChiSquareDetector.analyze` returns the pair-of-values chi-square p-value as
`score`. The value is already bounded in `[0, 1]`. No threshold or probability
interpretation is assigned here.

## 3. Existing RS score meaning

`RSAnalysisDetector.analyze` returns the clipped absolute value of its
regular/singular statistic, also bounded in `[0, 1]`. This magnitude score
does not retain the sign of the underlying statistic.

## 4. Week 7 observed direction

The Week 7 development-only review reports Chi-square means of 0.140474 for
clean and 0.188673 for stego, with both medians at 0. The observed direction is
higher-stego-on-average, which supports keeping its existing score direction
for this design. The means do not establish final accuracy or calibration.

RS means were 0.368833 for clean and 0.290116 for stego, and medians were
0.329166 and 0.252701 respectively. This lower-stego-on-average observation
supports flipping the RS score direction for compatibility. These are
descriptive development results only, not accuracy estimates.

## 5. Ensemble compatibility rule

Both normalized functions return values in `[0, 1]`, and higher normalized
values mean more suspicious. Input must be a finite real numeric scalar in
`[0, 1]`; invalid, NaN, and infinite values are rejected.

## 6. Chi-square transformation

`normalize_chi_square(score)` returns `score` unchanged. The existing bounded
score is retained without arbitrary rescaling.

## 7. RS transformation

`normalize_rs(score)` returns `1 - score`. This simple inversion aligns the
lower-stego-on-average development direction with the shared suspiciousness
convention. It is a direction-alignment transformation, not final calibration.

## 8. Tests

`tests/test_ensemble_normalization.py` covers endpoints, middle values,
determinism, range, direction, and invalid negative, above-one, NaN, infinite,
boolean, and nonnumeric inputs for Arthur's functions.

![Arthur Week 9 focused Chi-square, RS, and normalization test output](assets/week9-progress/arthur-normalization-tests.png)

## 9. Limitations

No final calibration is performed, no final threshold is selected, no optimal
weights are selected, and no held-out data is used. The Week 7 development
means and medians are descriptive observations, not final accuracy. No voting
ensemble is implemented here.

## 10. Work deferred to Week 10

Final team-owned validation-based calibration, thresholds, and ensemble
integration remain for the later planned workflow. Difference Histogram
normalization and ensemble voting are outside this contribution.
