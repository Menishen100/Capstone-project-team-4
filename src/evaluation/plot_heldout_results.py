"""Create Week 11 held-out ROC/AUC and confusion-matrix plots."""

import csv
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.metrics import (
    confusion_matrix,
    roc_auc_score,
    roc_curve,
)

RESULT_PATH = Path("data/week11_heldout_predictions.csv")

OUTPUT_DIR = Path("docs/assets/week11-progress")

EXPECTED_SPLIT = "held_out_test"
EXPECTED_ROWS = 40

REQUIRED_COLUMNS = {
    "source_id",
    "label",
    "split",
    "normalized_chi",
    "normalized_rs",
    "normalized_dh",
    "ensemble_score",
    "prediction",
}

POSITIVE_LABEL = "stego"


def load_heldout_results(results_path):
    """Load and validate Week 11 held-out results."""

    results_path = Path(results_path)

    if not results_path.exists():
        raise FileNotFoundError(
            f"Held-out results do not exist: {results_path}"
        )

    with results_path.open(
        "r",
        newline = "",
        encoding = "utf-8",
    ) as handle:

        reader = csv.DictReader(handle)

        if reader.fieldnames is None:
            raise ValueError(
                "Held-out results must contain a header row"
            )

        missing_columns = (
            REQUIRED_COLUMNS
            - set(reader.fieldnames)
        )

        if missing_columns:
            raise ValueError(
                "Missing required held-out columns: "
                + ", ".join(sorted(missing_columns))
            )

        rows = list(reader)

    if len(rows) != EXPECTED_ROWS:
        raise ValueError(
            f"Expected {EXPECTED_ROWS} held-out rows, "
            f"found {len(rows)}"
        )

    return validate_heldout_rows(rows)



def _read_score(row, column):
    """Return a valid finite score in [0, 1]."""

    value = row[column].strip()

    if not value:
        raise ValueError(
            f"Missing value for {column}"
        )

    try:
        score = float(value)
    except ValueError as exc:
        raise ValueError(
            f"{column} must be numeric"
        ) from exc

    if not math.isfinite(score):
        raise ValueError(
            f"{column} must be finite"
        )

    if not 0.0 <= score <= 1.0:
        raise ValueError(
            f"{column} must be in [0, 1]"
        )

    return score


def validate_heldout_rows(rows):
    """Validate Week 11 held-out labels, splits, predictions, and scores."""

    valid_labels = {
        "clean",
        "stego",
    }

    for row_number, row in enumerate(
        rows,
        start = 2,
    ):
        source_id = row["source_id"].strip()

        if not source_id:
            raise ValueError(
                f"Row {row_number}: source_id is missing"
            )

        split = row["split"].strip()

        if split != EXPECTED_SPLIT:
            raise ValueError(
                f"Row {row_number}: expected split "
                f"{EXPECTED_SPLIT}, found {split}"
            )

        label = row["label"].strip().lower()

        if label not in valid_labels:
            raise ValueError(
                f"Row {row_number}: invalid label {label}"
            )

        prediction = (
            row["prediction"]
            .strip()
            .lower()
        )

        if prediction not in valid_labels:
            raise ValueError(
                f"Row {row_number}: invalid prediction "
                f"{prediction}"
            )

        _read_score(
            row,
            "normalized_chi",
        )

        _read_score(
            row,
            "normalized_rs",
        )

        _read_score(
            row,
            "normalized_dh",
        )

        _read_score(
            row,
            "ensemble_score",
        )

    labels = {
        row["label"].strip().lower()
        for row in rows
    }

    if labels != {"clean", "stego"}:
        raise ValueError(
            "Held-out results must contain both clean and stego labels"
        )
    
    return rows


def get_binary_labels(rows):
    """Convert clean/stego labels into binary ROC labels."""

    return [
        1 if row["label"].strip().lower() == POSITIVE_LABEL else 0
        for row in rows
    ]


def get_score_values(rows, column):
    """Return validated continuous scores for one ROC input."""

    return [
        _read_score(row, column)
        for row in rows
    ]


def calculate_roc(rows, score_column):
    """Calculate ROC coordinates and AUC for one score column."""

    true_labels = get_binary_labels(rows)

    scores = get_score_values(
        rows,
        score_column,
    )

    fpr, tpr, thresholds = roc_curve(
        true_labels,
        scores,
    )

    auc_value = roc_auc_score(
        true_labels,
        scores,
    )

    return {
        "fpr": fpr,
        "tpr": tpr,
        "thresholds": thresholds,
        "auc": auc_value,
    }


def plot_ensemble_roc(rows, output_path):
    """Create the Week 11 held-out ensemble ROC curve."""

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents = True,
        exist_ok = True,
    )

    roc_data = calculate_roc(
        rows,
        "ensemble_score",
    )

    sample_count = len(rows)

    fig, ax = plt.subplots()

    ax.plot(
        roc_data["fpr"],
        roc_data["tpr"],
        marker = "o",
        label = f"Ensemble AUC = {roc_data['auc']:.4f}"
    )

    ax.plot(
        [0.0, 1.0],
        [0.0, 1.0],
        linestyle = "--",
        label = "Random Classifier",
    )

    ax.set_xlabel("False Positive Rate")

    ax.set_ylabel("True Positive Rate")

    ax.set_title(
        f"Held-Out Ensemble ROC Curve (n = {sample_count})"
    )

    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)

    ax.legend()

    fig.tight_layout()

    fig.savefig(
        output_path,
        dpi = 150,
    )

    plt.close(fig)


