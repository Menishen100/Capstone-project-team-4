"""Release-candidate command-line interface for one-image steganalysis.

The CLI intentionally reuses the existing detector implementations, the Week 9
normalization/voting boundary, and the locked Week 10 configuration. It does
not calibrate, retrain, or change any detector score.
"""

from __future__ import annotations

import argparse
import math
from collections.abc import Mapping, Sequence
from numbers import Real
from pathlib import Path
from typing import Any

from src.ensemble.voting import combine_detector_scores
from src.evaluation.run_heldout_evaluation import LOCKED_CONFIG
from src.evaluation.run_preliminary_scores import default_detectors
from src.preprocessing import load_image


DETECTOR_NAMES = ("chi_square", "rs", "dh")


def _bounded_score(result: Mapping[str, Any]) -> float:
    """Extract a detector's common-interface score without re-normalizing it."""
    score = result.get("score")
    if (
        isinstance(score, bool)
        or not isinstance(score, Real)
        or not math.isfinite(float(score))
        or not 0.0 <= float(score) <= 1.0
    ):
        raise ValueError("detector returned a non-finite score outside [0, 1]")
    return float(score)


def analyze_image(
    image_path: str | Path,
    *,
    detectors: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    """Analyze one image with the existing locked ensemble configuration.

    Args:
        image_path: A file that Pillow can read. Grayscale and RGB images retain
            their pixel representation; other readable Pillow modes follow the
            project's established preprocessing conversion to RGB.
        detectors: Optional test seam. Production calls use the three project
            detector instances returned by :func:`default_detectors`.

    Returns:
        A display-ready, structured result containing raw detector scores,
        direction-aligned scores, locked configuration values, and the final
        ``Clean`` or ``Suspicious`` decision.
    """
    path = Path(image_path)
    image = load_image(path)
    active_detectors = dict(detectors or default_detectors())
    if set(active_detectors) != set(DETECTOR_NAMES):
        raise ValueError("detectors must provide chi_square, rs, and dh entries")

    raw_scores = {
        detector_name: _bounded_score(active_detectors[detector_name].analyze(image))
        for detector_name in DETECTOR_NAMES
    }
    ensemble = combine_detector_scores(raw_scores, LOCKED_CONFIG)
    diagnostics = ensemble["diagnostics"]
    normalized_scores = diagnostics["normalized_scores"]

    return {
        "image_path": str(path),
        "image_mode": "L" if image.ndim == 2 else "RGB",
        "raw_scores": raw_scores,
        "normalized_scores": normalized_scores,
        "ensemble_score": float(ensemble["ensemble_score"]),
        "classification": str(ensemble["label"]),
        "weights": diagnostics["weights"],
        "threshold": float(diagnostics["threshold"]),
    }


def format_analysis(analysis: Mapping[str, object]) -> str:
    """Format a concise, explainable release-candidate CLI report."""
    raw_scores = analysis["raw_scores"]
    normalized_scores = analysis["normalized_scores"]
    weights = analysis["weights"]
    assert isinstance(raw_scores, Mapping)
    assert isinstance(normalized_scores, Mapping)
    assert isinstance(weights, Mapping)

    return "\n".join(
        (
            "Multi-Feature Steganalysis Toolkit - Release Candidate",
            f"Image: {analysis['image_path']} ({analysis['image_mode']})",
            "Locked ensemble: "
            f"Chi-square={float(weights['chi_square']):.2f}, "
            f"RS={float(weights['rs']):.2f}, "
            f"DH={float(weights['dh']):.2f}, "
            f"threshold={float(analysis['threshold']):.2f}",
            "Detector scores (raw -> direction-aligned suspiciousness):",
            f"  Chi-square: {float(raw_scores['chi_square']):.4f} -> "
            f"{float(normalized_scores['chi_square']):.4f}",
            f"  RS:         {float(raw_scores['rs']):.4f} -> "
            f"{float(normalized_scores['rs']):.4f}",
            f"  DH:         {float(raw_scores['dh']):.4f} -> "
            f"{float(normalized_scores['dh']):.4f}",
            f"Ensemble score (not a probability): {float(analysis['ensemble_score']):.4f}",
            f"Final classification: {analysis['classification']}",
        )
    )


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser without duplicating analysis behavior."""
    parser = argparse.ArgumentParser(
        description=(
            "Analyze one image using the project's locked statistical "
            "steganalysis ensemble."
        )
    )
    parser.add_argument("image", type=Path, help="Path to an image readable by Pillow")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return a conventional process exit code."""
    parser = build_parser()
    arguments = parser.parse_args(argv)
    try:
        print(format_analysis(analyze_image(arguments.image)))
    except (OSError, ValueError) as error:
        parser.error(f"could not analyze '{arguments.image}': {error}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
