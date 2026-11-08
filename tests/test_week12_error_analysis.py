"""Tests for the read-only Week 12 error case analyzer."""

import csv
from pathlib import Path

import pytest

from src.evaluation.analyze_week12_errors import (
    analyze_rows,
    classify_cell,
    read_predictions,
    write_error_cases,
)


def _row(label="stego", prediction="clean", source_id="s1", score="0.65"):
    return {
        "source_id": source_id, "label": label, "prediction": prediction,
        "chi_square_score": "0.2", "rs_score": "0.4", "dh_score": "0.5",
        "normalized_chi": "0.2", "normalized_rs": "0.6", "normalized_dh": "0.5",
        "ensemble_score": score,
    }


@pytest.mark.parametrize(("label", "prediction", "expected"), [
    ("stego", "stego", "true_positive"), ("clean", "clean", "true_negative"),
    ("clean", "stego", "false_positive"), ("stego", "clean", "false_negative"),
])
def test_all_confusion_cells_are_classified(label, prediction, expected):
    assert classify_cell(label, prediction) == expected


def test_error_rows_keep_detector_scores_and_signed_distance():
    groups, errors = analyze_rows([
        _row(score="0.65", source_id="fn"),
        _row(label="clean", prediction="stego", score="0.73", source_id="fp"),
        _row(label="stego", prediction="stego", source_id="tp"),
        _row(label="clean", prediction="clean", source_id="tn"),
    ])
    assert [len(groups[name]) for name in ("true_positive", "true_negative", "false_positive", "false_negative")] == [1, 1, 1, 1]
    assert [(row["source_id"], row["error_type"]) for row in errors] == [("fn", "false_negative"), ("fp", "false_positive")]
    assert errors[0]["distance_from_threshold"] == pytest.approx(-0.05)
    assert errors[1]["distance_from_threshold"] == pytest.approx(0.03)
    assert errors[0]["normalized_rs"] == "0.6"


def test_writer_emits_stable_error_case_schema(tmp_path):
    _, errors = analyze_rows([_row()])
    output = tmp_path / "cases.csv"
    write_error_cases(output, errors)
    with output.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        row = next(reader)
        assert reader.fieldnames == ["source_id", "label", "prediction", "error_type", "chi_square_score", "rs_score", "dh_score", "normalized_chi", "normalized_rs", "normalized_dh", "ensemble_score", "distance_from_threshold"]
    assert row["error_type"] == "false_negative"


def test_reader_rejects_missing_numeric_values(tmp_path):
    path = tmp_path / "bad.csv"
    fields = list(_row())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        bad = _row()
        bad["rs_score"] = "NaN"
        writer.writerow(bad)
    with pytest.raises(ValueError, match="must be finite"):
        read_predictions(path)
