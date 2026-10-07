# Week 8 Midterm Evidence Package

## Project overview

The Multi-Feature Steganalysis Toolkit is an explainable, statistical image
steganalysis project. It investigates whether a PNG image is clean or has
potentially been altered with least-significant-bit (LSB) embedding. The
project uses three non-machine-learning prototype detectors:

- Chi-square pair-of-values analysis;
- RS (regular/singular) analysis; and
- Difference Histogram (DH) analysis.

Each detector follows the same `analyze(image)` contract and returns a
bounded numeric `score` plus named, detector-specific `diagnostics`. A final
weighted-voting classifier, threshold calibration, ROC/AUC evaluation, and
held-out-test results are deliberately later milestones; this is a Week 8
midterm package, not a final-performance report.

## Current architecture

```text
PNG image
  -> shared preprocessing (`src.preprocessing.load_image`)
  -> L or RGB NumPy array, without pixel-changing transformations
  -> Chi-square / RS / DH prototype detectors
  -> bounded score in [0, 1] + named diagnostics
```

The preliminary scoring runner at
`src/evaluation/run_preliminary_scores.py` applies all three detectors to the
development split and writes one reproducible score row per image. The
development-review scripts summarize those results without choosing a
classifier threshold or ensemble weights.

## Dataset description and reproducibility

The controlled evaluation dataset contains 100 legally tracked, lossless PNG
clean images and 100 matching LSB-stego images. Each metadata row in
`data/metadata.csv` represents one clean/stego pair, preserving the required
source mapping and keeping the pair in one split.

| Split | Clean images | Stego images | Pairs |
| --- | ---: | ---: | ---: |
| Development | 60 | 60 | 60 |
| Validation | 20 | 20 | 20 |
| Held-out test | 20 | 20 | 20 |
| **Total** | **100** | **100** | **100** |

Metadata records `source_id`, the two filenames, payload rate, random seed,
color mode, dimensions, split, PNG format, source/license note, and embedding
details. The current pairs use a payload rate of `0.25`; there are 50 RGB and
50 grayscale (`L`) pairs. The LSB utility uses deterministic seeds, so the
same clean inputs, configuration, and master seed reproduce the recorded
generation settings and stego output.

The reproducible paired-dataset workflow and integrity safeguards are
documented in [the dataset protocol](dataset-protocol.md). It requires one
stego counterpart per clean source and rejects missing metadata, duplicate
identifiers, invalid pair mappings, and incorrect split totals.

## Detector evidence

| Detector | What it measures | Current score and diagnostic evidence |
| --- | --- | --- |
| Chi-square | Balance in neighboring pixel-value pairs associated with LSB replacement | Score is the Chi-square p-value; diagnostics include `chi_square`, `p_value`, `value_pairs_analyzed`, and `samples_analyzed`. |
| RS | Change in local roughness after toggling LSBs in groups of four samples | Score is the absolute, bounded RS statistic; diagnostics include regular, singular, unchanged, and total group counts. |
| Difference Histogram | Roughness of horizontal/vertical adjacent-pixel-difference histograms | Score is a bounded mapping of raw DH roughness; diagnostics include raw roughness, central-region statistics, zero-difference values, and per-channel data. |

Arthur's detailed Chi-square and RS implementation, test, diagnostic, and
limitation evidence is in
[Week 8 Arthur detector evidence](week8-arthur-detector-evidence.md).
Exzavier's detailed DH, LSB embedder, dataset, pairing, and test evidence is
in [Week 8 DH, LSB, and dataset evidence](week8-dataset-dh-evidence.md).
The shared interface is specified in
[the detector output convention](detector-output-convention.md).

## Preprocessing decision

All detector inputs use the shared preprocessing rule set:

- preserve native grayscale (`L`) and RGB (`RGB`) images;
- convert any other Pillow mode to RGB;
- do not resize, filter, normalize, or otherwise alter pixel values before
  analysis.

This decision, retained after the Week 7 review, keeps the three prototype
detectors comparable without introducing hidden pixel changes. See
[preprocessing rules](preprocessing.md) and the
[Week 7 preliminary summary](week7-preliminary-validation-summary.md).

## Testing status

The repository includes focused unit and integration tests for the detector
contract, grayscale/RGB handling, bounded scores, diagnostics, invalid input,
input non-modification, LSB generation, dataset pairing, split isolation, and
development-only scoring/review safeguards.

Key focused commands are:

```powershell
.venv\Scripts\python.exe -m pytest tests/test_chi_square.py tests/test_rs_analysis.py tests/test_arthur_week7_review.py -v
.venv\Scripts\python.exe -m pytest tests/test_difference_histogram.py tests/test_lsb_embedder.py tests/test_review_dh.py -v
.venv\Scripts\python.exe -m pytest -v
```

Arthur's Week 8 evidence records 26 passing focused Chi-square/RS tests and a
123-passing full-suite run at packaging time. Exzavier's Week 8 evidence
documents focused DH, LSB, and development-review coverage. The demo checklist
uses the full suite as the final integration check, which should be rerun in
the current environment before the demonstration.

Menishen's integrated rerun completed with **123 passed in 16.66 seconds** on
October 7, 2026. The terminal-style evidence asset records the command and
result without claiming that the test count is a final project metric.

![Menishen Week 8 integrated full-suite evidence](assets/week8-progress/menishen-full-suite-evidence.svg)

*Menishen Week 8 — integrated automated-test evidence for the midterm package.*

## Development-set preliminary results

The preliminary runner completed 120 development rows: 60 clean and 60
matched stego images, with no Chi-square, RS, or DH execution errors. It did
not read validation or held-out-test rows. The descriptive means below are
evidence of current prototype behavior, not accuracy claims or selected
classification thresholds.

| Detector | Clean mean | Stego mean | Week 7 direction observation |
| --- | ---: | ---: | --- |
| Chi-square | 0.140474 | 0.188673 | higher-stego-on-average |
| RS | 0.368833 | 0.290116 | lower-stego-on-average |
| Difference Histogram | 0.340618 | 0.309736 | lower-stego-on-average |

The complete score table is
[Week 6 development-set score summary](week6-development-score-summary.md).
The Week 7 descriptive review identified no range-extreme candidate cases for
Chi-square, two candidate false-positive and two candidate false-negative
cases for RS, and three candidate false-positive cases for DH. These are
threshold-free review flags, not final classification errors. Their filenames
and the review method are recorded in the
[Week 7 preliminary validation summary](week7-preliminary-validation-summary.md).

## Known limitations

- The current scores are prototype statistical outputs, not calibrated
  probabilities of steganography.
- The development observations use one controlled LSB payload condition
  (`0.25`) and cannot establish performance across other payload rates.
- RS and DH had lower average stego scores in the development-only review;
  their score direction needs empirical review before any ensemble decision.
- No final detector threshold, score transformation, weighted ensemble,
  ROC/AUC analysis, or final error rate has been selected.
- Validation and held-out-test data have not been used for calibration or
  final reporting.

## Current status and next steps

The Week 8 milestone is met as an evidence package: the repository has a
documented paired dataset, three working prototype detectors with a common
interface and diagnostics, automated tests, development-set score evidence,
and a repeatable demo sequence. The next planned work begins in Week 9:
implement the weighted-voting ensemble and a reproducible baseline
configuration. Calibration must use the approved development/validation
workflow and keep the held-out test split reserved for final evaluation.
