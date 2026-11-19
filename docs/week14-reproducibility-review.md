# Week 14 - Final Documentation and Reproducibility Review

## Purpose

This review verifies that the final Multi-Feature Steganalysis Toolkit documentation, dataset workflow, command-line interface, and graphical user interface accurately represent the current project and provide sufficient information for another user to understand and reproduce the experimental workflow.

The review focuses on:

- README accuracy
- documented command verification
- clean-dataset provenance
- paired-dataset generation
- metadata reproducibility
- CLI operation
- GUI operation
- documentation links and paths
- final reproducibility-related corrections

This review does not modify the detector algorithms, score normalization, ensemble weights, decision threshold, or held-out evaluation results.

---

## Installation/Dependency Verification

The project dependencies are documented in:

```
requirements.txt
```

### Requirements Installation

The documented dependency installation command is:

```
pip install -r requirements.txt
```

The command was executed successfully in the project environment.

Result: PASS

### ReportLab Dependency Review

During the final reproducibility audit, the script:

```
scripts/export_week10_report_pdf.py
```

was found to import the third-party `reportlab` package while ReportLab was not included in `requirements.txt`.

The missing dependency was corrected by adding:

```
reportlab>=4.0
```

This ensures that the Week 10 PDF export script has its required external package documented with the rest of the project dependencies.

Result: **PASS - DEPENDENCY ISSUE CORRECTED**

---

## README Command Verification

The important user-facing commands documented in `README.md` were reviewed and executed from the repository root.

### CLI Help

Command:

```
python -m src.cli --help
```

The command successfully displayed the command-line interface help and expected image-path usage.

Result: **PASS**

### Clean Image Example

Command:

```
python -m src.cli dataset/clean/pair_081_clean.png
```

Expected classification:

```
Clean
```

Expected ensemble score:

```
approximately 0.3876
```

Observed result matched the documented clean example.

Result: **PASS**

### Suspicious Image Example

Command:

```
python -m src.cli dataset/stego/pair_083_stego.png
```

Expected classification:

```
Suspicious
```

Expected ensemble score:

```
approximately 0.8065
```

Observed result matched the documented suspicious example.

Result: **PASS**

### GUI Launch

Command:

```
python -m src.gui
```

The graphical user interface launched successfully from the repository root.

Result: **PASS**

---

## Clean Dataset and Provenance Verification

The repository contains the prepared clean-image dataset in:

```
dataset/clean/
```

The clean dataset was verified to contain:

```
100 PNG images
```

with filenames following the expected paired-image naming convention:

```
pair_001_clean.png
...
pair_100_clean.png
```

The clean-image provenance inventory is stored in:

```
data/clean_metadata.csv
```

The provenance file records a source ID, clean filename, and source/license information for each prepared clean image.

The clean images were sourced from the Art Institute of Chicago collection. The provenance records include information such as:

- source ID
- clean filename
- Art Institute of Chicago attribution
- artwork title
- creator information
- public-domain designation
- source artwork URL

A repository search did not identify a tracked script that originally downloaded and prepared the Art Institute images.

A team member confirmed that the original clean images were prepared separately and then committed to the repository.

Therefore, reproducibility of the experimental steganalysis workflow begins from the prepared clean dataset committed in:

```
dataset/clean/
```

rather than from an automated Art Institute image-acquisition script.

The repository provides the prepared test dataset and its source provenance directly.

Result: **PASS**

---

## Dataset Generation Workflow Verification

The project supports reproducible generation of randomized-LSB stego counterparts from the committed clean dataset.

### Clean Dataset Validation

The clean dataset protocol documents the validation command:

```
python -m src.evaluation.validate_dataset dataset/clean data/clean_metadata.csv --expected-count 100 --report data/clean_validation_report.json
```

This validation step checks the committed clean-image collection against its provenance inventory.

### Paired Dataset Generation

The documented full-dataset generation command is:

```
python -m src.evaluation.generate_dataset dataset/clean data/clean_metadata.csv dataset/stego data/metadata.csv --payload-rate 0.25 --seed 20260920
```

This workflow uses:

```
dataset/clean/
```

as the prepared clean-image input,

```
data/clean_metadata.csv
```

as the source/provenance inventory,

```
dataset/stego/
```

as the generated stego-image output directory, and

```
data/metadata.csv
```

as the paired experimental metadata output.

The primary experimental payload rate is:

```
0.25
```

The documented master seed is:

```
20260920
```

The dataset generator derives deterministic per-image random seeds from the master seed and each stable source ID. These per-image seeds are recorded in:

```
data/metadata.csv
```

The generator uses the existing randomized-LSB embedding implementation rather than a separate embedding algorithm.

### Dataset Contents

The final repository was verified to contain:

```
100 clean PNG images
100 stego PNG images
```

The clean and stego images use matching pair IDs.

Examples:

```
pair_001_clean.png
pair_001_stego.png
```

through:

```
pair_100_clean.png
pair_100_stego.png
```

The paired metadata was verified to record:

```
payload rate = 0.25
image width = 256
image height = 256
```

across the primary dataset.

The metadata also records the per-image random seeds used by the controlled generation workflow.

Result: **PASS**

---

## CLI Verification

The release-candidate command-line interface was verified using both a known clean held-out image and a known randomized-LSB stego held-out image.

### Known Clean Image

Image:

```
dataset/clean/pair_081_clean.png
```

Observed classification:

```
Clean
```

Observed ensemble score:

```
0.3876
```

Decision threshold:

```
0.70
```

The clean example behaved as documented.

Result: **PASS**

### Known Suspicious Image

Image:

```
dataset/stego/pair_083_stego.png
```

Observed classification:

```
Suspicious
```

Observed ensemble score:

```
0.8065
```

Decision threshold:

