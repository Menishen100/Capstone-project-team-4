"""Tests for Menishen's Week 10 reproducible ensemble calibration runner."""

import csv
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from src.evaluation.grid_search_ensemble import (
    ScoredImage,
    classification_metrics,
    format_selected_result,
    grid_search,
    score_calibration_images,
    threshold_grid,
    weight_grid,
    write_results,
)


def record(source_id, split, label, chi, rs, dh):
    return ScoredImage(source_id, split, label, chi, rs, dh)


def calibration_rows():
    return [
        record("dev-1", "development", "clean", 0.10, 0.90, 0.90),
        record("dev-1", "development", "stego", 0.90, 0.10, 0.10),
        record("val-1", "validation", "clean", 0.10, 0.90, 0.90),
        record("val-1", "validation", "stego", 0.90, 0.10, 0.10),
    ]


class RecordingDetector:
    def __init__(self, score):
        self.score = score
        self.calls = 0

    def analyze(self, image):
        self.calls += 1
        return {"score": self.score, "diagnostics": {}}


def _save_image(path: Path) -> None:
    Image.fromarray(np.arange(16, dtype=np.uint8).reshape(4, 4), mode="L").save(path)


def test_documented_weight_grid_has_only_normalized_weights():
    candidates = weight_grid()
    assert len(candidates) == 66
    assert all(sum(weights) == pytest.approx(1.0) for weights in candidates)
    assert all(all(weight >= 0.0 for weight in weights) for weights in candidates)


def test_documented_threshold_grid_is_reproducible_and_inclusive():
    assert threshold_grid() == pytest.approx((0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70))


def test_metrics_use_stego_as_positive_class():
    metrics = classification_metrics(
        ["clean", "stego", "stego", "clean"],
        ["clean", "stego", "clean", "clean"],
    )
    assert metrics == pytest.approx({"accuracy": 0.75, "precision": 1.0, "recall": 0.5, "f1": 2.0 / 3.0})


def test_grid_search_selects_from_validation_and_marks_exactly_one_result():
    results = grid_search(calibration_rows())
    assert len(results) == 66 * 9
    assert results[0]["rank"] == 1
    assert results[0]["selected"] is True
    assert sum(row["selected"] is True for row in results) == 1
    assert {row["development_rows"] for row in results} == {2}
    assert {row["validation_rows"] for row in results} == {2}
    assert all(sum(row[key] for key in ("chi_weight", "rs_weight", "dh_weight")) == pytest.approx(1.0) for row in results)


def test_scored_image_rejects_held_out_rows():
    with pytest.raises(ValueError, match="development or validation"):
        record("held-1", "held_out_test", "clean", 0.1, 0.9, 0.9)


def test_image_scoring_reads_development_and_validation_but_not_held_out(tmp_path):
    metadata = tmp_path / "metadata.csv"
    clean = tmp_path / "clean"
    stego = tmp_path / "stego"
    clean.mkdir()
    stego.mkdir()
    rows = [
        {"source_id": "dev", "clean_filename": "dev_clean.png", "stego_filename": "dev_stego.png", "split": "development"},
        {"source_id": "validation", "clean_filename": "val_clean.png", "stego_filename": "val_stego.png", "split": "validation"},
        {"source_id": "held", "clean_filename": "missing_clean.png", "stego_filename": "missing_stego.png", "split": "held_out_test"},
    ]
    with metadata.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)
    for filename in ("dev_clean.png", "val_clean.png"):
        _save_image(clean / filename)
    for filename in ("dev_stego.png", "val_stego.png"):
        _save_image(stego / filename)
    detectors = {name: RecordingDetector(0.25) for name in ("chi_square", "rs", "dh")}

    scored = score_calibration_images(metadata, clean, stego, detectors=detectors)

    assert len(scored) == 4
    assert {row.split for row in scored} == {"development", "validation"}
    assert all(detector.calls == 4 for detector in detectors.values())


def test_results_csv_and_display_text_include_selected_validation_details(tmp_path):
    results = grid_search(calibration_rows())
    output = tmp_path / "results.csv"
    write_results(results, output)
    with output.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 66 * 9
    assert rows[0]["selected"] == "True"
    text = format_selected_result(results[0])
    assert "Validation F1:" in text
    assert "Held-out test rows used: 0" in text
