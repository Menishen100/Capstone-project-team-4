"""Arthur's Chi-square/RS diagnostics over the official Week 11 outcomes."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Mapping

from src.evaluation.analyze_week12_errors import classify_cases, load_official_predictions


def detector_summary(rows: list[Mapping[str, Any]]) -> dict[str, dict[str, float | int]]:
    """Calculate raw and normalized Chi-square/RS means by confusion cell."""
    groups = classify_cases(rows)
    summary: dict[str, dict[str, float | int]] = {}
    for cell, entries in groups.items():
        result: dict[str, float | int] = {"count": len(entries)}
        for field in ("chi_square_score", "rs_score", "normalized_chi", "normalized_rs"):
            result[f"mean_{field}"] = (
                sum(float(row[field]) for row in entries) / len(entries) if entries else float("nan")
            )
        summary[cell] = result
    return summary


def render_markdown(summary: Mapping[str, Mapping[str, float | int]]) -> str:
    columns = ("count", "mean_chi_square_score", "mean_rs_score", "mean_normalized_chi", "mean_normalized_rs")
    labels = ("Rows", "Mean Chi-square", "Mean RS", "Mean normalized Chi", "Mean normalized RS")
    lines = ["| Outcome | " + " | ".join(labels) + " |", "|---|" + "---:|" * len(labels)]
    for cell in ("true_positive", "true_negative", "false_positive", "false_negative"):
        values = [summary[cell][column] for column in columns]
        formatted = [str(values[0])] + ["n/a" if value != value else f"{float(value):.4f}" for value in values[1:]]
        lines.append("| " + cell.replace("_", " ").title() + " | " + " | ".join(formatted) + " |")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions", type=Path, default=Path("data/week11_heldout_predictions.csv"))
    args = parser.parse_args(argv)
    print(render_markdown(detector_summary(load_official_predictions(args.predictions))))
    print("\nDiagnostic only: Chi-square's locked ensemble weight is 0.00; RS weight is 0.70.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
