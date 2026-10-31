"""Tests for Week 11 held-out ROC/AUC and confusion-matrix plotting."""

import csv
import matplotlib.axes
import pytest

from src.evaluation.plot_heldout_results import (
    calculate_confusion_matrix,
    calculate_roc,
    get_binary_labels,
    load_heldout_results,
    plot_detector_roc_comparison,
    plot_ensemble_confusion_matrix,
    plot_ensemble_roc,
)

FIELDNAMES = [
    "source_id",
    "label",
    "split",
    "normalized_chi",
    "normalized_rs",
    "normalized_dh",
    "ensemble_score",
    "prediction",
]


def _make_row(
    index,
    label,
    prediction,
    ensemble_score,
    chi_score = "0.20",
    rs_score = "0.30",
    dh_score = "0.40",
    split = "held_out_test",
):
    """Create one synthetic held-out result row."""

    return {
        "source_id": f"source-{index:03d}",
        "label": label,
        "split": split,
        "normalized_chi": chi_score,
        "normalized_rs": rs_score,
        "normalized_dh": dh_score,
        "ensemble_score": ensemble_score,
        "prediction": prediction,
    }


def _small_valid_rows():
    """Return a small valid dataset containing both classes."""

    return [
        _make_row(
            1,
            "clean",
            "clean",
            "0.20",
            chi_score = "0.10",
            rs_score = "0.20",
            dh_score = "0.30",
        ),
        _make_row(
            2,
            "clean",
            "stego",
            "0.40",
            chi_score = "0.30",
            rs_score = "0.40",
            dh_score = "0.45",
        ),
        _make_row(
            3,
            "stego",
            "clean",
            "0.70",
            chi_score = "0.60",
            rs_score = "0.70",
            dh_score = "0.65",
        ),
        _make_row(
            4,
            "stego",
            "stego",
            "0.90",
            chi_score = "0.90",
            rs_score = "0.85",
            dh_score = "0.80",
        ),
    ]


def _valid_40_rows():
    """Return 20 synthetic clean and 20 synthetic stego rows."""

    rows = []

    for index in range(1, 21):
        rows.append(
            _make_row(
                index,
                "clean",
                "clean",
                "0.20",
            )
        )

    for index in range(21, 41):
        rows.append(
            _make_row(
                index,
                "stego",
                "stego",
                "0.80",
            )
        )

    return rows


def _write_results_csv(
    tmp_path,
    rows,
    fieldnames = FIELDNAMES,
):
    """Write temporary Week 11 held-out results."""

    results_path = (
        tmp_path
        / "week11_heldout_predictions.csv"
    )

    with results_path.open(
        "w",
        newline = "",
        encoding = "utf-8",
    ) as handle:

        writer = csv.DictWriter(
            handle,
            fieldnames = fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)

    return results_path


def test_load_heldout_results_accepts_valid_file(tmp_path):
    rows = _valid_40_rows()

    results_path = _write_results_csv(
        tmp_path,
        rows,
    )

    loaded_rows = load_heldout_results(
        results_path
    )

    assert len(loaded_rows) == 40

    assert all(
        row["split"] == "held_out_test"
        for row in loaded_rows
    )


def test_load_heldout_results_rejects_non_heldout_row(
    tmp_path,
):
    rows = _valid_40_rows()

    rows[0]["split"] = "validation"

    results_path = _write_results_csv(
        tmp_path,
        rows,
    )

    with pytest.raises(
        ValueError,
        match="expected split held_out_test",
    ):
        load_heldout_results(results_path)


def test_load_heldout_results_requires_40_rows(
    tmp_path,
):
    rows = _valid_40_rows()[:-1]

    results_path = _write_results_csv(
        tmp_path,
        rows,
    )

    with pytest.raises(
        ValueError,
        match="Expected 40 held-out rows",
    ):
        load_heldout_results(results_path)


def test_binary_labels_map_clean_and_stego_correctly():
    rows = [
        _make_row(
            1,
            "clean",
            "clean",
            "0.20",
        ),
        _make_row(
            2,
            "stego",
            "stego",
            "0.80",
        ),
    ]

    labels = get_binary_labels(rows)

    assert labels == [0, 1]


def test_calculate_roc_returns_bounded_auc():
    rows = _small_valid_rows()

    roc_data = calculate_roc(
        rows,
        "ensemble_score",
    )

    assert 0.0 <= roc_data["auc"] <= 1.0
    assert roc_data["auc"] == pytest.approx(1.0)

    assert len(roc_data["fpr"]) > 0
    assert len(roc_data["tpr"]) > 0
    assert len(roc_data["thresholds"]) > 0


def test_confusion_matrix_counts_are_correct():
    rows = _small_valid_rows()

    confusion = calculate_confusion_matrix(
        rows
    )

    assert confusion["tn"] == 1
    assert confusion["fp"] == 1
    assert confusion["fn"] == 1
    assert confusion["tp"] == 1

    assert confusion["matrix"].sum() == len(rows)


def test_confusion_matrix_uses_official_predictions():
    rows = [
        _make_row(
            1,
            "clean",
            "stego",
            "0.10",
        ),
        _make_row(
            2,
            "stego",
            "clean",
            "0.90",
        ),
    ]

    confusion = calculate_confusion_matrix(
        rows
    )

    assert confusion["tn"] == 0
    assert confusion["fp"] == 1
    assert confusion["fn"] == 1
    assert confusion["tp"] == 0


@pytest.mark.parametrize(
    ("plot_function", "filename"),
    [
        (
            plot_ensemble_roc,
            "ensemble_roc.png",
        ),
        (
            plot_detector_roc_comparison,
            "detector_roc_comparison.png",
        ),
        (
            plot_ensemble_confusion_matrix,
            "ensemble_confusion_matrix.png",
        ),
    ],
)
def test_plot_file_is_created(
    tmp_path,
    plot_function,
    filename,
):
    rows = _small_valid_rows()

    output_path = tmp_path / filename

    plot_function(
        rows,
        output_path,
    )

    assert output_path.exists()
    assert output_path.stat().st_size > 0


@pytest.mark.parametrize(
    ("plot_function", "expected_title"),
    [
        (
            plot_ensemble_roc,
            "Held-Out Ensemble ROC Curve",
        ),
        (
            plot_detector_roc_comparison,
            "Held-Out Detector vs Ensemble ROC",
        ),
        (
            plot_ensemble_confusion_matrix,
            "Held-Out Ensemble Confusion Matrix",
        ),
    ],
)
def test_plot_title_contains_split_and_sample_count(
    tmp_path,
    monkeypatch,
    plot_function,
    expected_title,
):
    rows = _small_valid_rows()

    captured_titles = []

    original_set_title = matplotlib.axes.Axes.set_title

    def capture_title(
        self,
        label,
        *args,
        **kwargs,
    ):
        captured_titles.append(label)

        return original_set_title(
            self,
            label,
            *args,
            **kwargs,
        )

    monkeypatch.setattr(
        matplotlib.axes.Axes,
        "set_title",
        capture_title,
    )

    output_path = tmp_path / "test_plot.png"

    plot_function(
        rows,
        output_path,
    )

    assert len(captured_titles) == 1

    title = captured_titles[0]

    assert expected_title in title
    assert "n = 4" in title