"""Analyze Week 11 DH error cases for Week 12."""

import csv
from pathlib import Path
from statistics import mean, median

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

WEEK11_PATH = Path("data/week11_heldout_predictions.csv")
OUTPUT_DIR = Path("docs/assets/week12-progress")


def load_week11_results():
    """Load the official Week 11 held-out predictions."""

    with WEEK11_PATH.open(
        "r",
        newline = "",
        encoding = "utf-8",
    ) as csv_file:

        reader = csv.DictReader(csv_file)

        rows = list(reader)

    if len(rows) != 40:
        raise ValueError(
            f"Expected 40 Week 11 rows, "
            f"found {len(rows)}"
        )

    return rows


def classify_outcome(row):
    """Return TP, TN, FP, or FN for one Week 11 row."""

    actual = row["label"].strip().lower()

    prediction = (
        row["prediction"]
        .strip()
        .lower()
    )

    if (actual == "stego" and prediction == "stego"):
        return "TP"

    if (actual == "clean" and prediction == "clean"):
        return "TN"

    if (actual == "clean" and prediction == "stego"):
        return "FP"

    if (actual == "stego" and prediction == "clean"):
        return "FN"

    raise ValueError(
        f"Unexpected labels: "
        f"actual={actual}, "
        f"prediction={prediction}"
    )


def count_outcomes(rows):
    """Count Week 11 TP, TN, FP, and FN cases."""

    counts = {
        "TP": 0,
        "TN": 0,
        "FP": 0,
        "FN": 0,
    }

    for row in rows:

        outcome = classify_outcome(row)

        counts[outcome] += 1

    return counts


def summarize_dh_by_outcome(rows):
    """Summarize normalized DH scores for TP, TN, FP, and FN cases."""

    groups = {
        "TP": [],
        "TN": [],
        "FP": [],
        "FN": [],
    }

    for row in rows:

        outcome = classify_outcome(row)

        normalized_dh = float(row["normalized_dh"])

        groups[outcome].append(normalized_dh)

    summaries = {}

    for outcome, values in groups.items():

        summaries[outcome] = {
            "Count": len(values),
            "Mean": mean(values),
            "Median": median(values),
            "Min": min(values),
            "Max": max(values),
        }

    return summaries


def plot_dh_error_groups(dh_summaries):
    """Plot mean normalized DH score for TP, TN, FP, and FN groups."""

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    outcomes = [
        "TP",
        "TN",
        "FP",
        "FN",
    ]

    mean_dh_scores = [
        dh_summaries[outcome]["Mean"]
        for outcome in outcomes
    ]

    fig, ax = plt.subplots()

    ax.bar(
        outcomes,
        mean_dh_scores,
    )

    ax.set_xlabel("Classification Outcome")

    ax.set_ylabel("Mean Normalized DH Score")

    ax.set_title("Week 12 DH Score by Classification Outcome")

    ax.set_ylim(0.0, 1.0)

    fig.tight_layout()

    output_path = (OUTPUT_DIR / "dh_error_groups.png")

    fig.savefig(
        output_path,
        dpi = 150,
    )

    plt.close(fig)

    return output_path


def main():
    """Run Week 12 DH error-case analysis."""

    rows = load_week11_results()

    counts = count_outcomes(
        rows
    )

    print(
        "Week 12 DH Error Analysis"
    )

    print(
        f"Week 11 rows: {len(rows)}"
    )

    print(
        f"TP: {counts['TP']}"
    )

    print(
        f"TN: {counts['TN']}"
    )

    print(
        f"FP: {counts['FP']}"
    )

    print(
        f"FN: {counts['FN']}"
    )

    dh_summaries = summarize_dh_by_outcome(rows)

    print()
    print("Normalized DH statistics by outcome:")

    for outcome in [
        "TP",
        "TN",
        "FP",
        "FN",
    ]:

        summary = dh_summaries[outcome]

        print(
            f"{outcome}: "
            f"n = {summary['Count']}, "
            f"Mean = {summary['Mean']:.6f}, "
            f"Median = {summary['Median']:.6f}, "
            f"Min = {summary['Min']:.6f}, "
            f"Max = {summary['Max']:.6f}"
        )

    plot_path = plot_dh_error_groups(dh_summaries)

    print()
    print(f"DH error-group plot created: {plot_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )