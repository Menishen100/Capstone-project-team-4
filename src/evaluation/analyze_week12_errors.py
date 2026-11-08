"""Analyze Week 11 held-out errors without changing the locked evaluation.

This module is deliberately descriptive.  It reads the immutable Week 11
prediction table, labels its TP/TN/FP/FN rows, and writes a smaller CSV for the
false-positive and false-negative cases.  It does not load images, invoke a
detector, tune a threshold, or rewrite any Week 11 artifact.
"""

from __future__ import annotations

import argparse
import csv
import math
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any


HELD_OUT_SPLIT = "held_out_test"
LOCKED_THRESHOLD = 0.70
EXPECTED_ROW_COUNT = 40
EXPECTED_SOURCE_COUNT = 20
ERROR_TYPES = ("false_positive", "false_negative")
CASE_TYPES = ("true_positive", "true_negative", *ERROR_TYPES)
REQUIRED_PREDICTION_COLUMNS = (
    "source_id",
    "label",
    "filename",
    "split",
    "chi_square_score",
    "rs_score",
    "dh_score",
    "normalized_chi",
    "normalized_rs",
    "normalized_dh",
    "ensemble_score",
    "prediction",
)
ERROR_CASE_COLUMNS = (
    "source_id",
    "label",
    "prediction",
    "error_type",
    "chi_square_score",
    "rs_score",
    "dh_score",
    "normalized_chi",
    "normalized_rs",
    "normalized_dh",
    "ensemble_score",
    "distance_from_threshold",
)
SCORE_COLUMNS = (
    "chi_square_score",
    "rs_score",
    "dh_score",
    "normalized_chi",
    "normalized_rs",
    "normalized_dh",
    "ensemble_score",
)


def _finite_score(row: Mapping[str, str], column: str) -> float:
    """Read one bounded score from an official Week 11 prediction row."""
    try:
        value = float(row[column])
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(f"invalid {column} for source {row.get('source_id', '<unknown>')}") from error
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError(f"{column} must be a finite score in [0, 1]")
    return value


