"""Run the one-time Week 11 held-out evaluation with the locked configuration.

This runner deliberately reads only ``split=held_out_test`` metadata rows.  It
uses the Week 10 selected configuration unchanged and refuses to overwrite its
official result files, preventing an accidental second official run.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from collections.abc import Iterable, Mapping
from numbers import Real
from pathlib import Path
from typing import Any

from src.ensemble.voting import EnsembleConfig, combine_detector_scores
from src.evaluation.grid_search_ensemble import classification_metrics
from src.evaluation.run_preliminary_scores import default_detectors
from src.preprocessing import load_image


HELD_OUT_SPLIT = "held_out_test"
EXPECTED_PAIR_COUNT = 20
LOCKED_CONFIG = EnsembleConfig(
    chi_square_weight=0.00,
    rs_weight=0.70,
    dh_weight=0.30,
    threshold=0.70,
)
REQUIRED_METADATA_FIELDS = {
    "source_id",
    "clean_filename",
    "stego_filename",
    "split",
}
DETECTOR_NAMES = ("chi_square", "rs", "dh")
PREDICTION_COLUMNS = (
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
    "correct",
)


def heldout_pairs(
    metadata_path: str | Path,
    *,
    expected_pair_count: int = EXPECTED_PAIR_COUNT,
) -> list[dict[str, str]]:
    """Load exactly the expected number of held-out clean/stego source pairs."""
    if expected_pair_count <= 0:
        raise ValueError("expected_pair_count must be positive")
    with Path(metadata_path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        missing = REQUIRED_METADATA_FIELDS - fields
        if missing:
            raise ValueError("metadata is missing required columns: " + ", ".join(sorted(missing)))
        pairs = [dict(row) for row in reader if row.get("split") == HELD_OUT_SPLIT]

    if len(pairs) != expected_pair_count:
        raise ValueError(
            f"held-out evaluation requires exactly {expected_pair_count} source pairs; found {len(pairs)}"
        )
    source_ids = [(pair.get("source_id") or "").strip() for pair in pairs]
    if not all(source_ids):
        raise ValueError("held-out metadata contains an empty source_id")
    if len(source_ids) != len(set(source_ids)):
        raise ValueError("held-out metadata contains duplicate source_id values")
    for pair in pairs:
        for column in ("clean_filename", "stego_filename"):
            if not (pair.get(column) or "").strip():
                raise ValueError(f"{pair['source_id']} is missing {column}")
    return sorted(pairs, key=lambda pair: pair["source_id"])


def _bounded_score(result: Mapping[str, Any]) -> float:
    """Extract one detector's documented common-interface score."""
    score = result.get("score")
    if isinstance(score, bool) or not isinstance(score, Real) or not math.isfinite(float(score)):
        raise ValueError("detector returned a non-finite numeric score")
    if not 0.0 <= float(score) <= 1.0:
        raise ValueError("detector returned a score outside [0, 1]")
    return float(score)


def _score_image(
    source_id: str,
    label: str,
    filename: str,
    image_directory: Path,
    detectors: Mapping[str, Any],
) -> dict[str, str]:
    """Evaluate one held-out image through the fixed ensemble pipeline."""
    image = load_image(image_directory / filename)
    scores = {
        detector_name: _bounded_score(detectors[detector_name].analyze(image))
        for detector_name in DETECTOR_NAMES
    }
    result = combine_detector_scores(scores, LOCKED_CONFIG)
    diagnostics = result["diagnostics"]
    normalized = diagnostics["normalized_scores"]
    prediction = "stego" if result["label"] == "Suspicious" else "clean"
    return {
        "source_id": source_id,
        "label": label,
        "filename": filename,
        "split": HELD_OUT_SPLIT,
        "chi_square_score": str(scores["chi_square"]),
        "rs_score": str(scores["rs"]),
        "dh_score": str(scores["dh"]),
        "normalized_chi": str(normalized["chi_square"]),
        "normalized_rs": str(normalized["rs"]),
        "normalized_dh": str(normalized["dh"]),
        "ensemble_score": str(result["ensemble_score"]),
        "prediction": prediction,
        "correct": str(prediction == label),
    }


def evaluate_heldout_pairs(
    pairs: Iterable[Mapping[str, str]],
    clean_directory: str | Path,
    stego_directory: str | Path,
    *,
    detectors: Mapping[str, Any] | None = None,
) -> list[dict[str, str]]:
    """Score held-out clean/stego pairs with no opportunity to recalibrate."""
    active_detectors = dict(detectors or default_detectors())
    if set(active_detectors) != set(DETECTOR_NAMES):
        raise ValueError("detectors must provide chi_square, rs, and dh entries")
    rows: list[dict[str, str]] = []
    for pair in pairs:
        if pair.get("split") != HELD_OUT_SPLIT:
            raise ValueError("held-out evaluation cannot use development or validation rows")
        source_id = str(pair["source_id"])
        rows.append(_score_image(source_id, "clean", str(pair["clean_filename"]), Path(clean_directory), active_detectors))
        rows.append(_score_image(source_id, "stego", str(pair["stego_filename"]), Path(stego_directory), active_detectors))
    return rows


