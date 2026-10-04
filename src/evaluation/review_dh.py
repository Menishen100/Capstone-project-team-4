"""Review Difference Histogram (DH) development scores.

This module analyzes development-set DH results only. It verifies the current
normalization, compares paired clean/stego scores, reviews range-extreme cases,
and checks DH diagnostics and preprocessing consistency.

It does not select a final threshold or produce a final evaluation score.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from pathlib import Path
from typing import Any, Iterable


DEVELOPMENT_SPLIT = "development"
EXPECTED_HISTOGRAM_TOTAL = 130560
NORMALIZATION_FORMULA = "raw_roughness / (1.0 + raw_roughness)"

REQUIRED_COLUMNS = {
    "source_id",
    "label",
    "filename",
    "split",
    "status",
    "dh_score",
    "dh_raw_roughness",
    "dh_diagnostics",
}

REQUIRED_CHANNEL_DIAGNOSTICS = {
    "channel",
    "zero_difference_fraction",
    "variation",
    "central_total",
    "histogram_total",
}


def _read_dh_score(
    row: dict[str, str]
) -> float:
    try:
        score = float(row["dh_score"])
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(
            "dh_score must contain a numeric value"
        ) from error

    if not math.isfinite(score) or not 0.0 <= score <= 1.0:
        raise ValueError(
            "dh_score must contain a finite value in [0.0, 1.0]"
        )

    return score


def _read_raw_roughness(
    row: dict[str, str]
) -> float:
    try:
        roughness = float(
            row["dh_raw_roughness"]
        )
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(
            "dh_raw_roughness must contain a numeric value"
        ) from error

    if not math.isfinite(roughness) or roughness < 0.0:
        raise ValueError(
            "dh_raw_roughness must contain a finite non-negative value"
        )

    return roughness


def _read_dh_diagnostics(
    row: dict[str, str]
) -> dict[str, Any]:
    try:
        diagnostics = json.loads(
            row["dh_diagnostics"]
        )
    except (
        KeyError,
        TypeError,
        json.JSONDecodeError,
    ) as error:
        raise ValueError(
            "dh_diagnostics must contain valid JSON"
        ) from error

    if not isinstance(diagnostics, dict):
        raise ValueError(
            "dh_diagnostics must be a JSON object"
        )

    return diagnostics


def _summarize_dh_diagnostics(
    record: dict[str, Any]
) -> dict[str, Any]:
    channels = record["dh_diagnostics"].get(
        "channels"
    )

    if not isinstance(channels, list) or not channels:
        raise ValueError(
            "dh_diagnostics must contain a non-empty 'channels' list"
        )

    for channel in channels:
        if not isinstance(channel, dict):
            raise ValueError(
                "dh_diagnostics 'channels' must contain JSON objects"
            )

        missing = (
            REQUIRED_CHANNEL_DIAGNOSTICS
            - set(channel)
        )

        if missing:
            raise ValueError(
                "dh_diagnostics 'channels' is missing required keys: "
                + ", ".join(sorted(missing))
            )

    channel_names = [
        channel["channel"]
        for channel in channels
    ]

    if channel_names == ["L"]:
        image_mode = "L"

    elif channel_names == ["R", "G", "B"]:
        image_mode = "RGB"

    else:
        raise ValueError(
            "dh_diagnostics 'channels' must contain either "
            "['L'] or ['R', 'G', 'B']"
        )

    histogram_totals = [
        channel["histogram_total"]
        for channel in channels
    ]

    return {
        "source_id": record["source_id"],
        "filename": record["filename"],
        "label": record["label"],
        "image_mode": image_mode,
        "dh_score": record["dh_score"],
        "dh_raw_roughness": record["dh_raw_roughness"],
        "mean_zero_difference_fraction": statistics.fmean(
            channel["zero_difference_fraction"]
            for channel in channels
        ),
        "mean_variation": statistics.fmean(
            channel["variation"]
            for channel in channels
        ),
        "mean_central_total": statistics.fmean(
            channel["central_total"]
            for channel in channels
        ),
        "histogram_totals": histogram_totals,
        "histogram_total_verified": all(
            total == EXPECTED_HISTOGRAM_TOTAL
            for total in histogram_totals
        ),
    }


def _mean_score(
    summaries: list[dict[str, Any]]
) -> float | None:
    if not summaries:
        return None

    return statistics.fmean(
        summary["dh_score"]
        for summary in summaries
    )


def _format_optional_score(
    value: float | None
) -> str:
    if value is None:
        return "n/a"

    return f"{value:.6f}"


def review_development_dh(
    path: str | Path
) -> dict[str, Any]:
    """Review completed DH development rows without selecting a threshold."""

    with Path(path).open(
        newline="",
        encoding="utf-8",
    ) as handle:
        reader = csv.DictReader(handle)

        missing = (
            REQUIRED_COLUMNS
            - set(reader.fieldnames or [])
        )

        if missing:
            raise ValueError(
                "Score CSV is missing required columns: "
                + ", ".join(sorted(missing))
            )

        rows = list(reader)

    if not rows:
        raise ValueError(
            "Score CSV contains no rows"
        )

    development_rows = [
        row
        for row in rows
        if row["split"] == DEVELOPMENT_SPLIT
    ]

    if not development_rows:
        raise ValueError(
            "Score CSV contains no development rows"
        )

    grouped: dict[
        str,
        list[dict[str, Any]],
    ] = {
        "clean": [],
        "stego": [],
    }

    for row in development_rows:
        if row["status"] != "complete":
            raise ValueError(
                "All reviewed rows must have status 'complete'"
            )

        if row["label"] not in {
            "clean",
            "stego",
        }:
            raise ValueError(
                "All reviewed rows must have label 'clean' or 'stego'"
            )

        grouped[row["label"]].append(
            {
                "source_id": row["source_id"],
                "filename": row["filename"],
                "label": row["label"],
                "dh_score": _read_dh_score(row),
                "dh_raw_roughness": _read_raw_roughness(row),
                "dh_diagnostics": _read_dh_diagnostics(row),
            }
        )

    clean = grouped["clean"]
    stego = grouped["stego"]

    if not clean:
        raise ValueError(
            "Score CSV contains no clean rows"
        )

    if not stego:
        raise ValueError(
            "Score CSV contains no stego rows"
        )

    clean_scores = [
        record["dh_score"]
        for record in clean
    ]

    stego_scores = [
        record["dh_score"]
        for record in stego
    ]

    clean_roughness = [
        record["dh_raw_roughness"]
        for record in clean
    ]

    stego_roughness = [
        record["dh_raw_roughness"]
        for record in stego
    ]

    all_records = clean + stego

    normalization_mismatches = []

    for record in all_records:
        raw_roughness = record[
            "dh_raw_roughness"
        ]

        expected_score = (
            raw_roughness
            / (1.0 + raw_roughness)
        )

        if not math.isclose(
            record["dh_score"],
            expected_score,
            rel_tol=1e-6,
            abs_tol=1e-6,
        ):
            normalization_mismatches.append(
                {
                    "source_id": record["source_id"],
                    "filename": record["filename"],
                    "actual_score": record["dh_score"],
                    "expected_score": expected_score,
                }
            )

    clean_by_source = {
        record["source_id"]: record
        for record in clean
    }

    stego_by_source = {
        record["source_id"]: record
        for record in stego
    }

    if len(clean_by_source) != len(clean):
        raise ValueError(
            "Clean development rows contain duplicate source_id values"
        )

    if len(stego_by_source) != len(stego):
        raise ValueError(
            "Stego development rows contain duplicate source_id values"
        )

    if set(clean_by_source) != set(stego_by_source):
        raise ValueError(
            "Clean and stego records must have matching source_id values"
        )

    stego_higher_count = 0
    stego_lower_count = 0
    equal_score_count = 0

    stego_higher_pairs = []

    for source_id in sorted(clean_by_source):
        clean_record = clean_by_source[
            source_id
        ]

        stego_record = stego_by_source[
            source_id
        ]

        clean_score = clean_record[
            "dh_score"
        ]

        stego_score = stego_record[
            "dh_score"
        ]

        score_change = (
            stego_score
            - clean_score
        )

        if math.isclose(
            clean_score,
            stego_score,
            rel_tol=1e-6,
            abs_tol=1e-6,
        ):
            equal_score_count += 1

        elif stego_score > clean_score:
            stego_higher_count += 1

            stego_higher_pairs.append(
                {
                    "source_id": source_id,
                    "clean_filename": clean_record["filename"],
                    "stego_filename": stego_record["filename"],
                    "clean_score": clean_score,
                    "stego_score": stego_score,
                    "score_change": score_change,
                }
            )

        else:
            stego_lower_count += 1

    stego_max = max(
        stego_scores
    )

    clean_min = min(
        clean_scores
    )

    candidate_fp_records = [
        record
        for record in clean
        if record["dh_score"] > stego_max
    ]

    candidate_fn_records = [
        record
        for record in stego
        if record["dh_score"] < clean_min
    ]

    candidate_fp_summaries = [
        {
            **_summarize_dh_diagnostics(
                record
            ),
            "reason": (
                "clean score exceeded every stego score"
            ),
        }
        for record in candidate_fp_records
    ]

    candidate_fn_summaries = [
        {
            **_summarize_dh_diagnostics(
                record
            ),
            "reason": (
                "stego score was below every clean score"
            ),
        }
        for record in candidate_fn_records
    ]

    clean_summaries = [
        _summarize_dh_diagnostics(
            record
        )
        for record in clean
    ]

    stego_summaries = [
        _summarize_dh_diagnostics(
            record
        )
        for record in stego
    ]

    clean_rgb_summaries = [
        summary
        for summary in clean_summaries
        if summary["image_mode"] == "RGB"
    ]

    clean_grayscale_summaries = [
        summary
        for summary in clean_summaries
        if summary["image_mode"] == "L"
    ]

    stego_rgb_summaries = [
        summary
        for summary in stego_summaries
        if summary["image_mode"] == "RGB"
    ]

    stego_grayscale_summaries = [
        summary
        for summary in stego_summaries
        if summary["image_mode"] == "L"
    ]

    all_summaries = (
        clean_summaries
        + stego_summaries
    )

    histogram_total_mismatches = [
        {
            "source_id": summary["source_id"],
            "filename": summary["filename"],
            "image_mode": summary["image_mode"],
            "histogram_totals": summary["histogram_totals"],
        }
        for summary in all_summaries
        if not summary["histogram_total_verified"]
    ]

    return {
        "clean_count": len(clean),
        "stego_count": len(stego),

        "all_scores_in_range": all(
            0.0 <= record["dh_score"] <= 1.0
            for record in all_records
        ),

        "normalization_verified": (
            not normalization_mismatches
        ),
        "normalization_formula": NORMALIZATION_FORMULA,
        "normalization_mismatches": normalization_mismatches,

        "pair_count": len(
            clean_by_source
        ),
        "stego_higher_count": stego_higher_count,
        "stego_lower_count": stego_lower_count,
        "equal_score_count": equal_score_count,
        "stego_higher_pairs": stego_higher_pairs,

        "candidate_fp_count": len(
            candidate_fp_summaries
        ),
        "candidate_fn_count": len(
            candidate_fn_summaries
        ),
        "candidate_fp_summaries": candidate_fp_summaries,
        "candidate_fn_summaries": candidate_fn_summaries,

        "clean_zero_difference_mean": statistics.fmean(
            summary["mean_zero_difference_fraction"]
            for summary in clean_summaries
        ),
        "stego_zero_difference_mean": statistics.fmean(
            summary["mean_zero_difference_fraction"]
            for summary in stego_summaries
        ),

        "clean_variation_mean": statistics.fmean(
            summary["mean_variation"]
            for summary in clean_summaries
        ),
        "stego_variation_mean": statistics.fmean(
            summary["mean_variation"]
            for summary in stego_summaries
        ),

        "clean_central_total_mean": statistics.fmean(
            summary["mean_central_total"]
            for summary in clean_summaries
        ),
        "stego_central_total_mean": statistics.fmean(
            summary["mean_central_total"]
            for summary in stego_summaries
        ),

        "clean_rgb_count": len(
            clean_rgb_summaries
        ),
        "clean_grayscale_count": len(
            clean_grayscale_summaries
        ),
        "stego_rgb_count": len(
            stego_rgb_summaries
        ),
        "stego_grayscale_count": len(
            stego_grayscale_summaries
        ),

        "clean_rgb_mean_score": _mean_score(
            clean_rgb_summaries
        ),
        "clean_grayscale_mean_score": _mean_score(
            clean_grayscale_summaries
        ),
        "stego_rgb_mean_score": _mean_score(
            stego_rgb_summaries
        ),
        "stego_grayscale_mean_score": _mean_score(
            stego_grayscale_summaries
        ),

        "histogram_total_verified": (
            not histogram_total_mismatches
        ),
        "histogram_total_expected": EXPECTED_HISTOGRAM_TOTAL,
        "histogram_total_mismatches": histogram_total_mismatches,

        "clean_score_mean": statistics.fmean(
            clean_scores
        ),
        "stego_score_mean": statistics.fmean(
            stego_scores
        ),

        "clean_score_median": statistics.median(
            clean_scores
        ),
        "stego_score_median": statistics.median(
            stego_scores
        ),

        "clean_score_min": min(
            clean_scores
        ),
        "clean_score_max": max(
            clean_scores
        ),

        "stego_score_min": min(
            stego_scores
        ),
        "stego_score_max": max(
            stego_scores
        ),

        "clean_roughness_mean": statistics.fmean(
            clean_roughness
        ),
        "stego_roughness_mean": statistics.fmean(
            stego_roughness
        ),
    }


def format_review(
    review: dict[str, Any]
) -> str:
    """Return a concise terminal report for the DH development review."""

    fp_files = [
        summary["filename"]
        for summary in review[
            "candidate_fp_summaries"
        ]
    ]

    fn_files = [
        summary["filename"]
        for summary in review[
            "candidate_fn_summaries"
        ]
    ]

    lines = [
        "Difference Histogram (DH) Development-Only Review",
        "",
        "Normalized DH Score:",
        f"  Clean Count: {review['clean_count']}",
        f"  Stego Count: {review['stego_count']}",
        f"  Clean Mean: {review['clean_score_mean']:.6f}",
        f"  Stego Mean: {review['stego_score_mean']:.6f}",
        f"  Clean Median: {review['clean_score_median']:.6f}",
        f"  Stego Median: {review['stego_score_median']:.6f}",
        (
            "  Clean Min/Max: "
            f"{review['clean_score_min']:.6f} / "
            f"{review['clean_score_max']:.6f}"
        ),
        (
            "  Stego Min/Max: "
            f"{review['stego_score_min']:.6f} / "
            f"{review['stego_score_max']:.6f}"
        ),
        "",
        "Raw Roughness:",
        f"  Clean Mean: {review['clean_roughness_mean']:.6f}",
        f"  Stego Mean: {review['stego_roughness_mean']:.6f}",
        "",
        "Normalization:",
        (
            "  All scores in range [0.0, 1.0]: "
            + (
                "yes"
                if review["all_scores_in_range"]
                else "no"
            )
        ),
        (
            "  Formula verified: "
            + (
                "yes"
                if review["normalization_verified"]
                else "no"
            )
        ),
        f"  Formula: {review['normalization_formula']}",
        (
            "  Normalization mismatches: "
            f"{len(review['normalization_mismatches'])}"
        ),
        "",
        "Paired Clean/Stego Comparison:",
        f"  Pair Count: {review['pair_count']}",
        f"  Stego Higher Count: {review['stego_higher_count']}",
        f"  Stego Lower Count: {review['stego_lower_count']}",
        f"  Equal Score Count: {review['equal_score_count']}",
        "",
        "Candidate Range-Extreme Cases:",
        (
            "  Candidate False Positive Count: "
            f"{review['candidate_fp_count']}"
        ),
        (
            "  Candidate False Positive Files: "
            f"{', '.join(fp_files) or 'None'}"
        ),
        (
            "  Candidate False Negative Count: "
            f"{review['candidate_fn_count']}"
        ),
        (
            "  Candidate False Negative Files: "
            f"{', '.join(fn_files) or 'None'}"
        ),
        "",
        "Diagnostics Summary:",
        (
            "  Clean Mean Zero Difference Fraction: "
            f"{review['clean_zero_difference_mean']:.6f}"
        ),
        (
            "  Stego Mean Zero Difference Fraction: "
            f"{review['stego_zero_difference_mean']:.6f}"
        ),
        (
            "  Clean Mean Variation: "
            f"{review['clean_variation_mean']:.6f}"
        ),
        (
            "  Stego Mean Variation: "
            f"{review['stego_variation_mean']:.6f}"
        ),
        (
            "  Clean Mean Central Total: "
            f"{review['clean_central_total_mean']:.6f}"
        ),
        (
            "  Stego Mean Central Total: "
            f"{review['stego_central_total_mean']:.6f}"
        ),
        "",
        "Image Mode Review:",
        (
            "  Clean RGB/Grayscale Count: "
            f"{review['clean_rgb_count']} / "
            f"{review['clean_grayscale_count']}"
        ),
        (
            "  Stego RGB/Grayscale Count: "
            f"{review['stego_rgb_count']} / "
            f"{review['stego_grayscale_count']}"
        ),
        (
            "  Clean RGB Mean Score: "
            + _format_optional_score(
                review["clean_rgb_mean_score"]
            )
        ),
        (
            "  Stego RGB Mean Score: "
            + _format_optional_score(
                review["stego_rgb_mean_score"]
            )
        ),
        (
            "  Clean Grayscale Mean Score: "
            + _format_optional_score(
                review["clean_grayscale_mean_score"]
            )
        ),
        (
            "  Stego Grayscale Mean Score: "
            + _format_optional_score(
                review["stego_grayscale_mean_score"]
            )
        ),
        "",
        "Preprocessing Consistency Check:",
        (
            "  Expected Histogram Total per Channel: "
            f"{review['histogram_total_expected']}"
        ),
        (
            "  All histogram totals matched: "
            + (
                "yes"
                if review["histogram_total_verified"]
                else "no"
            )
        ),
        (
            "  Histogram Total Mismatches: "
            f"{len(review['histogram_total_mismatches'])}"
        ),
    ]

    if review["candidate_fp_summaries"]:
        lines.extend(
            [
                "",
                "Detailed Candidate Clean Case Diagnostics:",
            ]
        )

        for summary in review[
            "candidate_fp_summaries"
        ]:
            lines.append(
                (
                    f"  {summary['source_id']} | "
                    f"{summary['filename']} | "
                    f"label={summary['label']} | "
                    f"mode={summary['image_mode']} | "
                    f"score={summary['dh_score']:.6f} | "
                    f"raw={summary['dh_raw_roughness']:.6f} | "
                    f"zero_fraction="
                    f"{summary['mean_zero_difference_fraction']:.6f} | "
                    f"variation={summary['mean_variation']:.3f} | "
                    f"reason={summary['reason']}"
                )
            )

    if review["candidate_fn_summaries"]:
        lines.extend(
            [
                "",
                "Detailed Candidate Stego Case Diagnostics:",
            ]
        )

        for summary in review[
            "candidate_fn_summaries"
        ]:
            lines.append(
                (
                    f"  {summary['source_id']} | "
                    f"{summary['filename']} | "
                    f"label={summary['label']} | "
                    f"mode={summary['image_mode']} | "
                    f"score={summary['dh_score']:.6f} | "
                    f"raw={summary['dh_raw_roughness']:.6f} | "
                    f"zero_fraction="
                    f"{summary['mean_zero_difference_fraction']:.6f} | "
                    f"variation={summary['mean_variation']:.3f} | "
                    f"reason={summary['reason']}"
                )
            )

    if review["stego_higher_pairs"]:
        lines.extend(
            [
                "",
                "Detailed Stego-Higher Pair Diagnostics:",
            ]
        )

        for pair in review[
            "stego_higher_pairs"
        ]:
            lines.append(
                (
                    f"  {pair['source_id']} | "
                    f"clean={pair['clean_filename']} "
                    f"({pair['clean_score']:.6f}) | "
                    f"stego={pair['stego_filename']} "
                    f"({pair['stego_score']:.6f}) | "
                    f"change={pair['score_change']:.6f}"
                )
            )

    if review["histogram_total_mismatches"]:
        lines.extend(
            [
                "",
                "Histogram Total Mismatch Details:",
            ]
        )

        for mismatch in review[
            "histogram_total_mismatches"
        ]:
            lines.append(
                (
                    f"  {mismatch['source_id']} | "
                    f"{mismatch['filename']} | "
                    f"mode={mismatch['image_mode']} | "
                    f"totals={mismatch['histogram_totals']}"
                )
            )

    return "\n".join(lines)


def main(
    arguments: Iterable[str] | None = None
) -> int:
    """Run the DH development review from the command line."""

    parser = argparse.ArgumentParser(
        description=(
            "Review DH development-set scores."
        )
    )

    parser.add_argument(
        "--scores",
        type=Path,
        default=Path(
            "data/development_detector_scores.csv"
        ),
        help=(
            "Path to the development detector score CSV"
        ),
    )

    args = parser.parse_args(
        arguments
    )

    review = review_development_dh(
        args.scores
    )

    print(
        format_review(
            review
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )