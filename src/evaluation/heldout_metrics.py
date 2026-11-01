"""Independent verification of the locked Week 11 held-out result files.

This module consumes Menishen's per-image prediction CSV and metrics JSON. It
does not run detectors or adjust the locked configuration. Ensemble arithmetic
uses the existing calibration metric helper so its RS direction matches the
shared Week 9 voting convention in this repository.
"""

from __future__ import annotations

import csv
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from src.ensemble.normalization import (
    normalize_chi_square,
    normalize_dh,
    normalize_rs,
)
from src.ensemble.voting import EnsembleConfig, combine_detector_scores
from src.evaluation.calibration_metrics import classification_metrics


LOCKED_WEIGHTS = {
    "chi_weight": 0.00,
    "rs_weight": 0.70,
    "dh_weight": 0.30,
}
LOCKED_THRESHOLD = 0.70
EXPECTED_COUNTS = {"clean": 20, "stego": 20}
RESULT_FIELDS = {
    "source_id", "label", "filename", "split", "chi_square_score", "rs_score",
    "dh_score", "normalized_chi", "normalized_rs", "normalized_dh",
    "ensemble_score", "prediction",
}


def confusion_matrix_counts(
    y_true: Iterable[str], y_pred: Iterable[str]
) -> dict[str, int]:
    """Return TP/TN/FP/FN with stego as the positive class."""
    truth = [str(value).strip().lower() for value in y_true]
    predicted = [str(value).strip().lower() for value in y_pred]
    if not truth or len(truth) != len(predicted):
        raise ValueError("true and predicted labels must have equal non-zero length")
    allowed = {"clean", "stego"}
    if set(truth) - allowed or set(predicted) - allowed:
        raise ValueError("labels and predictions must be clean/stego")
    return {
        "tp": sum(a == "stego" and b == "stego" for a, b in zip(truth, predicted)),
        "tn": sum(a == "clean" and b == "clean" for a, b in zip(truth, predicted)),
        "fp": sum(a == "clean" and b == "stego" for a, b in zip(truth, predicted)),
        "fn": sum(a == "stego" and b == "clean" for a, b in zip(truth, predicted)),
    }


def _close(actual: Any, expected: float, name: str) -> None:
    try:
        value = float(actual)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if not math.isfinite(value) or not math.isclose(value, expected, rel_tol=1e-9, abs_tol=1e-9):
        raise ValueError(f"{name} mismatch: reported {actual}, recomputed {expected}")


