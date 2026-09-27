"""Tests for Menishen's Week 6 development-set scoring runner."""

import csv
from pathlib import Path

import numpy as np
from PIL import Image

from src.evaluation.run_preliminary_scores import development_pairs, run_preliminary_scores, summarize


class RecordingDetector:
    """Small deterministic detector used to verify runner orchestration."""

    def __init__(self, score, diagnostics):
        self.score = score
        self.diagnostics = diagnostics
        self.calls = 0

    def analyze(self, image):
        self.calls += 1
        return {"score": self.score, "diagnostics": self.diagnostics}


class FailingDetector:
    def analyze(self, image):
        raise ValueError("intentional test failure")


def write_metadata(path: Path) -> None:
    rows = [
        {"source_id": "source-development", "clean_filename": "dev_clean.png", "stego_filename": "dev_stego.png", "split": "development"},
        {"source_id": "source-validation", "clean_filename": "val_clean.png", "stego_filename": "val_stego.png", "split": "validation"},
        {"source_id": "source-held", "clean_filename": "test_clean.png", "stego_filename": "test_stego.png", "split": "held_out_test"},
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)


def save_image(path: Path) -> None:
    Image.fromarray(np.arange(16, dtype=np.uint8).reshape(4, 4), mode="L").save(path)


def test_runner_uses_only_development_pairs_and_records_all_detectors(tmp_path):
    metadata = tmp_path / "metadata.csv"
    clean = tmp_path / "clean"
    stego = tmp_path / "stego"
    output = tmp_path / "scores.csv"
    clean.mkdir()
    stego.mkdir()
    write_metadata(metadata)
    save_image(clean / "dev_clean.png")
    save_image(stego / "dev_stego.png")
    detectors = {
        "chi_square": RecordingDetector(0.1, {"p_value": 0.1}),
        "rs": RecordingDetector(0.2, {"rs_statistic": -0.2}),
        "dh": RecordingDetector(0.3, {"raw_roughness": 0.4}),
    }

    rows = run_preliminary_scores(metadata, clean, stego, output, detectors=detectors)

    assert [pair["source_id"] for pair in development_pairs(metadata)] == ["source-development"]
    assert len(rows) == 2
    assert {row["label"] for row in rows} == {"clean", "stego"}
    assert {row["split"] for row in rows} == {"development"}
    assert all(row["status"] == "complete" for row in rows)
    assert all(float(row[field]) in {0.1, 0.2, 0.3} for row in rows for field in ("chi_square_score", "rs_score", "dh_score"))
    assert all(row["chi_square_diagnostics"] and row["rs_diagnostics"] and row["dh_diagnostics"] for row in rows)
    assert all(detector.calls == 2 for detector in detectors.values())
    with output.open(newline="", encoding="utf-8") as handle:
        assert len(list(csv.DictReader(handle))) == 2


def test_runner_records_an_image_failure_and_continues(tmp_path):
    metadata = tmp_path / "metadata.csv"
    clean = tmp_path / "clean"
    stego = tmp_path / "stego"
    output = tmp_path / "scores.csv"
    clean.mkdir()
    stego.mkdir()
    write_metadata(metadata)
    save_image(clean / "dev_clean.png")
    # The stego image is intentionally absent.
    detectors = {
        "chi_square": RecordingDetector(0.1, {"p_value": 0.1}),
        "rs": RecordingDetector(0.2, {"rs_statistic": 0.2}),
        "dh": RecordingDetector(0.3, {"raw_roughness": 0.3}),
    }

    rows = run_preliminary_scores(metadata, clean, stego, output, detectors=detectors)

    assert rows[0]["status"] == "complete"
    assert rows[1]["status"] == "error"
    assert "image load: FileNotFoundError" in rows[1]["error"]
    assert len(list(csv.DictReader(output.open(newline="", encoding="utf-8")))) == 2


def test_runner_records_one_detector_failure_without_losing_other_scores(tmp_path):
    metadata = tmp_path / "metadata.csv"
    clean = tmp_path / "clean"
    stego = tmp_path / "stego"
    clean.mkdir()
    stego.mkdir()
    write_metadata(metadata)
    save_image(clean / "dev_clean.png")
    save_image(stego / "dev_stego.png")
    detectors = {
        "chi_square": RecordingDetector(0.1, {"p_value": 0.1}),
        "rs": FailingDetector(),
        "dh": RecordingDetector(0.3, {"raw_roughness": 0.3}),
    }

    rows = run_preliminary_scores(metadata, clean, stego, tmp_path / "scores.csv", detectors=detectors)

    assert all(row["status"] == "partial_error" for row in rows)
    assert all(row["chi_square_score"] == "0.1" and row["dh_score"] == "0.3" for row in rows)
    assert all(row["rs_score"] == "" and "rs: ValueError" in row["error"] for row in rows)
    assert summarize(rows) == {
        "clean_images_scored": 1,
        "stego_images_scored": 1,
        "total_images_scored": 2,
        "chi_square_errors": 0,
        "rs_errors": 2,
        "dh_errors": 0,
    }
