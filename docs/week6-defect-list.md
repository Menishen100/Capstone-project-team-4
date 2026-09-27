# Week 6 Development-Set Defect List

## Scope

This list records issues observed while running the three detector prototypes
over the Week 5 **development** dataset only (60 clean and 60 matched stego
images). Validation and held-out-test data are intentionally excluded.

## Observed execution defects

| ID | Component | Issue | Severity | Status | Evidence / resolution |
| --- | --- | --- | --- | --- | --- |
| None | Development scoring run | No detector, image-loading, metadata, or pairing errors were observed in the 120-image development run. | N/A | Closed | `data/development_detector_scores.csv` contains 120 `complete` rows and the runner summary reports zero errors for Chi-square, RS, and DH. |

## Tracked limitation (not a defect)

| ID | Component | Limitation | Status | Planned work |
| --- | --- | --- | --- | --- |
| W6-L1 | Detector score interpretation | The three prototype scores are descriptive and use different statistical mappings; no shared calibration, threshold, or detector ranking was selected in Week 6. | Open by plan | Week 7 normalization and false-positive/false-negative review; then later validation-based ensemble calibration. |
