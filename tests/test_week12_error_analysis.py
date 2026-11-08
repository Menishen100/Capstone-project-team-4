"""Tests for the descriptive Week 12 error-analysis workflow."""

import csv
from pathlib import Path

import pytest

from src.evaluation.analyze_week12_errors import (
    ERROR_CASE_COLUMNS,
    HELD_OUT_SPLIT,
    build_error_cases,
    case_type,
    classify_cases,
    format_summary,
    load_official_predictions,
    summarize_cases,
    write_error_cases,
)


def _row(source_id: str, label: str, prediction: str, score: float) -> dict[str, str]:
    return {
        "source_id": source_id,
        "label": label,
        "filename": f"{source_id}_{label}.png",
        "split": HELD_OUT_SPLIT,
        "chi_square_score": "0.20",
        "rs_score": "0.30",
        "dh_score": "0.40",
        "normalized_chi": "0.20",
        "normalized_rs": "0.70",
        "normalized_dh": "0.60",
        "ensemble_score": str(score),
        "prediction": prediction,
        "correct": str(label == prediction),
    }


def _official_shape_rows() -> list[dict[str, str]]:
    rows = []
    for index in range(20):
        source = f"source-{index:03d}"
        clean_prediction = "stego" if index < 4 else "clean"
        stego_prediction = "clean" if index < 11 else "stego"
        rows.extend((
            _row(source, "clean", clean_prediction, 0.71 if index < 4 else 0.20),
            _row(source, "stego", stego_prediction, 0.69 if index < 11 else 0.80),
        ))
    return rows


def _write_predictions(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def test_load_requires_complete_paired_heldout_population(tmp_path):
    predictions = tmp_path / "predictions.csv"
    expected = _official_shape_rows()
    _write_predictions(predictions, expected)

    actual = load_official_predictions(predictions)

    assert actual == sorted(expected, key=lambda row: (row["source_id"], row["label"]))


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda rows: rows.pop(), "exactly 40 prediction rows"),
        (lambda rows: rows.__setitem__(0, {**rows[0], "split": "validation"}), "held_out_test"),
        (lambda rows: rows.__setitem__(0, {**rows[0], "ensemble_score": "1.1"}), "ensemble_score"),
        (lambda rows: rows.__setitem__(0, {**rows[0], "source_id": ""}), "empty source_id"),
    ],
)
def test_load_rejects_non_official_or_invalid_rows(tmp_path, change, message):
    predictions = tmp_path / "predictions.csv"
    rows = _official_shape_rows()
    change(rows)
    _write_predictions(predictions, rows)

    with pytest.raises(ValueError, match=message):
        load_official_predictions(predictions)


def test_case_types_and_error_csv_include_only_fp_and_fn(tmp_path):
    rows = [
        _row("a", "stego", "stego", 0.80),
        _row("b", "clean", "clean", 0.20),
        _row("c", "clean", "stego", 0.72),
        _row("d", "stego", "clean", 0.68),
    ]

    assert [case_type(row) for row in rows] == ["true_positive", "true_negative", "false_positive", "false_negative"]
    cases = build_error_cases(rows)
    assert [case["error_type"] for case in cases] == ["false_negative", "false_positive"]
    assert float(cases[0]["distance_from_threshold"]) == pytest.approx(-0.02)
    assert float(cases[1]["distance_from_threshold"]) == pytest.approx(0.02)

    output = tmp_path / "errors.csv"
    write_error_cases(cases, output)
    with output.open(newline="", encoding="utf-8") as handle:
        written = list(csv.DictReader(handle))
    assert list(written[0]) == list(ERROR_CASE_COLUMNS)
    assert written == cases


def test_summary_reports_observed_counts_and_detector_means_without_retuning():
    rows = [
        _row("tp", "stego", "stego", 0.80),
        _row("tn", "clean", "clean", 0.20),
        _row("fp", "clean", "stego", 0.71),
        _row("fn", "stego", "clean", 0.69),
    ]
    summary = summarize_cases(rows)
    output = format_summary(summary, build_error_cases(rows))

    assert summary["case_counts"] == {
        "true_positive": 1,
        "true_negative": 1,
        "false_positive": 1,
        "false_negative": 1,
    }
    assert summary["mean_scores"]["false_negative"]["normalized_rs"] == pytest.approx(0.70)
    assert "False-positive source IDs: fp" in output
    assert "False-negative source IDs: fn" in output
    assert "No weights, threshold, preprocessing, detector behavior, predictions, or Week 11 metrics were changed." in output


def test_classification_rejects_invalid_labels():
    with pytest.raises(ValueError, match="clean/stego"):
        case_type(_row("bad", "clean", "unknown", 0.4))


def test_official_week11_error_population_is_preserved():
    rows = load_official_predictions(Path("data/week11_heldout_predictions.csv"))
    cases = build_error_cases(rows)

    assert [case["source_id"] for case in cases if case["error_type"] == "false_positive"] == [
        "source-083", "source-084", "source-088", "source-096",
    ]
    assert [case["source_id"] for case in cases if case["error_type"] == "false_negative"] == [
        "source-081", "source-082", "source-085", "source-090", "source-091",
        "source-092", "source-094", "source-097", "source-098", "source-099",
        "source-100",
    ]
