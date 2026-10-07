# Week 8 Midterm Demo Checklist

## Purpose and scope

This checklist demonstrates the Week 8 midterm state of the repository: a
traceable paired dataset, three working statistical prototype detectors, named
diagnostics, and automated tests. It does **not** present a final classifier,
final decision threshold, ROC/AUC results, weighted ensemble, or held-out-test
performance.

Run commands from the repository root with the project virtual environment.

```powershell
Set-Location "C:\Users\afriy\OneDrive\Documents\ChatGPT\CapstoneProject"
```

## Before the demo

- [ ] Confirm the checked-out commit is the intended reviewed commit.
- [ ] Confirm dependencies are installed in `.venv`.
- [ ] Keep `data/metadata.csv`, `data/development_detector_scores.csv`, and
  the `dataset/clean` and `dataset/stego` directories unchanged during the
  demonstration.
- [ ] State that the current work is a prototype evidence package and that
  no calibration is performed on held-out test data.

## Demonstration sequence

### 1. Show repository organization

- [ ] Show `src/detectors/` for the three detector modules.
- [ ] Show `src/lsb_embedder.py` and `src/evaluation/` for reproducible data
  generation and development scoring.
- [ ] Show `docs/week8-midterm-report.md` and the two member evidence
  documents.

### 2. Show the paired dataset and metadata

Run:

```powershell
(Get-ChildItem dataset\clean -Filter *.png -File).Count
(Get-ChildItem dataset\stego -Filter *.png -File).Count
Import-Csv data\metadata.csv | Group-Object split | Select-Object Name, Count
Import-Csv data\metadata.csv | Select-Object -First 1 source_id, clean_filename, stego_filename, payload_rate, random_seed, color_mode, width, height, split
```

- [ ] Confirm 100 clean PNGs and 100 stego PNGs.
- [ ] Confirm 60 development, 20 validation, and 20 held-out-test pair rows.
- [ ] Point out that one metadata row keeps each clean/stego pair in the same
  split and records reproducibility fields.

### 3. Show shared preprocessing and all three detector outputs

Run this read-only sample analysis using a development clean image:

```powershell
@'
from pathlib import Path
from src.detectors import ChiSquareDetector, DifferenceHistogramDetector, RSAnalysisDetector
from src.preprocessing import load_image

sample = Path("dataset/clean/pair_001_clean.png")
image = load_image(sample)
print(f"Sample: {sample}")
print(f"Array shape: {image.shape}; dtype: {image.dtype}")
for name, detector in (
    ("Chi-square", ChiSquareDetector()),
    ("RS", RSAnalysisDetector()),
    ("Difference Histogram", DifferenceHistogramDetector()),
):
    result = detector.analyze(image)
    print(f"{name}: score={result['score']:.6f}")
    print(f"  diagnostics={result['diagnostics']}")
'@ | .venv\Scripts\python.exe
```

- [ ] Point out that every detector produces `score` plus `diagnostics`.
- [ ] Explain that scores are bounded in `[0, 1]`, but are not final
  calibrated classification probabilities.
- [ ] Note that preprocessing preserves `L`/`RGB` pixels and applies no
  resize, filtering, or pixel normalization.

### 4. Show development-set evidence

- [ ] Open `docs/week6-development-score-summary.md`.
- [ ] Open `docs/week7-preliminary-validation-summary.md`.
- [ ] State that the preliminary run contains 120 completed development rows:
  60 clean and 60 matched stego images.
- [ ] State that validation and held-out-test data were excluded from this
  descriptive review.
- [ ] State that Week 7 candidate cases are range-overlap review flags rather
  than final false-positive or false-negative classifications.

### 5. Show member implementation evidence

- [ ] Open `docs/week8-arthur-detector-evidence.md` for Chi-square and RS
  purpose, diagnostics, tests, observations, and limitations.
- [ ] Open `docs/week8-dataset-dh-evidence.md` for DH, LSB embedder, dataset
  counts, pairing/split, reproducibility, tests, and limitations.
- [ ] Refer to their attached passing-test screenshots when presenting the
  focused component evidence.

### 6. Run automated verification

Run the full suite at the end of the demo:

```powershell
.venv\Scripts\python.exe -m pytest -v -p no:cacheprovider
```

- [ ] Confirm the test run completes without failures.
- [ ] If the number of tests differs from an earlier screenshot, report the
  current output rather than editing or recreating historical evidence.

## Closing statement

The project currently demonstrates a reproducible paired image dataset and
three independently tested statistical steganalysis prototypes with a common
score-and-diagnostics interface. The next milestone is a weighted-voting
baseline; score calibration and threshold selection must remain separate from
the held-out test split.
