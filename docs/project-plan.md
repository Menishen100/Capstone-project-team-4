# Project Plan: Multi-Feature Steganalysis Toolkit

## 1. Project summary

The team will build a Python steganalysis toolkit that classifies images as **Clean** or **Suspicious** without using machine learning. It will combine three statistical detectors:

1. Chi-square analysis of pair-of-values (PoV) histograms, returning a p-value and suspiciousness score.
2. RS analysis, returning an RS steganalytic statistic and suspiciousness score.
3. Difference Histogram (DH) analysis, measuring adjacent-pixel difference distributions and smoothness.

The toolkit will include an in-house LSB embedding utility to create an evaluation dataset of at least 100 clean and 100 matched stego images. A weighted voting ensemble will be calibrated on a development subset and evaluated on a held-out test subset using ROC curves, AUC, confusion matrices, and accuracy metrics.

## 2. Objectives and success criteria

| Objective | Success criterion |
| --- | --- |
| Implement three independent detectors | Each detector accepts a supported image and returns a numeric suspiciousness score in `[0, 1]` plus diagnostic values. |
| Build a reproducible dataset | At least 100 clean images and 100 corresponding LSB-stego images, with metadata documenting source, payload rate, and split. |
| Fuse detector results | A weighted voting classifier produces a label and calibrated confidence score. |
| Validate detector performance | ROC/AUC plots and confusion matrices compare each detector with the ensemble on a held-out test set. |
| Deliver a usable application | A CLI or GUI analyzes an image and reports `Clean` or `Suspicious`, confidence, and per-detector results. |
| Maintain team documentation | README, meeting minutes, setup instructions, experiment records, report, slides, and tests are stored in the repository. |

## 3. Scope and constraints

### In scope

- Raster image analysis using Python, NumPy, Pillow, SciPy, and Matplotlib.
- LSB replacement embedding for controlled stego-image generation.
- Grayscale and RGB image support, with analyses performed per channel or on a documented grayscale conversion.
- Statistical calibration and evaluation; no learned model.
- CLI as the minimum interface; GUI only if time permits after evaluation is complete.

### Out of scope

- Machine-learning or deep-learning detectors.
- Claims of universal detection of every steganography method.
- Analysis of encrypted, compressed, video, audio, or non-image payloads.

## 4. Team responsibilities

| Role | Primary responsibilities | Integration deliverables |
| --- | --- | --- |
| Afriyie | Ensemble design, grid-search calibration, integration, project tracking, meeting minutes, final packaging | Voting module, reproducible experiment runner, final CLI/GUI, release checklist |
| Arthur | Chi-square and RS detectors, unit tests, score normalization documentation | `chi_square.py`, `rs_analysis.py`, detector tests, method notes |
| Exzavier | Difference Histogram detector, LSB dataset generator, ROC/AUC visualizations | `difference_histogram.py`, `lsb_embed.py`, dataset metadata, evaluation plots |
| All members | Literature review, code review, data-quality checks, report/slides/demo preparation | Reviewed pull requests, report contributions, rehearsal feedback |


## 5. Technical design

```text
Input image
   |
   +--> Chi-square detector --------> normalized score
   +--> RS analysis detector -------> normalized score
   +--> Difference Histogram ------> normalized score
                                      |
                                      v
                          weighted ensemble / threshold
                                      |
                                      v
                   Clean or Suspicious + confidence + diagnostics
```

Suggested source layout:

```text
src/
  detectors/       # chi-square, RS, and DH implementations
  stego/           # LSB embedder and payload helpers
  ensemble/        # score normalization, weighting, thresholding
  evaluation/      # dataset loading, metrics, plots, experiment runner
  cli.py           # user-facing command-line interface
tests/             # unit and integration tests
docs/              # theory, plan, methods, and results
slides/            # presentation assets
data/              # metadata only; large images may be linked externally
```

## 6. Dataset and experiment protocol

1. Collect or create 100 legally usable clean lossless images (prefer PNG/BMP; do not use JPEG as a source for pixel-level matching without documenting the effect).
2. Generate one or more LSB-stego counterparts for every clean image using the team-owned LSB tool. Record payload rate, color mode, dimensions, random seed, and source-image identifier.
3. Partition images by source image - never place a clean image in one split and its stego counterpart in another:
   - Development/calibration: 60 clean + 60 stego images.
   - Validation: 20 clean + 20 stego images.
   - Held-out test: 20 clean + 20 stego images.
