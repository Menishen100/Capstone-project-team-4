# Week 9 Difference Histogram Ensemble Score Direction and Input Validation

## 1. Purpose

Prepare the existing bounded Difference Histogram (DH) score for later ensemble
input by making higher normalized values mean greater suspicion. This is score-
direction alignment, not final calibration.

This contribution also adds a development-score input validator to confirm that
the detector-score table is strcturally and numerically valid before later
ensemble integration.

## 2. Existing DH score meaning

`DifferenceHistogramDetector.analyze` produces a bounded DH suspiciousness score
in `[0, 1]`

The current DH detector first measures histogram roughness from adjacent-pixel
differences and then converts the raw roughness value using:

`raw_roughness / (1 + raw_roughness)`

This produces a bounded score, but the score is not a calibrated probability of
steganography and no final classification threshold is assigned here.

## 3. Week 7 observed direction

The Week 7 development-only review reported a mean DH score of `0.340618` for
clean images and `0.309736` for stego images.

The paired review also found that 59 of 60 images had a lower DH score than their
corresponding clean image. Only one pair had a slightly high stego score, with a
difference of approx `0.000026`.

This lower-stego-on-average development behavior supports reversing the DH score
direction for ensemble compatibility. These observations are descriptive development
results only and do no establish final accuracy or calibration.

## 4. Ensemble compatibility rule

Detector scores prepared for later ensemble use should remain in `[0, 1]`, and
higher normalized values should mean greater suspicion.

Input to the normalization functions must be a valid finite numeric scalar in `[0, 1]`.
Invalid, NaN, infinite, negative, and above-one values are rejected.

The original DH detector is not motified. Direction alignment is performed only when
preparing its score for later ensemble use.

## 5. DH transformation

`normalize_dh(score)` returns: `1 - score`

This simple inversion aligns the lower-stego-on-average DH development direction with 
the shared ensemble suspiciousness convention.

Examples:

| Original DH Score | Normalized DH Score |
| ---: | ---: |
| 0.00 | 1.00 |
| 0.25 | 0.75 |
| 0.50 | 0.50 |
| 1.00 | 0.00 |

The transformation reverses direction while preserving the existing bounded scale. It
is a direction-alignment transformation, not final calibration.

## 6. Ensemble Validation Input

`src/ensemble/check_ensemble_inputs.py` validates detector-score data before it is
passed into later ensemble work.

The required columns are:

- `source_id`
- `label`
- `split`
- `chi_square_score`
- `rs_score`
- `dh_score`
- `status`

For Week 9, only rows where `split == "development"` are checked. Validation and
held-out rows may exist in the score table, but they are excluded from this
development-only check

Each development row must have:

- A non-empty `source_id`,
- `status` equal to `complete`,
- A valid `clean` or `stego` label,
- A Chi-square score,
- An RS score,
- A DH score.

Each detector score must be numeric, finite, and within `[0, 1]`

The validator also confirms that both clean and stego development rows are present 
before returning a successful summary.

The validator does not normalize scores, combine detector outputs, classify images,
or calculate an ensemble result.

## 7. Validation Output

When the development score table passes validation, `validate_ensemble_inputs()`
returns a summary containing:

- Number of development rows checked,
- Number of clean rows,
- Number of stego rows,
- Invalid row count,
- Required-column validation status.

`format_validation()` converts this summary into readable terminal output, and `main()`
provides command-line execution using `data/development_detector_scores.csv` as the
default score-table path.

Invalid input produces a validation failure instead of silently continuing into later
ensemble processing.

## 8. Tests

`tests/test_ensemble_normalization.py` includes DH normalization coverage for bounded
values, direction inversion, deterministic behavior, and invalid negative, above-one, NaN, infinite, boolean, and nonnumeric inputs.

![Week 9 Focused Normalization Test Output](assets/week9-progress/week9-score-direction.png)

`tests/test_ensemble_input_validation.py` covers:

- Valid development rows being accepted,
- Missing required detector columns being rejected,
- Missing detector scores being rejected,
- Out-of-range scores being rejected,
- Nonnumeric scores being rejected,
- NaN and infinite scores being rejected,
- Incomplete status being rejected,
- Invalid labels being rejected,
- Missing clean development rows being rejected,
- Missing stego development rows being rejected,
- Absence of development rows being rejected,
- Validation rows being excluded,
- Held-out rows being excluded.

![Week 9 Ensemble Input Validation Test Output](assets/week9-progress/week9_ensemble_inputs_testing.png)

## 9. Limitations

No final DH calibration is performed, no final classification threshold is selected,
and no ensemble weights are selected

The DH direction decision is based on development-only observations and does not
represent final accuarcy.

The ensemble-input validator checks data quality only. It does not perform score
combination, weighted voting, ROC/AUC evalution, or final classification.

Validation and held-out data are not analyzrf as part of this Week 9 baseline check,
and held-out test data remains unchanged

## 10. Work deferred to Week 10

Final team-owned ensemble integration, validation-based calibration, threshold selection,
weighting, and later performance evaluation remain for the planned workflow.

The Week 9 contribution prepares DH for ensemble compatibility and verifies that the development detector-score table is safe to use before those later ensemble steps.