def metrics_summary(rows: Iterable[Mapping[str, str]]) -> dict[str, object]:
    """Calculate final metric and confusion-matrix values for complete output rows."""
    materialized = list(rows)
    labels = [str(row.get("label", "")) for row in materialized]
    predictions = [str(row.get("prediction", "")) for row in materialized]
    if not materialized or any(row.get("split") != HELD_OUT_SPLIT for row in materialized):
        raise ValueError("metrics require held_out_test prediction rows only")
    counts = Counter(labels)
    if counts != Counter({"clean": len(materialized) // 2, "stego": len(materialized) // 2}):
        raise ValueError("held-out predictions must contain equal clean and stego counts")
    metrics = classification_metrics(labels, predictions)
    confusion = {
        "true_positive": sum(label == "stego" and prediction == "stego" for label, prediction in zip(labels, predictions, strict=True)),
        "true_negative": sum(label == "clean" and prediction == "clean" for label, prediction in zip(labels, predictions, strict=True)),
        "false_positive": sum(label == "clean" and prediction == "stego" for label, prediction in zip(labels, predictions, strict=True)),
        "false_negative": sum(label == "stego" and prediction == "clean" for label, prediction in zip(labels, predictions, strict=True)),
    }
    if sum(confusion.values()) != len(materialized):
        raise ValueError("confusion-matrix counts do not cover every held-out row")
    return {
        "evaluation_split": HELD_OUT_SPLIT,
        "configuration": {
            "chi_square_weight": LOCKED_CONFIG.chi_square_weight,
            "rs_weight": LOCKED_CONFIG.rs_weight,
            "dh_weight": LOCKED_CONFIG.dh_weight,
            "threshold": LOCKED_CONFIG.threshold,
        },
        "image_counts": {
            "total": len(materialized),
            "clean": counts["clean"],
            "stego": counts["stego"],
        },
        "confusion_matrix": confusion,
        "metrics": metrics,
    }


def _ensure_new_output_paths(*paths: Path) -> None:
    """Refuse to overwrite official results after a held-out run."""
    existing = [str(path) for path in paths if path.exists()]
    if existing:
        raise FileExistsError("refusing to overwrite held-out results: " + ", ".join(existing))


def write_outputs(
    rows: Iterable[Mapping[str, str]],
    summary: Mapping[str, object],
    predictions_path: str | Path,
    metrics_path: str | Path,
) -> None:
    """Write the immutable official prediction CSV and final metrics JSON."""
    predictions_destination = Path(predictions_path)
    metrics_destination = Path(metrics_path)
    _ensure_new_output_paths(predictions_destination, metrics_destination)
    predictions_destination.parent.mkdir(parents=True, exist_ok=True)
    metrics_destination.parent.mkdir(parents=True, exist_ok=True)
    with predictions_destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=PREDICTION_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    with metrics_destination.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")


def run_heldout_evaluation(
    metadata_path: str | Path,
    clean_directory: str | Path,
    stego_directory: str | Path,
    predictions_path: str | Path,
    metrics_path: str | Path,
    *,
    detectors: Mapping[str, Any] | None = None,
    expected_pair_count: int = EXPECTED_PAIR_COUNT,
) -> tuple[list[dict[str, str]], dict[str, object]]:
    """Execute one held-out run and persist its predictions and metrics."""
    prediction_file = Path(predictions_path)
    metric_file = Path(metrics_path)
    _ensure_new_output_paths(prediction_file, metric_file)
    pairs = heldout_pairs(metadata_path, expected_pair_count=expected_pair_count)
    rows = evaluate_heldout_pairs(pairs, clean_directory, stego_directory, detectors=detectors)
    if len(rows) != expected_pair_count * 2:
        raise ValueError("held-out evaluation did not produce one clean and one stego row per pair")
    summary = metrics_summary(rows)
    if summary["image_counts"]["total"] != expected_pair_count * 2:
        raise ValueError("held-out summary does not cover the expected image count")
    write_outputs(rows, summary, prediction_file, metric_file)
    return rows, summary


def format_summary(summary: Mapping[str, object]) -> str:
    """Format held-out results without implying further calibration."""
    image_counts = summary["image_counts"]
    confusion = summary["confusion_matrix"]
    metrics = summary["metrics"]
    configuration = summary["configuration"]
    return "\n".join(
        (
            "Week 11 Held-Out Evaluation Complete",
            f"Split: {summary['evaluation_split']} ({image_counts['total']} images: {image_counts['clean']} clean, {image_counts['stego']} stego)",
            "Locked configuration: "
            f"Chi-square={configuration['chi_square_weight']:.2f}, "
            f"RS={configuration['rs_weight']:.2f}, DH={configuration['dh_weight']:.2f}, "
            f"threshold={configuration['threshold']:.2f}",
            f"Accuracy: {metrics['accuracy']:.4f}",
            f"Precision: {metrics['precision']:.4f}",
            f"Recall: {metrics['recall']:.4f}",
            f"F1: {metrics['f1']:.4f}",
            "Confusion matrix: "
            f"TP={confusion['true_positive']}, TN={confusion['true_negative']}, "
            f"FP={confusion['false_positive']}, FN={confusion['false_negative']}",
            "No weights, threshold, preprocessing, or detector behavior was changed after this held-out run.",
        )
    )


def main(arguments: Iterable[str] | None = None) -> int:
    """Run the locked Week 11 final held-out evaluation once."""
    parser = argparse.ArgumentParser(description="Run the locked Week 11 held-out evaluation once.")
    parser.add_argument("--metadata", type=Path, default=Path("data/metadata.csv"))
    parser.add_argument("--clean-directory", type=Path, default=Path("dataset/clean"))
    parser.add_argument("--stego-directory", type=Path, default=Path("dataset/stego"))
    parser.add_argument("--predictions", type=Path, default=Path("data/week11_heldout_predictions.csv"))
    parser.add_argument("--metrics", type=Path, default=Path("data/week11_heldout_metrics.json"))
    args = parser.parse_args(arguments)
    _, summary = run_heldout_evaluation(
        args.metadata,
        args.clean_directory,
        args.stego_directory,
        args.predictions,
        args.metrics,
    )
    print(format_summary(summary))
    print(f"Predictions CSV: {args.predictions}")
    print(f"Metrics JSON: {args.metrics}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
