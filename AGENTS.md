# Multi-Feature Steganalysis Toolkit - Project Instructions

## Project identity

This repository contains a capstone project that implements a statistical image-steganalysis toolkit. The toolkit must classify images as **Clean** or **Suspicious** by combining three non-machine-learning detectors:

- Chi-square analysis of pair-of-values (PoV) histograms, including a p-value.
- RS analysis, including an RS steganalytic statistic.
- Difference Histogram (DH) analysis of adjacent-pixel differences and smoothness.

The system uses a weighted voting ensemble whose weights and decision threshold are calibrated empirically. It also includes a team-owned LSB embedding utility for generating the evaluation dataset.

## Required deliverables

- A CLI or GUI that reports `Clean` or `Suspicious`, a confidence score, and per-detector diagnostic scores.
- A documented dataset with at least 100 clean and 100 stego images.
- Reproducible experiments, including ROC curves, AUC, confusion matrices, and comparisons of individual detectors against the ensemble.
- Documentation, test materials, report assets, and presentation slides.

## Team responsibilities

| Role | Responsibilities |
| --- | --- |
| Team Leader | Ensemble design, weight calibration, integration, final CLI/GUI, project tracking, and meeting minutes. |
| Member A | Chi-square and RS-analysis detectors, supporting tests, and method documentation. |
| Member B | Difference-histogram detector, LSB dataset generation, ROC/AUC plots, and dataset metadata. |
| All members | Literature review, code review, dataset-quality checks, report, slides, and demo preparation. |

## Development rules

- Use Python, NumPy, Pillow, SciPy, and Matplotlib unless the team agrees on an additional dependency.
- Do not use machine learning or deep learning. All classification decisions must remain statistical and explainable.
- Give every detector a consistent interface: accept an image/path and return a numeric suspiciousness score in `[0, 1]` plus named diagnostics.
- Higher score values must always mean greater suspicion. Document every score normalization and thresholding choice.
- Prefer deterministic experiments: record dataset version, payload rate, random seed, package versions, and command line/configuration.
- Keep source in `src/`, tests in `tests/`, documentation in `docs/`, and slide assets in `slides/`.
- Use descriptive names, type hints where useful, concise docstrings, and comments that explain statistical decisions rather than obvious syntax.

## Dataset and evaluation safeguards

- Generate stego images with the team's own LSB tool and retain a mapping to the source clean image.
- Split data by original source image. A clean image and its derived stego image must never appear in different data splits.
- Use development data for implementation, validation data for ensemble calibration, and reserve the held-out test set for final reporting.
- Do not tune detector weights or thresholds on held-out test results.
- Include sample size, data split, payload condition, and detector name in every plot/table.
- Do not commit large raw datasets unless the team has agreed on storage; commit metadata, scripts, and instructions needed to recreate them.

## Testing and integration

- Add unit tests for each detector, including clean/stego fixtures and edge cases such as unsupported formats, very small images, and color-mode handling.
- Test the LSB embedder by confirming that an embedded payload can be measured and that output images remain readable.
- Run the full evaluation workflow before merging changes that affect detector scores, normalization, ensemble weights, or the dataset pipeline.
- Keep the CLI usable even if an optional GUI is not completed.

## Git and collaboration

- Work on a focused branch; do not commit directly to `main` unless coordinating a leader-owned integration change.
- Pull or sync `main` before starting work. Use clear commits and pull requests for review.
- Preserve other members' work. Resolve conflicts by inspecting both changes rather than discarding one.
- Only the team leader may edit `minutes.md`. Other contributors must not modify it.
- Update `README.md` when installation, usage, layout, or team responsibilities materially change.

## Important project references

- `docs/project-plan.md` is the approved working plan, timeline, schedule, and evaluation protocol.
- `minutes.md` is the official meeting record and leader-owned.
- When instructions conflict, prioritize the current assignment requirements and agreed team decisions over illustrative examples from class handouts.