def plot_detector_roc_comparison(rows, output_path):
    """Compare held-out ROC curves for all detectors and the ensemble."""

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents = True,
        exist_ok = True,
    )

    chi_roc = calculate_roc(
        rows,
        "normalized_chi",
    )

    rs_roc = calculate_roc(
        rows,
        "normalized_rs",
    )

    dh_roc = calculate_roc(
        rows,
        "normalized_dh",
    )

    ensemble_roc = calculate_roc(
        rows,
        "ensemble_score",
    )

    sample_count = len(rows)

    fig, ax = plt.subplots()

    ax.plot(
        chi_roc["fpr"],
        chi_roc["tpr"],
        label = f"Chi-square (AUC = {chi_roc['auc']:.4f})"
    )

    ax.plot(
        rs_roc["fpr"],
        rs_roc["tpr"],
        label = f"RS (AUC = {rs_roc['auc']:.4f})"
        )

    ax.plot(
        dh_roc["fpr"],
        dh_roc["tpr"],
        label = f"DH (AUC = {dh_roc['auc']:.4f})"
        )

    ax.plot(
        ensemble_roc["fpr"],
        ensemble_roc["tpr"],
        label = f"Ensemble (AUC = {ensemble_roc['auc']:.4f})"
        )

    ax.plot(
        [0.0, 1.0],
        [0.0, 1.0],
        linestyle = "--",
        label = "Random Classifier",
    )

    ax.set_xlabel("False Positive Rate")

    ax.set_ylabel("True Positive Rate")

    ax.set_title(
        f"Held-Out Detector vs Ensemble ROC (n = {sample_count})"
    )

    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)

    ax.legend()

    fig.tight_layout()

    fig.savefig(
        output_path,
        dpi = 150,
    )

    plt.close(fig)


def get_binary_predictions(rows):
    """Convert clean/stego predictions into binary labels."""

    return [
        1 if row["prediction"].strip().lower() == POSITIVE_LABEL else 0
        for row in rows
    ]


def calculate_confusion_matrix(rows):
    """Calculate held-out TN, FP, FN, and TP counts."""

    true_labels = get_binary_labels(rows)
    predictions = get_binary_predictions(rows)

    matrix = confusion_matrix(
        true_labels,
        predictions,
        labels = [0, 1],
    )

    tn, fp, fn, tp = matrix.ravel()

    return {
       "matrix": matrix, 
       "tn": int(tn),
       "fp": int(fp),
       "fn": int(fn),
       "tp": int(tp), 
    }


def plot_ensemble_confusion_matrix(rows, output_path):
    """Create the Week 11 held-out ensemble confusion matrix."""

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents = True,
        exist_ok = True,
    )

    confusion = calculate_confusion_matrix(rows)

    matrix = confusion["matrix"]
    sample_count = len(rows)

    fig, ax = plt.subplots()

    image = ax.imshow(matrix)

    fig.colorbar(
        image,
        ax = ax,
    )

    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])

    ax.set_xticklabels([
        "Predicted Clean",
        "Predicted Stego"
    ])

    ax.set_yticklabels([
            "Actual Clean",
            "Actual Stego"
        ])

    cell_labels = [
        ["TN", "FP"],
        ["FN", "TP"],
    ]

    for row_index in range(2):
        for column_index in range(2):
            ax.text(
                column_index,
                row_index,
                (
                    f"{cell_labels[row_index][column_index]}\n"
                    f"{matrix[row_index, column_index]}"
                ),
                ha = "center",
                va = "center",
            )

    ax.set_title(
        f"Held-Out Ensemble Confusion Matrix (n = {sample_count})"
    )

    ax.set_xlabel("Predicted Label")
    
    ax.set_ylabel("Actual Label")

    fig.tight_layout()

    fig.savefig(
        output_path,
        dpi = 150,
    )

    plt.close(fig)


def main():
    """Generate Week 11 held-out evaluation plots and summary."""

    rows = load_heldout_results(
        RESULT_PATH
    )

    OUTPUT_DIR.mkdir(
        parents = True,
        exist_ok = True,
    )

    plot_ensemble_roc(
        rows,
        OUTPUT_DIR / "ensemble_roc.png"
    )

    plot_detector_roc_comparison(
        rows,
        OUTPUT_DIR / "detector_roc_comparison.png"
        )

    plot_ensemble_confusion_matrix(
        rows,
        OUTPUT_DIR / "ensemble_confusion_matrix.png"
        )

    chi_roc = calculate_roc(
        rows,
        "normalized_chi",
    )
    
    rs_roc = calculate_roc(
        rows,
        "normalized_rs",
    )
    
    dh_roc = calculate_roc(
        rows,
        "normalized_dh",
    )
    
    ensemble_roc = calculate_roc(
        rows,
        "ensemble_score",
    )

    confusion = calculate_confusion_matrix(rows)

    print("Week 11 held-out evaluation plots created.")
    print(f"Held-Out rows: {len(rows)}")

    print()
    print("AUC results:")
    print(
        f"Chi-square AUC: "
        f"{chi_roc['auc']:.4f}"
    )
    print(
        f"RS AUC: "
        f"{rs_roc['auc']:.4f}"
    )
    print(
        f"DH AUC: "
        f"{dh_roc['auc']:.4f}"
    )
    print(
        f"Ensemble AUC: "
        f"{ensemble_roc['auc']:.4f}"
    )

    print()
    print("Confusion matrix counts:")
    print(f"TN: {confusion['tn']}")
    print(f"FP: {confusion['fp']}")
    print(f"FN: {confusion['fn']}")
    print(f"TP: {confusion['tp']}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())