```
0.70
```

The suspicious example behaved as documented.

Result: **PASS**

The final locked configuration remained:

```
Chi-square = 0.00
RS         = 0.70
DH         = 0.30
Threshold  = 0.70
```

No detector formula, normalization direction, ensemble weight, or decision threshold was changed during this documentation and reproducibility review.

---

## GUI Verification

The graphical user interface was launched with:

```
python -m src.gui
```

The GUI uses the existing analysis pipeline through the CLI analysis layer rather than implementing separate detector, normalization, or ensemble logic.

### Clean Image Verification

Selected image:

```
dataset/clean/pair_081_clean.png
```

Observed GUI output:

```
Final Classification: Clean
Ensemble Score: 0.3876
Decision Threshold: 0.70
Chi-square: 0.0000 -> 0.0000
RS: 0.6217 -> 0.3783
Difference Histogram: 0.5906 -> 0.4094
```

Result: **PASS**

### Suspicious Image Verification

Selected image:

```
dataset/stego/pair_083_stego.png
```

Observed GUI output:

```
Final Classification: Suspicious
Ensemble Score: 0.8065
Decision Threshold: 0.70
Chi-square: 0.9603 -> 0.9603
RS: 0.2094 -> 0.7906
Difference Histogram: 0.1565 -> 0.8435
```

Result: **PASS**

### No Image Selected

Action:

Clicked **Analyze** without first selecting an image.

Expected behavior:

The GUI should display a warning instead of attempting analysis or crashing.

Observed behavior:

A warning dialog appeared and the application remained operational.

Result: **PASS**

### Invalid or Unreadable Image

Action:

An invalid non-image file was selected and analysis was attempted.

Expected behavior:

The GUI should display an analysis error instead of crashing.

Observed behavior:

The GUI displayed an error containing:

```
cannot identify image file
```

The application handled the invalid input without crashing.

Result: **PASS**

---

## Documentation and Link Review

The final user-facing documentation was reviewed for consistency with the current repository.

The review included:

- `README.md`
- `requirements.txt`
- `docs/week13-user-guide.md`
- dataset protocol documentation
- dataset source rules
- GUI documentation
- CLI documentation
- screenshot references
- dataset paths
- example commands
- configuration values

The README was updated to reflect that the optional GUI is now implemented rather than a future improvement.

The final project documentation now reflects both:

```
CLI
GUI
```

as current user interfaces.

The Week 13 CLI guide wording was updated so its screenshots are described as demonstrating the complete release-candidate CLI user workflow rather than implying that the screenshots cover every user interface.

Repository-relative image paths are used for committed documentation rather than local VS Code resource links.

The documented locked configuration remains:

```
Chi-square = 0.00
RS         = 0.70
DH         = 0.30
Threshold  = 0.70
```

Result: **PASS**

---

## Issues Found and Corrections Made

### Missing ReportLab Dependency

Issue:

```
scripts/export_week10_report_pdf.py
```

imports the third-party `reportlab` package, but ReportLab was not originally listed in:

```
requirements.txt
```

Correction:

```
reportlab>=4.0
```

was added to the project requirements.

Result: **CORRECTED**

### Outdated GUI Documentation

Issue:

The GUI had been implemented, but portions of the README still described graphical user-interface support as future work or did not reflect the GUI as part of the current project.

Correction:

The README was updated to identify the GUI as part of the current project and remove GUI support from future improvements.

Result: **CORRECTED**

### Dataset Reproducibility Documentation

Issue:

The README explained the dataset but did not clearly summarize the final reproducibility relationship between the committed clean images, provenance metadata, randomized-LSB generation, and paired metadata.

Correction:

A `Dataset Reproducibility` subsection was added under the `Project Dataset` section.

The documentation now identifies:

```
dataset/clean/
dataset/stego/
data/clean_metadata.csv
data/metadata.csv
src/lsb_embedder.py
```

and explains the controlled randomized-LSB workflow.

Result: **CORRECTED**

### Clean Image Acquisition Clarification

Issue:

No tracked repository script was found that downloads and prepares the original Art Institute of Chicago clean images.

Resolution:

A team member confirmed that the original clean images were prepared separately and committed to the repository.

The final documentation therefore treats the committed clean dataset as the reproducible starting point for the experimental generation workflow, while `data/clean_metadata.csv` preserves source provenance and attribution.

Result: **DOCUMENTED**

---

## Final Result

The final documentation and reproducibility audit verified that:

```
README user commands                        PASS
CLI help                                    PASS
Known clean CLI example                     PASS
Known suspicious CLI example                PASS
GUI launch                                  PASS
GUI clean-image analysis                    PASS
GUI suspicious-image analysis               PASS
GUI no-image handling                       PASS
GUI invalid-image handling                  PASS
100 clean PNG images                        PASS
100 stego PNG images                        PASS
Matching clean/stego pair IDs               PASS
Clean-image provenance records              PASS
Payload rate 0.25                           PASS
Image dimensions 256 x 256                  PASS
Clean-dataset validation workflow           PASS
Full paired-dataset generation workflow     VERIFIED
Master generation seed documented           PASS
Per-image reproducible seeds recorded       PASS
Documentation paths and wording reviewed    PASS
ReportLab dependency issue                  CORRECTED
GUI documentation status                    CORRECTED
Dataset reproducibility explanation         CORRECTED
```

The original clean images were prepared separately and committed to the repository, with their provenance documented in `data/clean_metadata.csv`.

From that committed clean dataset, the randomized-LSB paired experimental dataset has a documented and reproducible validation and generation workflow.

No detector algorithms, normalization rules, locked ensemble weights, decision threshold, or held-out evaluation results were changed during this review.

**Final Week 14 documentation and reproducibility review result: PASS.**
