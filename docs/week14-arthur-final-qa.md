# Arthur — Week 14 Final QA

## Audit target

Fetched `origin/main` at `03ec6cb`, including the merged Week 13 CLI, GUI, and
documentation work. This is the latest integrated release candidate available
in the repository during this audit. No Week 14 branches were present.

## Tests and commands run

- Fresh virtual environment: `pip install -r requirements.txt` — completed.
- Full repository suite before GUI callback coverage: **277 passed**.
- `python -m pytest -q -p no:cacheprovider` after the GUI callback additions:
  **281 passed**.
- `python -m pytest -v`: **281 passed**.
- `python -m src.cli --help` — passed.
- `python -m src.cli dataset/clean/pair_081_clean.png` — Clean, ensemble
  score `0.3876`.
- `python -m src.cli dataset/stego/pair_083_stego.png` — Suspicious, ensemble
  score `0.8065`.
- `python src/cli.py dataset/clean/pair_081_clean.png` — passed.
- Dataset-generation and clean-inventory help commands — passed. Running
  `python -m src.evaluation.validate_dataset dataset/clean
  data/clean_metadata.csv --expected-count 100` found 100 valid PNG sources,
  with no validation issues.
- `python -m src.gui` — launched the GUI window and opened the Select Image
  picker. Callback-level tests verify selection, analysis display, warnings,
  and error handling. A full manual file-selection and Analyze walkthrough
  remains open.
- Scanned local Markdown links in `README.md`, `docs/`, and `minutes/` — no
  missing local targets found.

## Detector and release regression checks

- Locked values remain Chi-square `0.00`, RS `0.70`, DH `0.30`, threshold
  `0.70`.
- The CLI clean and suspicious examples match the corresponding official
  Week 11 prediction rows and expected labels.
- The official Week 11 metrics artifact remains accuracy `0.625`, precision
  `0.6923`, recall `0.45`, F1 `0.5455`; confusion counts are TP `9`, TN `16`,
  FP `4`, FN `11`.
- No held-out evaluation or recalibration was run as part of this QA.
- Existing tests cover the detectors, preprocessing, normalization, ensemble,
  and CLI. Four callback-level GUI tests were added for image selection,
  displayed scores, the no-selection warning, and analysis-error handling.

## Findings

- **Documentation issue for Exzavier:** the README's final paragraph still
  describes optional GUI support as future work, although `src/gui.py` is now
  included and documented earlier in the README. Update that sentence before
  release.
- No detector, normalization, ensemble, threshold, grayscale, or RGB behavior
  changes were needed or made.
- A full manual GUI analysis walkthrough remains unverified; automated callback
  tests cover the GUI logic without opening a window.

## Final QA result

The fetched Week 13 `main` passes the automated release suite and CLI examples.
The repository is **not yet ready for the final tag**: the README finding and
manual GUI walkthrough remain open, Week 14 member contributions are not
merged, and the team has not completed its final review. See the [release
checklist](week14-final-release-checklist.md).