4. Design score direction consistently: higher scores must mean more suspicious.
5. Use the development subset for initial weights, validation for choosing weights and decision threshold, and the held-out test set only once for final metrics.
6. Record environment versions, random seeds, command lines, and results so another team can reproduce the evaluation.

## 7. Timeline and schedule

| Week | Planned work | Owner(s) | Milestone / evidence |
| --- | --- | --- | --- |
| W2 | Confirm project scope; create repository; assign roles; review Chi-square, RS, and DH theory; approve this plan. | All; leader coordinates | Approved plan, repository, initial minutes |
| W3 | Define common detector interface and image preprocessing rules; implement Chi-square prototype. | Leader, Member A | Detector API and Chi-square test case |
| W4 | Implement RS and DH prototypes; review code and align all outputs to score convention. | Member A, Member B | Three standalone modules run on sample images |
| W5 | Implement LSB embedder; gather clean images; generate paired stego images and metadata. | Member B; all validate | 100 clean + 100 stego dataset target reached |
| W6 | Add unit tests and per-detector diagnostic output; run preliminary scores across development set. | All | Detector score table and defect list |
| W7 | Normalize scores; inspect false positives/negatives; refine preprocessing and document decisions. | All | Preliminary validation summary |
| W8 | Package midterm evidence: dataset description and three working detectors. | Leader; all contribute | Midterm report/demo |
| W9 | Implement weighted-voting ensemble and baseline equal-weight model. | Leader | Ensemble module with reproducible config |
| W10 | Run grid search for weights and threshold using development/validation sets. | Leader; Member B supports plots | Selected weights, threshold, validation results |
| W11 | Run held-out evaluation; calculate accuracy, precision, recall, F1, ROC, AUC, and confusion matrices. | All | Metrics tables and plots |
| W12 | Investigate error cases and robustness across payload rates; add regression tests. | All | Error analysis and expanded tests |
| W13 | Polish CLI; optionally add GUI only if core evaluation is finished; prepare user documentation. | Leader; all review | Usable release candidate |
| W14 | Draft final report with methodology, dataset, calibration, results, limitations, and reproducibility steps. | All | Complete report draft |
| W15 | Create slides; rehearse live demo; resolve final issues. | All | Presentation-ready slides and demo script |
| W16 | Deliver final presentation and submit repository, report, dataset documentation, and slides. | All | Final submission |

## 8. Recurring team schedule

| Activity | Frequency | Participants | Expected output |
| --- | --- | --- | --- |
| Stand-up | Weekly, 15 minutes | All | Blockers, next tasks, updates sent to leader |
| Technical working session | Weekly, 60-90 minutes | Relevant implementers | Demonstrable code or experiment result |
| Code review | For every pull request | At least one teammate | Review approval and tested merge |
| Leader minutes update | After each team meeting | Team Leader only | Updated `minutes.md` |
| Milestone review | End of each listed week | All | Acceptance decision and revised task assignments |

## 9. Quality and acceptance checklist

- [ ] Each detector has documented inputs, outputs, assumptions, and tests.
- [ ] Dataset metadata maps every stego image to its clean source and embedding settings.
- [ ] Calibration data and held-out evaluation data are not mixed.
- [ ] All plots label split, sample size, detector, and payload conditions.
- [ ] The CLI/GUI reports label, confidence, and individual detector scores.
- [ ] README includes installation, usage examples, and project-member descriptions.
- [ ] The leader has kept meeting time, attendees, tasks, and decisions current in `minutes.md`.
- [ ] The final report states limitations and avoids unsupported detection claims.

## 10. Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Small or biased image dataset | Use diverse source images, paired splits, and document selection criteria. |
| Detector scores on incompatible scales | Normalize scores before ensemble calibration and store the transformation. |
| Leakage from paired images across splits | Split by original source image before generating or assigning counterparts. |
| Overfitting weights to the test data | Reserve held-out images until final evaluation. |
| Team integration conflicts | Use small focused branches, pull requests, code review, and one shared detector interface. |
| Limited time for GUI | Treat CLI and evaluation report as required; GUI is a post-core enhancement. |
