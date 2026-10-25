"""Create Week 10 validation calibration plots."""

import csv
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.ensemble.voting import (
    EQUAL_WEIGHT_BASELINE,
    combine_detector_scores,
)

from src.evaluation.grid_search_ensemble import (
    classification_metrics,
    score_calibration_images,
)

RESULT_PATH = Path("data/week10_grid_search_results.csv")

METADATA_PATH = Path("data/metadata.csv")

CLEAN_DIR = Path("dataset/clean")

STEGO_DIR = Path("dataset/stego")

OUTPUT_DIR = Path("docs/assets/week10-progress")

REQUIRED_RESULT_COLUMNS = {
    "selected",
    "chi_weight",
    "rs_weight",
    "dh_weight",
    "threshold",
    "validation_accuracy",
    "validation_precision",
    "validation_recall",
    "validation_f1",
    "validation_rows"
}


def load_grid_results(results_path):
    """Load and validate Week 10 grid-search results."""

    results_path = Path(results_path)

    if not results_path.exists():
        raise FileNotFoundError(
            f"Grid-search results do not exist: {results_path}"
        )

    with results_path.open(
        "r",
        newline = "",
        encoding = "utf-8",
    ) as handle:

        reader = csv.DictReader(handle)

        if reader.fieldnames is None:
            raise ValueError(
                "Grid-search results must contain a header row"
            )

        missing_columns = (
            REQUIRED_RESULT_COLUMNS
            - set(reader.fieldnames)
        )

        if missing_columns:
            raise ValueError(
                "Missing required plotting columns: "
                + ", ".join(sorted(missing_columns))
            )

        rows = list(reader)

    return rows


def find_selected_result(rows):
    """Return the one officially selected Week 10 configuration."""

    selected_rows = [
        row
        for row in rows
        if row["selected"].strip().lower() == "true"
    ]

    if len(selected_rows) != 1:
        raise ValueError(
            "Grid-search results must contain exactly one selected row"
        )

    return selected_rows[0]


def get_selected_weight_rows(rows, selected):
    """Return all threshold results for the selected weight combination."""

    selected_chi = float(selected["chi_weight"])

    selected_rs = float(selected["rs_weight"])

    selected_dh = float(selected["dh_weight"])

    matching_rows = [
        row
        for row in rows
        if math.isclose(
            float(row["chi_weight"]),
            selected_chi,
        )
        and math.isclose(
            float(row["rs_weight"]),
            selected_rs,
        )
        and math.isclose(
            float(row["dh_weight"]),
            selected_dh,
        )
    ]

    matching_rows.sort(
        key = lambda row: float(row["threshold"])
    )

    if not matching_rows:
        raise ValueError(
            "No threshold rows found for the selected weights"
        )

    return matching_rows


def plot_threshold_f1(
    rows,
    selected,
    output_path,
):
    """Plot validation F1 across thresholds for the selected weights."""

    selected_weight_rows = get_selected_weight_rows(
        rows,
        selected,
    )

    thresholds = [
        float(row["threshold"])
        for row in selected_weight_rows
    ]

    f1_scores = [
        float(row["validation_f1"])
        for row in selected_weight_rows
    ]

    selected_threshold = float(
        selected["threshold"]
    )

    selected_f1 = float(
        selected["validation_f1"]
    )

    validation_rows = int(
        selected["validation_rows"]
    )

    fig, ax = plt.subplots()

    ax.plot(
        thresholds,
        f1_scores,
        marker = "o",
    )

    ax.axvline(
        selected_threshold,
        linestyle = "--",
        label = f"Selected Threshold = {selected_threshold:.2f}",
    )

    ax.scatter(
        [selected_threshold],
        [selected_f1],
        label = "Selected Configuration",
    )

    ax.set_xlabel("Decision Threshold")

    ax.set_ylabel("Validation F1")

    ax.set_title(
        f"Validation F1 by Threshold\n"
        f"Validation split, n = {validation_rows}"
    )

    ax.set_ylim(0.0, 1.0)

    ax.legend()

    fig.tight_layout()

    fig.savefig(
        output_path,
        dpi = 150,
    )

    plt.close(fig)


