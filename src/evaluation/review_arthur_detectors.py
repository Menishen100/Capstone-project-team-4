"""Review Chi-square and RS development scores for Arthur's Week 7 work.

This module is descriptive only. It excludes validation and held-out rows and
does not select thresholds, normalize scores, rank detectors, or classify
images.
"""

from __future__ import annotations

import argparse
import csv
import math
import statistics
from pathlib import Path
from typing import Any, Iterable


DEVELOPMENT_SPLIT = "development"
DETECTORS = {"Chi-square": "chi_square_score", "RS": "rs_score"}
REQUIRED_COLUMNS = {"source_id", "label", "filename", "split", "status", *DETECTORS.values()}


def _read_score(row: dict[str, str], column: str) -> float:
    try:
        score = float(row[column])
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(f"{column} must contain a numeric score") from error
    if not math.isfinite(score) or not 0.0 <= score <= 1.0:
        raise ValueError(f"{column} must contain a finite score in [0, 1]")
    return score


def review_development_scores(path: str | Path) -> dict[str, Any]:
    """Summarize only completed Chi-square and RS development score rows.

    A candidate false positive is a clean score higher than every stego score
    for the same detector; a candidate false negative is a stego score lower
    than every clean score. These range-overlap flags are not classification
    errors because no decision threshold is chosen in this review.
    """
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError("score CSV is missing required columns: " + ", ".join(sorted(missing)))
        rows = list(reader)

    if not rows:
        raise ValueError("score CSV contains no rows")

    grouped: dict[str, dict[str, list[tuple[float, dict[str, str]]]]] = {
        name: {"clean": [], "stego": []} for name in DETECTORS
    }
    for row in rows:
        if row["split"] != DEVELOPMENT_SPLIT:
            raise ValueError("only development rows may be reviewed")
        if row["status"] != "complete":
            raise ValueError("all reviewed rows must have status=complete")
        if row["label"] not in {"clean", "stego"}:
            raise ValueError("labels must be clean or stego")
        for detector, column in DETECTORS.items():
            grouped[detector][row["label"]].append((_read_score(row, column), row))

    output: dict[str, Any] = {}
    for detector, labels in grouped.items():
        clean, stego = labels["clean"], labels["stego"]
        if not clean or not stego:
            raise ValueError(f"{detector} is missing clean or stego development scores")
        stego_max = max(score for score, _ in stego)
        clean_min = min(score for score, _ in clean)
        candidates_fp = [row for score, row in clean if score > stego_max]
        candidates_fn = [row for score, row in stego if score < clean_min]
        output[detector] = {
            "clean_mean": statistics.fmean(score for score, _ in clean),
            "stego_mean": statistics.fmean(score for score, _ in stego),
            "clean_median": statistics.median(score for score, _ in clean),
            "stego_median": statistics.median(score for score, _ in stego),
            "candidate_fp_rows": candidates_fp,
            "candidate_fn_rows": candidates_fn,
        }
    return output


def format_review(review: dict[str, Any]) -> str:
    """Return a concise terminal report for Arthur's Week 7 evidence."""
    lines = ["Arthur Week 7 — Chi-square and RS development-only review", ""]
    for detector, values in review.items():
        fp_rows = values["candidate_fp_rows"]
        fn_rows = values["candidate_fn_rows"]
        lines.extend(
            [
                f"{detector}:",
                f"  Clean mean: {values['clean_mean']:.6f}",
                f"  Stego mean: {values['stego_mean']:.6f}",
                f"  Clean median: {values['clean_median']:.6f}",
                f"  Stego median: {values['stego_median']:.6f}",
                f"  Candidate FP count: {len(fp_rows)}",
                f"  Candidate FN count: {len(fn_rows)}",
                f"  Candidate FP files: {', '.join(row['filename'] for row in fp_rows) or 'none'}",
                f"  Candidate FN files: {', '.join(row['filename'] for row in fn_rows) or 'none'}",
                "",
            ]
        )
    lines.extend(
        [
            "Candidate counts use opposite-class score-range overlap only.",
            "No threshold, normalization, ranking, classifier, or ensemble was selected.",
        ]
    )
    return "\n".join(lines)


def main(arguments: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Review Arthur's Week 7 detector scores.")
    parser.add_argument("--scores", type=Path, default=Path("data/development_detector_scores.csv"))
    args = parser.parse_args(arguments)
    print(format_review(review_development_scores(args.scores)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
