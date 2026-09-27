"""Run the three prototype detectors across the development dataset only.

This Week 6 runner produces descriptive, per-image results.  It deliberately
does not select thresholds, normalize across detectors, or inspect the
validation and held-out splits; those activities belong to later weeks.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from numbers import Real
from pathlib import Path
from typing import Any, Iterable, Mapping

from src.detectors import ChiSquareDetector, DifferenceHistogramDetector, RSAnalysisDetector
from src.preprocessing import load_image


DEVELOPMENT_SPLIT = "development"
REQUIRED_METADATA_FIELDS = {
    "source_id",
    "clean_filename",
    "stego_filename",
    "split",
}
SCORE_FIELDS = ("chi_square_score", "rs_score", "dh_score")
OUTPUT_FIELDS = (
    "source_id",
    "label",
    "image_type",
    "filename",
    "split",
    *SCORE_FIELDS,
    "chi_square_p_value",
    "rs_statistic",
    "dh_raw_roughness",
    "chi_square_diagnostics",
    "rs_diagnostics",
    "dh_diagnostics",
    "status",
    "error",
)


def default_detectors() -> dict[str, Any]:
    """Return the detectors used by the preliminary experiment."""
    return {
        "chi_square": ChiSquareDetector(),
        "rs": RSAnalysisDetector(),
        "dh": DifferenceHistogramDetector(),
    }


def development_pairs(metadata_path: str | Path) -> list[dict[str, str]]:
    """Load only development rows from paired-dataset metadata.

    The metadata represents pairs, so each returned row will later produce one
    clean score row and one stego score row.
    """
    path = Path(metadata_path)
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        missing = REQUIRED_METADATA_FIELDS - fieldnames
        if missing:
            raise ValueError("metadata is missing required columns: " + ", ".join(sorted(missing)))
        rows = [dict(row) for row in reader if row.get("split") == DEVELOPMENT_SPLIT]

    source_ids = [row["source_id"] for row in rows]
    if len(source_ids) != len(set(source_ids)):
        raise ValueError("development metadata contains duplicate source_id values")
    return sorted(rows, key=lambda row: row["source_id"])


def _bounded_score(result: Mapping[str, Any]) -> float:
    """Read and validate one common-interface suspiciousness score."""
    score = result.get("score")
    if not isinstance(score, Real) or isinstance(score, bool) or not 0.0 <= float(score) <= 1.0:
        raise ValueError("detector returned a score outside the required [0, 1] range")
    return float(score)


def _as_json(value: Any) -> str:
    """Serialize diagnostics in a CSV-safe, reproducible representation."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _score_image(
    source_id: str,
    label: str,
    filename: str,
    image_directory: Path,
    detectors: Mapping[str, Any],
) -> dict[str, str]:
    """Score one image, recording failures without ending the complete run."""
    row = {
        "source_id": source_id,
        "label": label,
        "image_type": label,
        "filename": filename,
        "split": DEVELOPMENT_SPLIT,
        **{field: "" for field in SCORE_FIELDS},
        "chi_square_p_value": "",
        "rs_statistic": "",
        "dh_raw_roughness": "",
        "chi_square_diagnostics": "",
        "rs_diagnostics": "",
        "dh_diagnostics": "",
        "status": "complete",
        "error": "",
    }
    try:
        image = load_image(image_directory / filename)
    except Exception as error:  # The row must document a bad image rather than abort the run.
        row["status"] = "error"
        row["error"] = f"image load: {type(error).__name__}: {error}"
        return row

    errors: list[str] = []
    for detector_name, detector in detectors.items():
        try:
            result = detector.analyze(image)
            diagnostics = result.get("diagnostics")
            if not isinstance(diagnostics, Mapping):
                raise ValueError("detector returned diagnostics that are not a mapping")
            row[f"{detector_name}_score"] = str(_bounded_score(result))
            row[f"{detector_name}_diagnostics"] = _as_json(diagnostics)
            if detector_name == "chi_square":
                row["chi_square_p_value"] = str(diagnostics.get("p_value", ""))
            elif detector_name == "rs":
                row["rs_statistic"] = str(diagnostics.get("rs_statistic", ""))
            elif detector_name == "dh":
                row["dh_raw_roughness"] = str(diagnostics.get("raw_roughness", ""))
        except Exception as error:  # One detector failure must not hide the other detector results.
            errors.append(f"{detector_name}: {type(error).__name__}: {error}")

    if errors:
        row["status"] = "partial_error"
        row["error"] = " | ".join(errors)
    return row


def run_preliminary_scores(
    metadata_path: str | Path,
    clean_directory: str | Path,
    stego_directory: str | Path,
    output_path: str | Path,
    *,
    detectors: Mapping[str, Any] | None = None,
) -> list[dict[str, str]]:
    """Score clean/stego development pairs and write a reproducible CSV table."""
    active_detectors = dict(detectors or default_detectors())
    if set(active_detectors) != {"chi_square", "rs", "dh"}:
        raise ValueError("detectors must provide chi_square, rs, and dh entries")

    rows: list[dict[str, str]] = []
    for pair in development_pairs(metadata_path):
        rows.append(_score_image(pair["source_id"], "clean", pair["clean_filename"], Path(clean_directory), active_detectors))
        rows.append(_score_image(pair["source_id"], "stego", pair["stego_filename"], Path(stego_directory), active_detectors))

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return rows


def summarize(rows: Iterable[Mapping[str, str]]) -> dict[str, int]:
    """Return concise, display-ready counts for a completed scoring run."""
    materialized = list(rows)
    counts = Counter(row["label"] for row in materialized)
    detector_errors = {
        name: sum(name + ":" in row.get("error", "") for row in materialized)
        for name in ("chi_square", "rs", "dh")
    }
    return {
        "clean_images_scored": counts["clean"],
        "stego_images_scored": counts["stego"],
        "total_images_scored": len(materialized),
        **{f"{name}_errors": count for name, count in detector_errors.items()},
    }


def main(arguments: Iterable[str] | None = None) -> int:
    """Run the Week 6 preliminary development-only experiment."""
    parser = argparse.ArgumentParser(description="Score the development split with all three detectors.")
    parser.add_argument("--metadata", type=Path, default=Path("data/metadata.csv"))
    parser.add_argument("--clean-directory", type=Path, default=Path("dataset/clean"))
    parser.add_argument("--stego-directory", type=Path, default=Path("dataset/stego"))
    parser.add_argument("--output", type=Path, default=Path("data/development_detector_scores.csv"))
    args = parser.parse_args(arguments)

    rows = run_preliminary_scores(args.metadata, args.clean_directory, args.stego_directory, args.output)
    result = summarize(rows)
    print("Development scoring complete")
    print(f"Clean images scored: {result['clean_images_scored']}")
    print(f"Stego images scored: {result['stego_images_scored']}")
    print(f"Total images scored: {result['total_images_scored']}")
    print(f"Chi-square errors: {result['chi_square_errors']}")
    print(f"RS errors: {result['rs_errors']}")
    print(f"DH errors: {result['dh_errors']}")
    print(f"Output: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
