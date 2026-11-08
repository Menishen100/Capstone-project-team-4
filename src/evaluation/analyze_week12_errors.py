"""Analyze the locked Week 11 held-out predictions without rescoring them."""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping


THRESHOLD = 0.70
ERROR_COLUMNS = (
    "source_id", "label", "prediction", "error_type", "chi_square_score",
    "rs_score", "dh_score", "normalized_chi", "normalized_rs",
    "normalized_dh", "ensemble_score", "distance_from_threshold",
)
CELL_NAMES = ("true_positive", "true_negative", "false_positive", "false_negative")


def read_predictions(path: str | Path) -> list[dict[str, str]]:
    """Read the official prediction CSV and validate fields and labels."""
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = set(ERROR_COLUMNS) - {"error_type", "distance_from_threshold"}
        missing = required - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"prediction CSV is missing columns: {sorted(missing)}")
        rows = list(reader)
    if not rows:
        raise ValueError("prediction CSV must contain at least one row")
    for index, row in enumerate(rows, start=2):
        if row["label"].strip().lower() not in {"clean", "stego"}:
            raise ValueError(f"row {index}: label must be clean or stego")
        if row["prediction"].strip().lower() not in {"clean", "stego"}:
            raise ValueError(f"row {index}: prediction must be clean or stego")
        for field in ERROR_COLUMNS[4:-1] + ("ensemble_score",):
            try:
                value = float(row[field])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"row {index}: {field} must be numeric") from exc
            if not math.isfinite(value):
                raise ValueError(f"row {index}: {field} must be finite")
    return rows


def classify_cell(label: str, prediction: str) -> str:
    """Return the confusion-matrix cell with stego as the positive class."""
    truth, predicted = label.strip().lower(), prediction.strip().lower()
    if truth not in {"clean", "stego"} or predicted not in {"clean", "stego"}:
        raise ValueError("label and prediction must be clean or stego")
    if truth == "stego":
        return "true_positive" if predicted == "stego" else "false_negative"
    return "false_positive" if predicted == "stego" else "true_negative"


def analyze_rows(rows: Iterable[Mapping[str, Any]], threshold: float = THRESHOLD) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    """Return all four confusion groups and a table containing only errors."""
    if not math.isfinite(threshold):
        raise ValueError("threshold must be finite")
    groups: dict[str, list[dict[str, Any]]] = {name: [] for name in CELL_NAMES}
    errors: list[dict[str, Any]] = []
    for source in rows:
        row = dict(source)
        cell = classify_cell(str(row["label"]), str(row["prediction"]))
        groups[cell].append(row)
        if cell in {"false_positive", "false_negative"}:
            case = {column: row[column] for column in ERROR_COLUMNS if column in row}
            case["error_type"] = cell
            case["distance_from_threshold"] = float(row["ensemble_score"]) - threshold
            errors.append(case)
    return groups, errors


def write_error_cases(path: str | Path, errors: Iterable[Mapping[str, Any]]) -> None:
    """Write error rows in a stable, reviewable column order."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=ERROR_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(errors)


def format_summary(groups: Mapping[str, list[Mapping[str, Any]]]) -> str:
    """Format confusion counts and exact error source IDs for terminal review."""
    lines = ["Week 11 held-out confusion groups (read-only analysis)"]
    for name in CELL_NAMES:
        entries = groups[name]
        ids = ", ".join(str(row["source_id"]) for row in entries)
        lines.append(f"{name}: {len(entries)}" + (f" | {ids}" if name.startswith("false_") else ""))
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions", type=Path, default=Path("data/week11_heldout_predictions.csv"))
    parser.add_argument("--output", type=Path, default=Path("data/week12_error_cases.csv"))
    args = parser.parse_args(argv)
    groups, errors = analyze_rows(read_predictions(args.predictions))
    write_error_cases(args.output, errors)
    print(format_summary(groups))
    print(f"\nWrote {len(errors)} error cases to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
