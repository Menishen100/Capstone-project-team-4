"""User-facing command line interface for one-image steganalysis."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# When invoked as ``python src/cli.py``, Python starts with ``src/`` on the
# import path. Add the project root so the same package imports work as with
# ``python -m src.cli``.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image, UnidentifiedImageError

from src.detectors import ChiSquareDetector, DifferenceHistogramDetector, RSAnalysisDetector
from src.ensemble.voting import combine_detector_scores
from src.evaluation.run_heldout_evaluation import LOCKED_CONFIG
from src.preprocessing import load_image

VERSION = "1.0.0"
SUPPORTED_FORMATS = {"PNG", "JPEG", "BMP", "TIFF"}


class UserInputError(Exception):
    """An input or image problem that should be shown without a traceback."""


def analyze_image(path: str | Path) -> dict[str, object]:
    """Run the project's detectors and locked ensemble on one supported image."""
    image_path = Path(path)
    if not image_path.is_file():
        raise UserInputError(f"image file does not exist: {image_path}")
    try:
        with Image.open(image_path) as opened:
            if opened.format not in SUPPORTED_FORMATS:
                raise UserInputError(
                    f"unsupported image format: {opened.format or 'unknown'}; "
                    "supported formats are PNG, JPEG, BMP, and TIFF"
                )
            opened.verify()
        pixels = load_image(image_path)
    except UserInputError:
        raise
    except (UnidentifiedImageError, OSError, ValueError) as error:
        raise UserInputError(f"cannot read image '{image_path}': {error}") from error

    detectors = {
        "chi_square": ChiSquareDetector(),
        "rs": RSAnalysisDetector(),
        "dh": DifferenceHistogramDetector(),
    }
    try:
        raw_scores = {
            name: float(detector.analyze(pixels)["score"])
            for name, detector in detectors.items()
        }
        result = combine_detector_scores(raw_scores, LOCKED_CONFIG)
    except Exception as error:
        raise UserInputError(f"detector analysis failed: {error}") from error
    return {"image": str(image_path), "detector_scores": raw_scores, **result}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m src.cli",
        description="Analyze one image with the statistical LSB steganalysis ensemble.",
    )
    parser.add_argument("image", nargs="?", help="image file to analyze")
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    parser.add_argument("--verbose", action="store_true", help="show locked weights and normalized scores")
    parser.add_argument("--json", action="store_true", help="write the result as JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.image:
        parser.error("an image path is required")
    try:
        result = analyze_image(args.image)
    except UserInputError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2

    diagnostics = result["diagnostics"]
    if args.json:
        print(json.dumps(result, indent=2, default=float))
        return 0
    print("Multi-Feature Steganalysis Toolkit\n")
    print(f"Image: {result['image']}\n")
    print(f"Result: {result['label']}")
    print(f"Ensemble Score: {result['ensemble_score']:.4f}")
    print(f"Decision Threshold: {diagnostics['threshold']:.4f}\n")
    print("Detector Results:")
    scores = result["detector_scores"]
    print(f"Chi-square: {scores['chi_square']:.4f}")
    print(f"RS:         {scores['rs']:.4f}")
    print(f"DH:         {scores['dh']:.4f}")
    if args.verbose:
        print("\nLocked weights: Chi-square=0.00, RS=0.70, DH=0.30")
        print(f"Normalized scores: {diagnostics['normalized_scores']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