def plot_threshold_accuracy(
    rows,
    selected,
    output_path,
):
    """Plot validation accuracy across thresholds for the selected weights."""

    selected_weight_rows = get_selected_weight_rows(
        rows,
        selected,
    )

    threshold = [
        float(row["threshold"])
        for row in selected_weight_rows
    ]

    accuracy_scores = [
        float(row["validation_accuracy"])
        for row in selected_weight_rows
    ]

    selected_threshold = float(
        selected["threshold"]
    )

    selected_accuracy = float(
        selected["validation_accuracy"]
    )

    validation_rows = int(
        selected["validation_rows"]
    )

    fig, ax = plt.subplots()

    ax.plot(
        threshold,
        accuracy_scores,
        marker = "o",
    )

    ax.axvline(
        selected_threshold,
        linestyle = "--",
        label = f"Selected Threshold = {selected_threshold:.2f}",
    )

    ax.scatter(
        [selected_threshold],
        [selected_accuracy],
        label = "Selected Configuration",
    )

    ax.set_xlabel("Decision Threshold")

    ax.set_ylabel("Validation Accuracy")

    ax.set_title(
        f"Validation Accuracy by Threshold\n"
        f"Validation split, n = {validation_rows}"
    )

    ax.set_ylim(0.0, 1.0)

    ax.legend()

    fig.tight_layout()

    fig.savefig(
        output_path,
        dpi = 150,
    )

    plt.close(fig)


def calculate_equal_weight_validation_metrics():
    """Evaluate the existing equal-weight baseline on validation data."""

    records = score_calibration_images(
        METADATA_PATH,
        CLEAN_DIR,
        STEGO_DIR,
    )

    validation_records = [
        record
        for record in records
        if record.split == "validation"
    ]

    true_labels = []
    predictions = []

    for record in validation_records:

        result = combine_detector_scores(
            record.scores,
            EQUAL_WEIGHT_BASELINE,
        )

        if result["label"] == "Suspicious":
            predicted_label = "stego"

        else:
            predicted_label = "clean"

        true_labels.append(
            record.label
        )

        predictions.append(
            predicted_label
        )

    metrics = classification_metrics(
            true_labels,
            predictions,
        )

    return metrics, len(validation_records)


def plot_baseline_vs_selected(
    baseline_metrics,
    selected,
    output_path,
):
    """Compare equal-weight baseline with selected Week 10 configuration."""

    metric_names = [
        "Accuracy",
        "Precision",
        "Recall",
        "F1",
    ]

    baseline_values = [
        baseline_metrics["accuracy"],
        baseline_metrics["precision"],
        baseline_metrics["recall"],
        baseline_metrics["f1"],
    ]

    selected_values = [
        float(selected["validation_accuracy"]),
        float(selected["validation_precision"]),
        float(selected["validation_recall"]),
        float(selected["validation_f1"]),
    ]

    positions = list(
        range(len(metric_names))
    )

    width = 0.35

    baseline_positions = [
        position - width / 2
        for position in positions
    ]

    selected_positions = [
        position + width / 2
        for position in positions
    ]

    fig, ax = plt.subplots()

    ax.bar(
        baseline_positions,
        baseline_values,
        width,
        label = "Equal-Weight Baseline",
    )

    ax.bar(
        selected_positions,
        selected_values,
        width,
        label = "Week 10 selected",
    )

    ax.set_xticks(positions)

    ax.set_xticklabels(metric_names)

    ax.set_ylabel("Validation Metric")

    ax.set_ylim(0.0, 1.0)

    ax.set_title(
        f"Equal-Weight Baseline vs Selected Configuration\n"
        f"Validation split, n = {selected['validation_rows']}"
    )

    ax.legend()

    fig.tight_layout()

    fig.savefig(
        output_path,
        dpi = 150,
    )

    plt.close(fig)


def main():
    """Generate Week 10 validation calibration plots."""

    OUTPUT_DIR.mkdir(
        parents = True,
        exist_ok = True,
    )

    rows = load_grid_results(
        RESULT_PATH
    )

    selected = find_selected_result(
        rows
    )

    plot_threshold_f1(
        rows,
        selected,
        OUTPUT_DIR / "validation_threshold_f1.png"
    )

    plot_threshold_accuracy(
        rows,
        selected,
        OUTPUT_DIR / "validation_threshold_accuracy.png"
    )

    baseline_metrics, validation_count = (
        calculate_equal_weight_validation_metrics()
    )

    expected_validation_count = int(
        selected["validation_rows"]
    )
    
    if validation_count != expected_validation_count:
        raise ValueError(
            "Baseline and selected configuration use different "
            "validation sample sizes"
        )

    plot_baseline_vs_selected(
        baseline_metrics,
        selected,
        OUTPUT_DIR / "baseline_vs_selected.png"
    )

    print(
        "Week 10 validation plots created."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())