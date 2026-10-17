"""Explainable weighted voting for the three statistical detectors.

The Week 9 default is an equal-weight baseline.  Its score is a reproducible
combination of direction-aligned detector outputs, not a calibrated probability.
Final weights and the operating threshold remain a Week 10 validation task.
"""

from dataclasses import dataclass
import math
from numbers import Real
from typing import Mapping

from src.ensemble.normalization import (
    normalize_chi_square,
    normalize_dh,
    normalize_rs,
)


DETECTOR_NAMES = ("chi_square", "rs", "dh")


@dataclass(frozen=True)
class EnsembleConfig:
    """Configuration for a weighted three-detector ensemble."""

    chi_square_weight: float = 1.0 / 3.0
    rs_weight: float = 1.0 / 3.0
    dh_weight: float = 1.0 / 3.0
    threshold: float = 0.5

    def __post_init__(self) -> None:
        weights = self.weights
        if any(
            isinstance(weight, bool)
            or not isinstance(weight, Real)
            or not math.isfinite(float(weight))
            for weight in weights
        ):
            raise ValueError("ensemble weights must be finite numeric values")
        if any(float(weight) < 0.0 for weight in weights):
            raise ValueError("ensemble weights must be non-negative")
        if abs(sum(float(weight) for weight in weights) - 1.0) > 1e-9:
            raise ValueError("ensemble weights must sum to 1.0")
        if (
            isinstance(self.threshold, bool)
            or not isinstance(self.threshold, Real)
            or not math.isfinite(float(self.threshold))
            or not 0.0 <= float(self.threshold) <= 1.0
        ):
            raise ValueError("ensemble threshold must be a finite numeric value in [0, 1]")

    @property
    def weights(self) -> tuple[float, float, float]:
        """Return weights in the documented detector order."""
        return (
            self.chi_square_weight,
            self.rs_weight,
            self.dh_weight,
        )


EQUAL_WEIGHT_BASELINE = EnsembleConfig()


def _read_raw_score(scores: Mapping[str, Real], detector: str) -> Real:
    """Return one required raw detector score with a clear missing-key error."""
    try:
        return scores[detector]
    except KeyError as error:
        raise ValueError(f"missing required detector score: {detector}") from error


def combine_detector_scores(
    scores: Mapping[str, Real],
    config: EnsembleConfig = EQUAL_WEIGHT_BASELINE,
) -> dict[str, object]:
    """Combine raw detector scores and return an explainable baseline decision.

    ``scores`` must contain the bounded raw score for ``chi_square``, ``rs``,
    and ``dh``.  The function direction-aligns RS and DH before applying the
    configured weights.  A score at or above the configured threshold receives
    the baseline label ``Suspicious``; otherwise it receives ``Clean``.
    """
    if not isinstance(scores, Mapping):
        raise ValueError("scores must be a mapping of detector names to scores")
    if not isinstance(config, EnsembleConfig):
        raise ValueError("config must be an EnsembleConfig")

    raw_scores = {
        detector: _read_raw_score(scores, detector)
        for detector in DETECTOR_NAMES
    }
    normalized_scores = {
        "chi_square": normalize_chi_square(raw_scores["chi_square"]),
        "rs": normalize_rs(raw_scores["rs"]),
        "dh": normalize_dh(raw_scores["dh"]),
    }
    weights = dict(zip(DETECTOR_NAMES, config.weights, strict=True))
    contributions = {
        detector: normalized_scores[detector] * float(weights[detector])
        for detector in DETECTOR_NAMES
    }
    ensemble_score = sum(contributions.values())
    threshold = float(config.threshold)

    return {
        "label": "Suspicious" if ensemble_score >= threshold else "Clean",
        "ensemble_score": ensemble_score,
        "diagnostics": {
            "raw_scores": raw_scores,
            "normalized_scores": normalized_scores,
            "weights": weights,
            "weighted_contributions": contributions,
            "threshold": threshold,
            "configuration": "equal_weight_baseline"
            if config == EQUAL_WEIGHT_BASELINE
            else "custom_weighted_configuration",
            "calibrated": False,
        },
    }
