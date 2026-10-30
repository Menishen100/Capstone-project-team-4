"""Tests for Menishen's locked Week 11 held-out evaluation runner."""

import csv
import json
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from src.evaluation.run_heldout_evaluation import (
    HELD_OUT_SPLIT,
    LOCKED_CONFIG,
    PREDICTION_COLUMNS,
    evaluate_heldout_pairs,
    format_summary,
    heldout_pairs,
    metrics_summary,
    run_heldout_evaluation,
)


class FixedDetector:
    """Return a bounded score while counting calls."""

    def __init__(self, score: float) -> None:
        self.score = score
        self.calls = 0

    def analyze(self, image):
        self.calls += 1
        return {"score": self.score, "diagnostics": {}}


def _save_image(path: Path) -> None:
    Image.fromarray(np.arange(16, dtype=np.uint8).reshape(4, 4), mode="L").save(path)


def _write_metadata(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("source_id", "clean_filename", "stego_filename", "split"))
        writer.writeheader()
        writer.writerows(rows)


def _fixture_dataset(tmp_path: Path) -> tuple[Path, Path, Path, list[dict[str, str]]]:
    metadata = tmp_path / "metadata.csv"
    clean = tmp_path / "clean"
    stego = tmp_path / "stego"
    clean.mkdir()
    stego.mkdir()
    pairs = [
        {"source_id": "held-002", "clean_filename": "c2.png", "stego_filename": "s2.png", "split": HELD_OUT_SPLIT},
        {"source_id": "held-001", "clean_filename": "c1.png", "stego_filename": "s1.png", "split": HELD_OUT_SPLIT},
        {"source_id": "development", "clean_filename": "missing.png", "stego_filename": "missing.png", "split": "development"},
    ]
    _write_metadata(metadata, pairs)
    for filename in ("c1.png", "c2.png"):
        _save_image(clean / filename)
    for filename in ("s1.png", "s2.png"):
        _save_image(stego / filename)
    return metadata, clean, stego, pairs


def _detectors() -> dict[str, FixedDetector]:
    # RS and DH are inverted by the official ensemble boundary, producing 0.8.
    return {name: FixedDetector(0.2) for name in ("chi_square", "rs", "dh")}


def test_locked_configuration_matches_week10_selection():
    assert LOCKED_CONFIG.weights == pytest.approx((0.0, 0.7, 0.3))
    assert LOCKED_CONFIG.threshold == pytest.approx(0.70)


def test_heldout_pairs_read_only_heldout_rows_and_sort_by_source(tmp_path):
    metadata, _, _, _ = _fixture_dataset(tmp_path)
    pairs = heldout_pairs(metadata, expected_pair_count=2)
    assert [pair["source_id"] for pair in pairs] == ["held-001", "held-002"]
    assert all(pair["split"] == HELD_OUT_SPLIT for pair in pairs)


def test_heldout_pairs_require_expected_pair_count(tmp_path):
    metadata, _, _, _ = _fixture_dataset(tmp_path)
    with pytest.raises(ValueError, match="exactly 3 source pairs"):
        heldout_pairs(metadata, expected_pair_count=3)


def test_evaluation_uses_locked_boundary_and_writes_required_prediction_fields(tmp_path):
    metadata, clean, stego, _ = _fixture_dataset(tmp_path)
    pairs = heldout_pairs(metadata, expected_pair_count=2)
    detectors = _detectors()
    rows = evaluate_heldout_pairs(pairs, clean, stego, detectors=detectors)

    assert len(rows) == 4
    assert all(row["split"] == HELD_OUT_SPLIT for row in rows)
    assert all(float(row["ensemble_score"]) == pytest.approx(0.8) for row in rows)
    assert all(row["prediction"] == "stego" for row in rows)
    assert set(rows[0]) == set(PREDICTION_COLUMNS)
    assert all(detector.calls == 4 for detector in detectors.values())


def test_metrics_report_confusion_counts_and_final_scores():
    rows = [
        {"label": "clean", "prediction": "clean", "split": HELD_OUT_SPLIT},
        {"label": "clean", "prediction": "stego", "split": HELD_OUT_SPLIT},
        {"label": "stego", "prediction": "clean", "split": HELD_OUT_SPLIT},
        {"label": "stego", "prediction": "stego", "split": HELD_OUT_SPLIT},
    ]
    summary = metrics_summary(rows)
    assert summary["confusion_matrix"] == {
        "true_positive": 1,
        "true_negative": 1,
        "false_positive": 1,
        "false_negative": 1,
    }
    assert summary["metrics"] == pytest.approx({"accuracy": 0.5, "precision": 0.5, "recall": 0.5, "f1": 0.5})


def test_metrics_reject_non_heldout_rows():
    with pytest.raises(ValueError, match="held_out_test"):
        metrics_summary([
            {"label": "clean", "prediction": "clean", "split": "validation"},
            {"label": "stego", "prediction": "stego", "split": "validation"},
        ])


def test_runner_writes_results_once_and_refuses_overwrite(tmp_path):
    metadata, clean, stego, _ = _fixture_dataset(tmp_path)
    predictions = tmp_path / "predictions.csv"
    metrics = tmp_path / "metrics.json"
    rows, summary = run_heldout_evaluation(
        metadata, clean, stego, predictions, metrics, detectors=_detectors(), expected_pair_count=2
    )
    with predictions.open(newline="", encoding="utf-8") as handle:
        written_rows = list(csv.DictReader(handle))
    assert len(written_rows) == len(rows) == 4
    assert set(written_rows[0]) == set(PREDICTION_COLUMNS)
    assert json.loads(metrics.read_text(encoding="utf-8")) == summary
    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        run_heldout_evaluation(
            metadata, clean, stego, predictions, metrics, detectors=_detectors(), expected_pair_count=2
        )


def test_summary_states_locked_configuration_and_final_metrics():
    summary = metrics_summary([
        {"label": "clean", "prediction": "clean", "split": HELD_OUT_SPLIT},
        {"label": "stego", "prediction": "stego", "split": HELD_OUT_SPLIT},
    ])
    output = format_summary(summary)
    assert "Chi-square=0.00, RS=0.70, DH=0.30, threshold=0.70" in output
    assert "TP=1, TN=1, FP=0, FN=0" in output
