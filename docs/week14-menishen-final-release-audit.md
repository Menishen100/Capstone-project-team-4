# Menishen Week 14 - Final Release Audit and Packaging

## Scope

This final integration audit was performed after Arthur's final QA and
Exzavier's documentation/reproducibility work were merged into `main`. It
reviews the repository as a release candidate without changing detector
algorithms, normalization, weights, threshold, or official evaluation outputs.

## Fresh-environment verification

A new temporary virtual environment was created, then the declared
requirements were installed:

```powershell
python -m venv <temporary-release-environment>
<temporary-release-environment>\Scripts\python.exe -m pip install --no-compile -r requirements.txt
<temporary-release-environment>\Scripts\python.exe -m pip check
```

Installation completed successfully, including `scikit-learn` and `reportlab`.
`pip check` reported no broken requirements.

## Full automated verification

The complete repository test inventory contains 281 tests. The CLI integration
tests were run separately because they intentionally launch subprocesses for
both documented CLI invocation forms.

```powershell
python -m pytest -q -p no:cacheprovider tests/test_cli_integration.py
# 9 passed

python -m pytest -q -p no:cacheprovider <all other test files>
# 272 passed
```

**Final full-suite result: 281 passed.**

## End-to-end interface verification

The documented user commands ran successfully in the fresh environment:

```powershell
python -m src.cli --help
python -m src.cli dataset/clean/pair_081_clean.png
python -m src.cli dataset/stego/pair_083_stego.png
```

The clean example produced ensemble score `0.3876` and `Clean`. The stego
example produced ensemble score `0.8065` and `Suspicious`. The optional GUI
also launched successfully and visibly displayed a completed analysis with its
classification, ensemble score, threshold, and all three detector values.

## Configuration and official-result protection

The release remains bound to the existing locked configuration:

| Setting | Locked value |
| --- | ---: |
| Chi-square weight | `0.00` |
| RS weight | `0.70` |
| Difference Histogram weight | `0.30` |
| Decision threshold | `0.70` |

The official Week 11 artifact remains unchanged: accuracy `0.6250`, precision
`0.6923`, recall `0.4500`, F1 `0.5455`, and confusion counts TP `9`, TN `16`,
FP `4`, FN `11`. No held-out data was used for recalibration during Week 14.

## Repository and documentation audit

- Confirmed the required source, tests, data, dataset, docs, README,
  requirements, and minutes locations are present.
- Confirmed the README clean/stego example paths exist.
- Checked local Markdown links in `README.md`, `docs/`, and `minutes/`; no
  broken local targets were found.
- Confirmed no temporary test or cache directories are tracked by Git.
- Confirmed `requirements.txt` includes the third-party packages needed by the
  project scripts, including `reportlab`.

## Release decision

The repository is ready for the final annotated Git tag after this Menishen
audit record is merged into `main`. The `v1.0-final` tag is deliberately the
last release action.
