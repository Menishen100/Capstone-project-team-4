"""Reproducible Week 10 ensemble calibration on development and validation data.

The runner deliberately scores only the approved development and validation
splits.  It never reads images or labels from ``held_out_test``.  Candidate
weights are evaluated on both permitted splits, while the selected
configuration is chosen strictly from validation metrics.
"""

from __future__ import annotations

import argparse
import csv
import math
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from src.ensemble.voting import EnsembleConfig, combine_detector_scores
from src.evaluation.run_preliminary_scores import default_detectors
from src.preprocessing import load_image


CALIBRATION_SPLITS = ("development", "validation")
REQUIRED_METADATA_FIELDS = {
    "source_id",
    "clean_filename",
    "stego_filename",
    "split",
}
SCORE_COLUMNS = ("chi_square", "rs", "dh")
RESULT_COLUMNS = (
    "rank",
    "selected",
    "chi_weight",
    "rs_weight",
    "dh_weight",
    "threshold",
    "development_accuracy",
    "development_precision",
    "development_recall",
    "development_f1",
    "validation_accuracy",
    "validation_precision",
    "validation_recall",
    "validation_f1",
    "development_rows",
    "validation_rows",
)


@dataclass(frozen=True)
class ScoredImage:
    """One detector-score record used for calibration."""

    source_id: str
    split: str
    label: str
    chi_square: float
    rs: float
    dh: float

    def __post_init__(self) -> None:
        if self.split not in CALIBRATION_SPLITS:
            raise ValueError("calibration rows must use development or validation splits only")
        if self.label not in {"clean", "stego"}:
            raise ValueError("calibration labels must be clean or stego")
        for detector in SCORE_COLUMNS:
            value = getattr(self, detector)
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
                raise ValueError(f"{detector} must be a finite numeric score")
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(f"{detector} must be in [0, 1]")

    @property
    def scores(self) -> dict[str, float]:
        return {detector: float(getattr(self, detector)) for detector in SCORE_COLUMNS}


def weight_grid(step: float = 0.1) -> tuple[tuple[float, float, float], ...]:
    """Return every non-negative three-detector weight tuple summing to one.

    Integer units prevent floating-point drift.  With the documented 0.10
    increment, this produces 66 valid configurations.
    """
    if not isinstance(step, (int, float)) or isinstance(step, bool) or not math.isfinite(step):
        raise ValueError("weight step must be a finite numeric value")
    units = round(1.0 / float(step))
    if units <= 0 or not math.isclose(units * float(step), 1.0, abs_tol=1e-12):
        raise ValueError("weight step must divide 1.0 exactly")
    return tuple(
        (chi / units, rs / units, dh / units)
        for chi in range(units + 1)
        for rs in range(units - chi + 1)
        for dh in (units - chi - rs,)
    )


def threshold_grid(start: float = 0.30, stop: float = 0.70, step: float = 0.05) -> tuple[float, ...]:
    """Return the documented inclusive threshold candidates."""
    if step <= 0.0 or stop < start:
        raise ValueError("threshold range must have a positive step and stop >= start")
    count = round((stop - start) / step)
    values = tuple(round(start + index * step, 10) for index in range(count + 1))
    if not math.isclose(values[-1], stop, abs_tol=1e-9):
        raise ValueError("threshold step must reach the requested stop value")
    if any(value < 0.0 or value > 1.0 for value in values):
        raise ValueError("thresholds must remain in [0, 1]")
    return values


def _read_metadata(metadata_path: str | Path) -> list[dict[str, str]]:
    with Path(metadata_path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        missing = REQUIRED_METADATA_FIELDS - fields
        if missing:
            raise ValueError("metadata is missing required columns: " + ", ".join(sorted(missing)))
        return [dict(row) for row in reader if row.get("split") in CALIBRATION_SPLITS]


def score_calibration_images(
    metadata_path: str | Path,
    clean_directory: str | Path,
    stego_directory: str | Path,
    *,
    detectors: Mapping[str, Any] | None = None,
) -> list[ScoredImage]:
    """Score only development/validation clean-stego pairs for calibration."""
    active_detectors = dict(detectors or default_detectors())
    if set(active_detectors) != set(SCORE_COLUMNS):
        raise ValueError("detectors must provide chi_square, rs, and dh entries")

    records: list[ScoredImage] = []
    seen_sources: set[tuple[str, str]] = set()
    for pair in _read_metadata(metadata_path):
        source_id = (pair["source_id"] or "").strip()
        split = pair["split"]
        if not source_id:
            raise ValueError("calibration metadata row is missing source_id")
        if (split, source_id) in seen_sources:
            raise ValueError(f"duplicate calibration source_id: {source_id}")
        seen_sources.add((split, source_id))
        for label, directory, filename_column in (
            ("clean", Path(clean_directory), "clean_filename"),
            ("stego", Path(stego_directory), "stego_filename"),
        ):
            filename = (pair.get(filename_column) or "").strip()
            if not filename:
                raise ValueError(f"{source_id} is missing {filename_column}")
            image = load_image(directory / filename)
            scores = {
                name: float(active_detectors[name].analyze(image)["score"])
                for name in SCORE_COLUMNS
            }
            records.append(ScoredImage(source_id=source_id, split=split, label=label, **scores))

    expected = {"development", "validation"}
    found = {record.split for record in records}
    if found != expected:
        raise ValueError("calibration requires both development and validation score rows")
    return records


def classification_metrics(true_labels: Iterable[str], predictions: Iterable[str]) -> dict[str, float]:
    """Compute explainable binary metrics where ``stego`` is the positive class."""
    actual = list(true_labels)
    predicted = list(predictions)
    if not actual or len(actual) != len(predicted):
        raise ValueError("labels and predictions must be non-empty and have equal length")
    if any(label not in {"clean", "stego"} for label in [*actual, *predicted]):
        raise ValueError("labels and predictions must use clean or stego")
    true_positive = sum(label == "stego" and guess == "stego" for label, guess in zip(actual, predicted, strict=True))
    false_positive = sum(label == "clean" and guess == "stego" for label, guess in zip(actual, predicted, strict=True))
    false_negative = sum(label == "stego" and guess == "clean" for label, guess in zip(actual, predicted, strict=True))
    accuracy = sum(label == guess for label, guess in zip(actual, predicted, strict=True)) / len(actual)
    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"accuracy": accuracy, "precision": precision, "recall": recall, "f1": f1}


