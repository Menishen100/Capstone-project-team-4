# Clean Dataset Source and Validation Rules

Arthur's validation step runs before LSB embedding. Its purpose is to make sure
only suitable, traceable clean source images enter the paired-dataset workflow.

## Inventory

Maintain `data/clean_metadata.csv` with one row per file and these required
columns:

```text
source_id,filename,source_license_note
```

`source_id` must be unique and stable. `source_license_note` must identify the
actual source and license or permission, for example `Unsplash, photographer
name, Unsplash License, URL`. Do not write a placeholder or infer a license.
The validator also reports the detected format, color mode, dimensions, and a
pixel-content hash in its JSON output.

## Acceptance rules

- Exactly 100 clean source files are expected for the Week 5 collection.
- PNG and BMP are accepted; JPEG and other formats are rejected.
- Images must decode successfully, be mode `L` or `RGB`, and meet the configured
  minimum dimensions.
- Every file needs one inventory row; every inventory row must refer to a file.
- Source IDs, filenames, and decoded pixel content must be unique.
- The clean directory must not contain names that indicate stego output.

## Run the validator

Install dependencies, complete the source inventory with genuine information,
then run this command from the repository root:

```powershell
python -m src.evaluation.validate_dataset dataset/clean data/clean_metadata.csv --expected-count 100 --report data/clean_validation_report.json
```

An exit code of `0` means the dataset is ready for the generator. An exit code
of `1` means the report contains issues that must be resolved first.