def load_official_predictions(
    path: str | Path,
    *,
    expected_row_count: int = EXPECTED_ROW_COUNT,
    expected_source_count: int = EXPECTED_SOURCE_COUNT,
) -> list[dict[str, str]]:
    """Load and validate the complete, paired official held-out table."""
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        missing = set(REQUIRED_PREDICTION_COLUMNS) - fields
        if missing:
            raise ValueError("prediction CSV is missing required columns: " + ", ".join(sorted(missing)))
        rows = [dict(row) for row in reader]

    if len(rows) != expected_row_count:
        raise ValueError(f"Week 12 analysis requires exactly {expected_row_count} prediction rows; found {len(rows)}")
    if any(row.get("split") != HELD_OUT_SPLIT for row in rows):
        raise ValueError("Week 12 analysis accepts held_out_test rows only")

    labels = Counter(row.get("label") for row in rows)
    if labels != Counter({"clean": expected_row_count // 2, "stego": expected_row_count // 2}):
        raise ValueError("prediction CSV must contain equal clean and stego rows")
    if any(row.get("prediction") not in {"clean", "stego"} for row in rows):
        raise ValueError("prediction CSV contains an invalid prediction label")

    source_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        source_id = (row.get("source_id") or "").strip()
        if not source_id:
            raise ValueError("prediction CSV contains an empty source_id")
        source_groups[source_id].append(row)
        for column in SCORE_COLUMNS:
            _finite_score(row, column)
    if len(source_groups) != expected_source_count:
        raise ValueError(f"prediction CSV requires exactly {expected_source_count} source IDs; found {len(source_groups)}")
    if any(Counter(row["label"] for row in group) != Counter({"clean": 1, "stego": 1}) for group in source_groups.values()):
        raise ValueError("each source must have exactly one clean row and one stego row")
    return sorted(rows, key=lambda row: (row["source_id"], row["label"]))


def case_type(row: Mapping[str, str]) -> str:
    """Return the observed confusion-matrix category for one result row."""
    label = row.get("label")
    prediction = row.get("prediction")
    categories = {
        ("stego", "stego"): "true_positive",
        ("clean", "clean"): "true_negative",
        ("clean", "stego"): "false_positive",
        ("stego", "clean"): "false_negative",
    }
    try:
        return categories[(label, prediction)]
    except KeyError as error:
        raise ValueError("row must use clean/stego label and prediction values") from error


def classify_cases(rows: Iterable[Mapping[str, str]]) -> dict[str, list[dict[str, str]]]:
    """Group official rows into TP, TN, FP, and FN without reclassification."""
    grouped = {category: [] for category in CASE_TYPES}
    for source_row in rows:
        row = dict(source_row)
        grouped[case_type(row)].append(row)
    return grouped


def build_error_cases(rows: Iterable[Mapping[str, str]], *, threshold: float = LOCKED_THRESHOLD) -> list[dict[str, str]]:
    """Return FP/FN rows with signed distance from the unchanged threshold."""
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be in [0, 1]")
    cases: list[dict[str, str]] = []
    for row in rows:
        category = case_type(row)
        if category not in ERROR_TYPES:
            continue
        score = _finite_score(row, "ensemble_score")
        cases.append({
            "source_id": row["source_id"],
            "label": row["label"],
            "prediction": row["prediction"],
            "error_type": category,
            **{column: row[column] for column in SCORE_COLUMNS},
            "distance_from_threshold": f"{score - threshold:.12g}",
        })
    return sorted(cases, key=lambda row: (row["error_type"], row["source_id"]))


def summarize_cases(rows: Iterable[Mapping[str, str]]) -> dict[str, Any]:
    """Summarize observed categories and score means for the Week 12 review."""
    grouped = classify_cases(rows)
    summary: dict[str, Any] = {"case_counts": {category: len(grouped[category]) for category in CASE_TYPES}}
    mean_scores: dict[str, dict[str, float]] = {}
    for category, category_rows in grouped.items():
        if category_rows:
            mean_scores[category] = {
                column: sum(_finite_score(row, column) for row in category_rows) / len(category_rows)
                for column in SCORE_COLUMNS
            }
    summary["mean_scores"] = mean_scores
    return summary


def write_error_cases(error_cases: Iterable[Mapping[str, str]], output_path: str | Path) -> None:
    """Write a deterministic derived CSV without touching Week 11 inputs."""
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=ERROR_CASE_COLUMNS)
        writer.writeheader()
        writer.writerows(error_cases)


def format_summary(summary: Mapping[str, Any], error_cases: Iterable[Mapping[str, str]]) -> str:
    """Format an evidence-friendly descriptive summary, never a tuning proposal."""
    cases = list(error_cases)
    source_ids = {
        error_type: [case["source_id"] for case in cases if case["error_type"] == error_type]
        for error_type in ERROR_TYPES
    }
    counts = summary["case_counts"]
    means = summary["mean_scores"]
    lines = [
        "Week 12 Held-Out Error Analysis Complete",
        f"Locked threshold retained: {LOCKED_THRESHOLD:.2f}",
        f"TP={counts['true_positive']}, TN={counts['true_negative']}, FP={counts['false_positive']}, FN={counts['false_negative']}",
        "False-positive source IDs: " + ", ".join(source_ids["false_positive"]),
        "False-negative source IDs: " + ", ".join(source_ids["false_negative"]),
        "Mean normalized scores for false negatives: "
        f"Chi={means['false_negative']['normalized_chi']:.4f}, "
        f"RS={means['false_negative']['normalized_rs']:.4f}, "
        f"DH={means['false_negative']['normalized_dh']:.4f}",
        "No weights, threshold, preprocessing, detector behavior, predictions, or Week 11 metrics were changed.",
    ]
    return "\n".join(lines)


def main(arguments: Iterable[str] | None = None) -> int:
    """Create the Week 12 derived error-case table from official predictions."""
    parser = argparse.ArgumentParser(description="Analyze official Week 11 held-out FP/FN cases without retuning.")
    parser.add_argument("--predictions", type=Path, default=Path("data/week11_heldout_predictions.csv"))
    parser.add_argument("--output", type=Path, default=Path("data/week12_error_cases.csv"))
    args = parser.parse_args(arguments)

    rows = load_official_predictions(args.predictions)
    error_cases = build_error_cases(rows)
    summary = summarize_cases(rows)
    write_error_cases(error_cases, args.output)
    print(format_summary(summary, error_cases))
    print(f"Error-case CSV: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
