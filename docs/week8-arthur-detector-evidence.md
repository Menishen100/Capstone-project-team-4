# Week 8 Arthur Detector Evidence

## 1. Scope

This document packages midterm evidence for Arthur's two detectors: Chi-square
and RS Analysis. It records their current implementation, tests, and known
limits for the Week 8 midterm demo. It does not claim final detection accuracy.

## 2. Chi-square Detector

- **Purpose:** Look for signs of LSB replacement by comparing counts in
  neighboring pixel-value pairs: `(0, 1)`, `(2, 3)`, through `(254, 255)`.
- **Input:** `ChiSquareDetector.analyze(image)` accepts integer NumPy pixel data
  in the range 0–255. The shared preprocessing interface supplies grayscale
  `(height, width)` or RGB `(height, width, 3)` arrays. The detector pools all
  supplied samples into one histogram, including the RGB channels.
- **Output and score range:** A result has a floating-point `score` equal to
  the Chi-square p-value, in `[0, 1]`, and a `diagnostics` dictionary. In the
  current score convention, a higher p-value means greater suspicion of LSB
  replacement.
- **Diagnostics:** `chi_square` is the goodness-of-fit statistic;
  `p_value` is the probability value and matches `score`;
  `value_pairs_analyzed` counts populated adjacent value pairs; and
  `samples_analyzed` counts all values in the input array.
- **Common interface:** The detector exposes `analyze(image)` and returns the
  shared `score` plus detector-specific `diagnostics` result. Its tests verify
  the score and diagnostic types, ranges, and consistency.
- **Relevant tests:** `tests/test_chi_square.py` checks valid and balanced
  inputs, grayscale and RGB inputs, too-small and invalid pixel data,
  deterministic output, and that analysis does not modify its input.
- **Current limitations:** This is a prototype score, not a calibrated
  probability of steganography or a payload estimate. The score is the
  p-value itself. The implementation checks pixel count, integer type, and
  value range, but does not independently validate that the array has a
  grayscale or RGB shape; normal use relies on shared image preprocessing.
- **Week 7 observation:** In Arthur's development-only review, Chi-square had
  clean and stego means of `0.140474` and `0.188673`; both medians were
  `0.000000`. There were no candidate scores outside the opposite label's
  observed score range. These are descriptive observations, not accuracy
  results or evidence for a selected threshold.

## 3. RS Analysis Detector

- **Purpose:** Measure how local pixel differences change when each sample's
  least significant bit (LSB) is toggled.
- **Input:** `RSAnalysisDetector.analyze(image)` accepts integer grayscale
  `(height, width)` or RGB `(height, width, 3)` arrays with values from 0 to
  255. RGB channels are analyzed independently.
- **Output and score range:** The result contains a floating-point
  `rs_statistic` diagnostic and a score equal to its absolute value, clipped
  to `[0, 1]`. A higher score indicates greater suspicion under the current
  prototype convention.
- **Diagnostics:** The detector returns counts of regular, singular, and
  unchanged groups; the total complete groups analyzed; the RS statistic; the
  number of channels analyzed; and the number of samples in complete groups.
- **Group meaning:** Samples are split into non-overlapping groups of four.
  A **regular** group gets rougher after toggling all four LSBs. A **singular**
  group gets smoother. An **unchanged** group has the same roughness before
  and after toggling. Roughness is the sum of absolute differences between
  neighboring samples in the group. The statistic is `(regular - singular) /
  (regular + singular)`; unchanged groups are not in that denominator. If no
  groups are classifiable, the statistic is `0.0`.
- **Common interface:** The detector implements the shared `analyze(image)`
  interface and returns `{"score": float, "diagnostics": dict}`.
- **Relevant tests:** `tests/test_rs_analysis.py` checks grayscale and RGB
  inputs, repeatability, too-small input, invalid pixels and shapes,
  diagnostic consistency, score bounds, and input non-modification.
