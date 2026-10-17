"""Validate detector-score data before ensemble use"""

import argparse
import csv
import math
from pathlib import Path


REQUIRED_COLUMNS = {
    "source_id",
    "label",
    "split",
    "chi_square_score",
    "rs_score",
    "dh_score",
    "status",
}


SCORE_COLUMNS = (
    "chi_square_score",
    "rs_score",
    "dh_score",
)


VALID_LABELS = {
    "clean",
    "stego",
}


def _read_score(row, column):
    """
    Read and validate one detector score from a CSV row.
    
    Score must:
    - Exist, 
    - Numeric,
    - Finite,
    - Be between 0.0 and 1.0
    """

    raw_value = row[column]

    if raw_value is None or raw_value.strip() == "":
        raise ValueError(
            f"{column} is missing"
        )

    try:
        value = float(raw_value)
    except (TypeError, ValueError):
        raise ValueError(
            f"{column} must be numeric"
        )

    if not math.isfinite(value):
        raise ValueError(
            f"{column} must be finite"
        )

    if value < 0.0 or value > 1.0:
        raise ValueError(
            f"{column} must be between 0.0 and 1.0"
        )

    return value


def validate_ensemble_inputs(score_path):
    """
    Validate development rows before ensemble use.
    
    Checks:
    - Required columns,
    - Development rows exist,
    - Complete status,
    - Valid clean/stego labels,
    - Valid detector scores,
    - Both clean and stego are present

    Return a summary dictionary.
    """

    score_path = Path(score_path)

    # Make sure the score file exists
    if not score_path.exists():
        raise FileNotFoundError(
            f"Score file does not exist: {score_path}"
        )

    # Open the detector-score CSV
    with score_path.open(
        "r",
        newline = "",
        encoding = "utf-8",
    ) as handle:

        reader = csv.DictReader(handle)

        # Make sure the CSV has a header
        if reader.fieldnames is None:
            raise ValueError(
                "Score file must contain a header row"
            )

        # Check for required columns
        missing_columns = (
            REQUIRED_COLUMNS
            - set(reader.fieldnames)
        )

        if missing_columns:
            raise ValueError(
                "Missing required columns: "
                + ", ".join(
                    sorted(missing_columns)
                )
            )

        # Keep only development rows
        development_rows = [
            row
            for row in reader
            if row["split"] == "development"
        ]

    # Development data must exist
    if not development_rows:
        raise ValueError(
            "No development rows found"
        )

    clean_count = 0
    stego_count = 0

    # Validate every development row
    for row in development_rows:
        source_id = row["source_id"]

        if source_id is None or source_id.strip() == "":
            raise ValueError(
                "Development row is missing source_id"
            )

        source_id = source_id.strip()

        if row["status"] != "complete":
            raise ValueError(
                f"{source_id} Does not have complete status"
            )

        label_value = row["label"]

        if label_value is None or label_value.strip() == "":
            raise ValueError(
                f"{source_id} is missing a label"
            )
        
        label = label_value.strip()

        if label not in VALID_LABELS:
            raise ValueError(
                f"{source_id} Has invalid label: {label}"
            )

        # Validate all detector scores
        for column in SCORE_COLUMNS:
            _read_score(
                row,
                column,
            )

        if label == "clean":
            clean_count += 1

        elif label == "stego":
            stego_count += 1

    # Both classes must be represented
    if clean_count == 0:
        raise ValueError(
            "Development data contains no clean rows"
        )

    if stego_count == 0:
        raise ValueError(
            "Development data contains no stego rows"
        )

    return {
        "rows_checked": len(development_rows),
        "clean_count": clean_count,
        "stego_count": stego_count,
        "invalid_row_count": 0,
        "required_columns_present": True
    }


def format_validation(summary):
    """Create readable terminal output from the validation summary."""

    return "\n".join(
        [
            "Ensemble Input Validation",
            "",
            f"Development Rows Checked: {summary['rows_checked']}",
            f"Clean Rows: {summary['clean_count']}",
            f"Stego Rows: {summary['stego_count']}",
            f"Invalid Rows: {summary['invalid_row_count']}",
            "",
            "Required Columns: PASS",
            "Detector Scores: PASS",
            "Labels: PASS",
            "Status: PASS",
            "",
            "Result: VALID",
        ]
    )


def main(argv = None):
    """Run ensemble-input validation from the command line."""

    parser = argparse.ArgumentParser(
        description = "Validate detector-score data before ensemble use."
    )

    parser.add_argument(
        "--scores",
        type = Path,
        default = Path("data/development_detector_scores.csv"),
        help = "Path to the detector-score CSV file.",
    )

    args = parser.parse_args(argv)

    try:
        summary = validate_ensemble_inputs(
            args.scores
        )

    except (FileNotFoundError, ValueError) as error:
        print("Ensemble Input Validation")
        print()
        print("Result: INVALID")
        print(f"Reason: {error}")

        return 1

    print(
        format_validation(summary)
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())