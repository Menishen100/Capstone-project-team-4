"""Tests for Week 10 validation calibration plotting."""

import csv
from types import SimpleNamespace

import pytest

from src.evaluation import plot_calibration
from src.evaluation.plot_calibration import (
    calculate_equal_weight_validation_metrics,
    find_selected_result,
    get_selected_weight_rows,
    load_grid_results,
    plot_baseline_vs_selected,
    plot_threshold_accuracy,
    plot_threshold_f1,
)

FIELDNAMES = [
    "selected",
    "chi_weight",
    "rs_weight",
    "dh_weight",
    "threshold",
    "validation_accuracy",
    "validation_precision",
    "validation_recall",
    "validation_f1",
    "validation_rows",
]


def _valid_grid_rows():
    """Return sample grid-search rows for the selected weight combination."""

    return [
        {
            "selected": "False",
            "chi_weight": "0.0",
            "rs_weight": "0.7",
            "dh_weight": "0.3",
            "threshold": "0.60",
            "validation_accuracy": "0.70",
            "validation_precision": "0.68",
            "validation_recall": "0.75",
            "validation_f1": "0.71",
            "validation_rows": "40",
        },
        {
            "selected": "False",
            "chi_weight": "0.0",
            "rs_weight": "0.7",
            "dh_weight": "0.3",
            "threshold": "0.65",
            "validation_accuracy": "0.725",
            "validation_precision": "0.70",
            "validation_recall": "0.78",
            "validation_f1": "0.738",
            "validation_rows": "40",
        },
        {
            "selected": "True",
            "chi_weight": "0.0",
            "rs_weight": "0.7",
            "dh_weight": "0.3",
            "threshold": "0.70",
            "validation_accuracy": "0.75",
            "validation_precision": "0.7273",
            "validation_recall": "0.80",
            "validation_f1": "0.7619",
            "validation_rows": "40",
        },
        {
            "selected": "False",
            "chi_weight": "0.2",
            "rs_weight": "0.5",
            "dh_weight": "0.3",
            "threshold": "0.70",
            "validation_accuracy": "0.65",
            "validation_precision": "0.64",
            "validation_recall": "0.70",
            "validation_f1": "0.67",
            "validation_rows": "40",
        },
    ]


def _write_grid_csv(
    tmp_path,
    rows,
    fieldnames=FIELDNAMES,
):
    """Write temporary Week 10 grid-search results."""

    results_path = tmp_path / "week10_grid_search_results.csv"

    with results_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:

        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)

    return results_path


def test_load_grid_results_accepts_valid_csv(tmp_path):
    rows = _valid_grid_rows()

    results_path = _write_grid_csv(
        tmp_path,
        rows,
    )

    loaded_rows = load_grid_results(
        results_path
    )

    assert len(loaded_rows) == 4


def test_load_grid_results_rejects_missing_column(tmp_path):
    rows = _valid_grid_rows()

    fieldnames = [
        column
        for column in FIELDNAMES
        if column != "validation_f1"
    ]

    rows_without_f1 = []

    for row in rows:
        new_row = row.copy()
        new_row.pop("validation_f1")
        rows_without_f1.append(new_row)

    results_path = _write_grid_csv(
        tmp_path,
        rows_without_f1,
        fieldnames=fieldnames,
    )

    with pytest.raises(
        ValueError,
        match="Missing required plotting columns",
    ):
        load_grid_results(results_path)


def test_find_selected_result_returns_official_selection():
    rows = _valid_grid_rows()

    selected = find_selected_result(
        rows
    )

    assert selected["selected"] == "True"
    assert float(selected["chi_weight"]) == 0.0
    assert float(selected["rs_weight"]) == 0.7
    assert float(selected["dh_weight"]) == 0.3
    assert float(selected["threshold"]) == 0.70


def test_multiple_selected_rows_are_rejected():
    rows = _valid_grid_rows()

    rows[0]["selected"] = "True"

    with pytest.raises(
        ValueError,
        match="exactly one selected row",
    ):
        find_selected_result(rows)


def test_selected_weight_rows_are_filtered_and_sorted():
    rows = _valid_grid_rows()

    selected = find_selected_result(
        rows
    )

    matching_rows = get_selected_weight_rows(
        rows,
        selected,
    )

    thresholds = [
        float(row["threshold"])
        for row in matching_rows
    ]

    assert thresholds == [
        0.60,
        0.65,
        0.70,
    ]

    assert all(
        float(row["chi_weight"]) == 0.0
        for row in matching_rows
    )

    assert all(
        float(row["rs_weight"]) == 0.7
        for row in matching_rows
    )

    assert all(
        float(row["dh_weight"]) == 0.3
        for row in matching_rows
    )


def test_threshold_f1_plot_is_created(tmp_path):
    rows = _valid_grid_rows()

    selected = find_selected_result(
        rows
    )

    output_path = (
        tmp_path
        / "validation_threshold_f1.png"
    )

    plot_threshold_f1(
        rows,
        selected,
        output_path,
    )

    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_threshold_accuracy_plot_is_created(tmp_path):
    rows = _valid_grid_rows()

    selected = find_selected_result(
        rows
    )

    output_path = (
        tmp_path
        / "validation_threshold_accuracy.png"
    )

    plot_threshold_accuracy(
        rows,
        selected,
        output_path,
    )

    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_baseline_vs_selected_plot_is_created(tmp_path):
    rows = _valid_grid_rows()

    selected = find_selected_result(
        rows
    )

    baseline_metrics = {
        "accuracy": 0.60,
        "precision": 0.58,
        "recall": 0.65,
        "f1": 0.61,
    }

    output_path = (
        tmp_path
        / "baseline_vs_selected.png"
    )

    plot_baseline_vs_selected(
        baseline_metrics,
        selected,
        output_path,
    )

    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_equal_weight_metrics_use_validation_only(
    monkeypatch,
):
    fake_records = [
        SimpleNamespace(
            split="development",
            label="clean",
            scores={"fake": "development"},
        ),
        SimpleNamespace(
            split="validation",
            label="clean",
            scores={"fake": "validation-clean"},
        ),
        SimpleNamespace(
            split="validation",
            label="stego",
            scores={"fake": "validation-stego"},
        ),
        SimpleNamespace(
            split="held_out_test",
            label="stego",
            scores={"fake": "held-out"},
        ),
    ]

    monkeypatch.setattr(
        plot_calibration,
        "score_calibration_images",
        lambda *args, **kwargs: fake_records,
    )

    def fake_combine(scores, config):
        if scores["fake"] == "validation-stego":
            return {
                "label": "Suspicious"
            }

        return {
            "label": "Clean"
        }

    monkeypatch.setattr(
        plot_calibration,
        "combine_detector_scores",
        fake_combine,
    )

    captured = {}

    def fake_metrics(
        true_labels,
        predictions,
    ):
        captured["true_labels"] = true_labels
        captured["predictions"] = predictions

        return {
            "accuracy": 1.0,
            "precision": 1.0,
            "recall": 1.0,
            "f1": 1.0,
        }

    monkeypatch.setattr(
        plot_calibration,
        "classification_metrics",
        fake_metrics,
    )

    metrics, validation_count = (
        calculate_equal_weight_validation_metrics()
    )

    assert validation_count == 2

    assert captured["true_labels"] == [
        "clean",
        "stego",
    ]

    assert captured["predictions"] == [
        "clean",
        "stego",
    ]

    assert metrics["accuracy"] == 1.0
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["f1"] == 1.0
    