- **Current limitations:** As documented in `docs/rs-analysis.md`, the score
  has not been calibrated on the clean/stego dataset, uses a fixed group size
  of four and one all-sample LSB flip, and does not estimate payload rate.
  Image texture can affect the statistic. Trailing samples that do not fill a
  complete group are excluded.
- **Week 7 observation:** In Arthur's development-only review, RS had clean
  and stego means of `0.368833` and `0.290116`, and medians of `0.329166` and
  `0.252701`. Two clean and two stego files fell outside the opposite label's
  score range (`pair_033_clean.png`, `pair_039_clean.png`,
  `pair_008_stego.png`, and `pair_012_stego.png`). These range-overlap flags
  are not classification errors because no threshold was selected.

## 4. Common Output Contract

Both detectors return:

```python
{
    "score": float,
    "diagnostics": dict,
}
```

Both scores are bounded in `[0, 1]`. Diagnostics are specific to each
detector. The scores are prototype outputs and are not final calibrated
probabilities. The shared contract and score direction are described in
`docs/detector-output-convention.md` and `src/detectors/base_detector.py`.

## 5. Testing Evidence

The focused test files demonstrate:

- **Grayscale and RGB handling:** `test_grayscale_and_rgb_inputs_have_sane_diagnostics`
  in `tests/test_chi_square.py`; `test_analyzes_grayscale_image` and
  `test_analyzes_rgb_image` in `tests/test_rs_analysis.py`.
- **Invalid input handling:** `test_invalid_pixel_data_is_rejected` in both
  detector test files; RS also has `test_unsupported_shape_is_rejected`.
- **Deterministic behavior:** `test_result_is_deterministic_and_input_is_not_modified`
  for Chi-square and `test_score_is_repeatable_for_deterministic_input` for RS.
- **Score bounds and diagnostic consistency:** the valid-result, balanced-pair,
  and grayscale/RGB Chi-square tests; `assert_detector_result` and
  `test_group_diagnostics_are_consistent_and_input_is_not_modified` for RS.
- **Input protection:** Chi-square's deterministic/input-protection test and
  RS's diagnostic consistency/input-protection test compare the input after
  analysis.
- **Week 7 review safeguards:** `tests/test_arthur_week7_review.py` checks
  development-score summaries, rejects validation and held-out-test rows,
  requires both detector score columns, and rejects invalid scores.

Commands and observed results:

```text
.venv\Scripts\python.exe -m pytest tests/test_chi_square.py tests/test_rs_analysis.py tests/test_arthur_week7_review.py -v
26 passed in 7.20s

.venv\Scripts\python.exe -m pytest -v
123 passed in 18.50s
```

Both runs used the repository's virtual environment because system Python did
not have pytest installed. Pytest's temporary test data required the approved
Windows Temp access. The attached screenshot shows Arthur's focused rerun,
which completed with **26 passed in 1.22s**.

![Arthur Week 8 focused Chi-square and RS test output](assets/week8-arthur-focused-tests.png)

*Arthur Week 8 — PowerShell screenshot of the focused test command and passing
results.*

## 6. Midterm Readiness

Chi-square and RS are ready to be shown in the Week 8 midterm demo as working
prototype detectors. Their code, tests, shared result format, documentation,
and Arthur's development-only review provide evidence for a technical demo.
The Week 7 review used 120 completed development rows (60 clean and 60
matched LSB-stego rows) and did not use validation or held-out-test results.
Neither detector is ready to be presented as a final calibrated classifier;
the available evidence does not establish final detection accuracy or a
decision threshold.

## 7. Known Limitations

- Neither score has been calibrated as a probability or final classification
  score.
- Chi-square uses a p-value as the current suspiciousness score and pools all
  input values into one histogram.
- RS uses fixed groups of four, one LSB-flip pattern, and does not estimate
  payload rate; image texture affects its statistic.
- Week 7 observations are descriptive summaries of development data only.
  Candidate score-range flags are not final false-positive or false-negative
  classifications, and do not select thresholds.