def _evaluate_split(records: Iterable[ScoredImage], config: EnsembleConfig) -> dict[str, float]:
    split_records = list(records)
    labels = [record.label for record in split_records]
    predictions = [
        "stego" if combine_detector_scores(record.scores, config)["label"] == "Suspicious" else "clean"
        for record in split_records
    ]
    return classification_metrics(labels, predictions)


def grid_search(records: Iterable[ScoredImage]) -> list[dict[str, float | int | bool]]:
    """Evaluate every documented configuration and deterministically select one.

    Selection uses validation F1, then validation recall, precision, and
    accuracy.  Exact ties prefer a threshold closest to 0.50 and then the
    lexicographically smallest weight tuple.  Development metrics are reported
    for transparency but never used to break selection ties.
    """
    materialized = list(records)
    by_split = {
        split: [record for record in materialized if record.split == split]
        for split in CALIBRATION_SPLITS
    }
    if any(not rows for rows in by_split.values()):
        raise ValueError("calibration requires non-empty development and validation rows")
    if any(record.split not in CALIBRATION_SPLITS for record in materialized):
        raise ValueError("held-out data is not permitted in grid search")

    results: list[dict[str, float | int | bool]] = []
    for chi_weight, rs_weight, dh_weight in weight_grid():
        for threshold in threshold_grid():
            config = EnsembleConfig(chi_weight, rs_weight, dh_weight, threshold)
            development = _evaluate_split(by_split["development"], config)
            validation = _evaluate_split(by_split["validation"], config)
            results.append(
                {
                    "rank": 0,
                    "selected": False,
                    "chi_weight": chi_weight,
                    "rs_weight": rs_weight,
                    "dh_weight": dh_weight,
                    "threshold": threshold,
                    **{f"development_{name}": value for name, value in development.items()},
                    **{f"validation_{name}": value for name, value in validation.items()},
                    "development_rows": len(by_split["development"]),
                    "validation_rows": len(by_split["validation"]),
                }
            )

    ranked = sorted(
        results,
        key=lambda row: (
            -float(row["validation_f1"]),
            -float(row["validation_recall"]),
            -float(row["validation_precision"]),
            -float(row["validation_accuracy"]),
            abs(float(row["threshold"]) - 0.50),
            float(row["chi_weight"]),
            float(row["rs_weight"]),
            float(row["dh_weight"]),
        ),
    )
    for index, row in enumerate(ranked, start=1):
        row["rank"] = index
        row["selected"] = index == 1
    return ranked


def write_results(results: Iterable[Mapping[str, object]], output_path: str | Path) -> None:
    """Write a stable CSV result table suitable for review and plotting."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=RESULT_COLUMNS)
        writer.writeheader()
        for result in results:
            writer.writerow({field: result[field] for field in RESULT_COLUMNS})


def format_selected_result(selected: Mapping[str, object]) -> str:
    """Format the selected validation configuration for a reproducible demo."""
    return "\n".join(
        (
            "Week 10 Ensemble Calibration Complete",
            "Selection metric: validation F1 (then recall, precision, accuracy)",
            f"Selected weights: Chi-square={float(selected['chi_weight']):.2f}, RS={float(selected['rs_weight']):.2f}, DH={float(selected['dh_weight']):.2f}",
            f"Selected threshold: {float(selected['threshold']):.2f}",
            f"Validation accuracy: {float(selected['validation_accuracy']):.4f}",
            f"Validation precision: {float(selected['validation_precision']):.4f}",
            f"Validation recall: {float(selected['validation_recall']):.4f}",
            f"Validation F1: {float(selected['validation_f1']):.4f}",
            f"Calibration rows: development={selected['development_rows']}, validation={selected['validation_rows']}",
            "Held-out test rows used: 0",
        )
    )


def run_grid_search(
    metadata_path: str | Path,
    clean_directory: str | Path,
    stego_directory: str | Path,
    output_path: str | Path,
) -> dict[str, float | int | bool]:
    """Score permitted data, evaluate candidates, write results, and return best row."""
    results = grid_search(score_calibration_images(metadata_path, clean_directory, stego_directory))
    write_results(results, output_path)
    return results[0]


def main(arguments: Iterable[str] | None = None) -> int:
    """Run the documented Week 10 development/validation-only grid search."""
    parser = argparse.ArgumentParser(description="Calibrate ensemble weights without using held-out data.")
    parser.add_argument("--metadata", type=Path, default=Path("data/metadata.csv"))
    parser.add_argument("--clean-directory", type=Path, default=Path("dataset/clean"))
    parser.add_argument("--stego-directory", type=Path, default=Path("dataset/stego"))
    parser.add_argument("--output", type=Path, default=Path("data/week10_grid_search_results.csv"))
    args = parser.parse_args(arguments)
    selected = run_grid_search(args.metadata, args.clean_directory, args.stego_directory, args.output)
    print(format_selected_result(selected))
    print(f"Results CSV: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