def verify_heldout_results(
    rows: Sequence[Mapping[str, Any]],
    metadata_rows: Sequence[Mapping[str, Any]],
    summary: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate held-out membership and independently recalculate metrics.

    Each paired source must contribute exactly one clean and one stego image.
    This makes the expected 20/20 class balance verifiable even when the CSV
    identifies a pair by ``source_id`` rather than by filename.
    """
    heldout = [row for row in metadata_rows if row.get("split") == "held_out_test"]
    if len(heldout) != 20 or len({row.get("source_id") for row in heldout}) != 20:
        raise ValueError("metadata must contain exactly 20 unique held_out_test sources")
    expected_sources = {row["source_id"] for row in heldout}
    if len(rows) != 40:
        raise ValueError(f"expected exactly 40 held-out image rows; got {len(rows)}")
    if any(not RESULT_FIELDS.issubset(row) for row in rows):
        missing = sorted(set().union(*(RESULT_FIELDS - set(row) for row in rows)))
        raise ValueError(f"prediction rows are missing required fields: {missing}")
    if any(row.get("split") != "held_out_test" for row in rows):
        raise ValueError("every prediction row must be explicitly held_out_test")
    ids = [str(row["source_id"]) for row in rows]
    if set(ids) != expected_sources or any(count != 2 for count in Counter(ids).values()):
        raise ValueError("prediction rows must contain only the 20 held-out sources, twice each")
    labels = [str(row["label"]).strip().lower() for row in rows]
    if Counter(labels) != EXPECTED_COUNTS:
        raise ValueError("held-out rows must contain exactly 20 clean and 20 stego labels")
    for source_id in expected_sources:
        pair_rows = [row for row in rows if str(row["source_id"]) == source_id]
        pair_labels = [str(row["label"]).strip().lower() for row in pair_rows]
        if Counter(pair_labels) != {"clean": 1, "stego": 1}:
            raise ValueError(f"source {source_id} must have one clean and one stego row")
        metadata_row = next(row for row in heldout if row["source_id"] == source_id)
        filenames = {str(row["label"]).strip().lower(): row["filename"] for row in pair_rows}
        if filenames != {"clean": metadata_row["clean_filename"],
                         "stego": metadata_row["stego_filename"]}:
            raise ValueError(f"source {source_id} filenames do not match held-out metadata")

    config = summary.get("configuration", summary)
    weights = config.get("weights", config)
    if "chi_weight" not in weights:
        weights = {
            "chi_weight": weights.get("chi_square_weight"),
            "rs_weight": weights.get("rs_weight"),
            "dh_weight": weights.get("dh_weight"),
        }
    for key, expected in LOCKED_WEIGHTS.items():
        _close(weights.get(key), expected, key)
    _close(config.get("threshold"), LOCKED_THRESHOLD, "threshold")

    expected_predictions = []
    for index, row in enumerate(rows):
        raw_scores = {
            "chi_square": float(row["chi_square_score"]),
            "rs": float(row["rs_score"]),
            "dh": float(row["dh_score"]),
        }
        normalized = {
            "chi_square": normalize_chi_square(raw_scores["chi_square"]),
            "rs": normalize_rs(raw_scores["rs"]),
            "dh": normalize_dh(raw_scores["dh"]),
        }
        for key, official_key in (("normalized_chi", "chi_square"),
                                  ("normalized_rs", "rs"),
                                  ("normalized_dh", "dh")):
            _close(row[key], normalized[official_key], f"row {index} {key}")
        decision = combine_detector_scores(
            raw_scores,
            EnsembleConfig(chi_square_weight=0.0, rs_weight=0.70,
                           dh_weight=0.30, threshold=LOCKED_THRESHOLD),
        )
        score = float(decision["ensemble_score"])
        _close(row["ensemble_score"], score, f"row {index} ensemble_score")
        expected_predictions.append(
            "stego" if decision["label"] == "Suspicious" else "clean"
        )
    predictions = [str(row["prediction"]).strip().lower() for row in rows]
    if predictions != expected_predictions:
        raise ValueError("predictions do not match the locked threshold and official score direction")

    metrics = classification_metrics(labels, predictions)
    confusion = confusion_matrix_counts(labels, predictions)
    if sum(confusion.values()) != 40:
        raise ValueError("confusion-matrix counts must sum to 40")
    reported_metrics = summary.get("metrics", summary)
    reported_confusion = summary.get("confusion_matrix", summary)
    for key, value in metrics.items():
        _close(reported_metrics.get(key), value, key)
    official_names = {"tp": "true_positive", "tn": "true_negative",
                      "fp": "false_positive", "fn": "false_negative"}
    for key, value in confusion.items():
        _close(reported_confusion.get(key, reported_confusion.get(
            official_names[key], reported_confusion.get(key.upper()))), value, key)
    counts = summary.get("image_counts", {})
    if counts and counts != {"clean": 20, "stego": 20, "total": 40}:
        raise ValueError(f"reported image_counts mismatch: {counts}")
    if summary.get("evaluation_split", "held_out_test") != "held_out_test":
        raise ValueError("summary evaluation_split must be held_out_test")
    return {"sample_count": 40, "class_counts": dict(EXPECTED_COUNTS),
            "confusion_matrix": confusion, "metrics": metrics,
            "configuration": {"weights": LOCKED_WEIGHTS.copy(), "threshold": LOCKED_THRESHOLD}}


def verify_files(predictions_csv: Path, metrics_json: Path, metadata_csv: Path) -> dict[str, Any]:
    """Load the official artifacts and verify them without evaluating images."""
    with predictions_csv.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    with metadata_csv.open(newline="", encoding="utf-8") as handle:
        metadata = list(csv.DictReader(handle))
    with metrics_json.open(encoding="utf-8") as handle:
        summary = json.load(handle)
    return verify_heldout_results(rows, metadata, summary)


def main(argv: Sequence[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions", type=Path, default=Path("data/week11_heldout_predictions.csv"))
    parser.add_argument("--metrics", type=Path, default=Path("data/week11_heldout_metrics.json"))
    parser.add_argument("--metadata", type=Path, default=Path("data/metadata.csv"))
    args = parser.parse_args(argv)
    result = verify_files(args.predictions, args.metrics, args.metadata)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
