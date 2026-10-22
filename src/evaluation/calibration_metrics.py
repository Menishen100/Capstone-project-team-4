"""Metric and integrity helpers for Week 10 ensemble calibration.

Scores passed to ``ensemble_score`` must already be normalized to [0, 1].
RS uses the Week 9 convention that lower raw RS scores indicate suspicion, so
it is inverted here before weighted voting. Chi-square p-values must first be
converted to suspiciousness as ``1 - p_value`` by the score preparation step.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping, Sequence
from typing import Any


LABELS = {"clean", "stego"}
WEIGHT_KEYS = ("chi_weight", "rs_weight", "dh_weight")


def _labels(values: Iterable[str]) -> list[str]:
    result = [str(value).strip().lower() for value in values]
    if not result:
        raise ValueError("labels must not be empty")
    invalid = set(result) - LABELS
    if invalid:
        raise ValueError(f"labels must be clean/stego; got {sorted(invalid)}")
    return result


def predictions_from_scores(scores: Iterable[float], threshold: float) -> list[str]:
    """Classify score >= threshold as stego, else clean."""
    values = [float(value) for value in scores]
    if not values or any(not math.isfinite(value) for value in values):
        raise ValueError("scores must be a non-empty sequence of finite values")
    if not math.isfinite(float(threshold)) or not 0 <= threshold <= 1:
        raise ValueError("threshold must be in [0, 1]")
    if any(not 0 <= value <= 1 for value in values):
        raise ValueError("scores must be in [0, 1]")
    return ["stego" if value >= threshold else "clean" for value in values]


def classification_metrics(y_true: Iterable[str], y_pred: Iterable[str]) -> dict[str, float]:
    """Return binary metrics with stego as the positive class (zero-safe)."""
    truth, predicted = _labels(y_true), _labels(y_pred)
    if len(truth) != len(predicted):
        raise ValueError("true and predicted labels must have equal length")
    tp = sum(a == "stego" and b == "stego" for a, b in zip(truth, predicted))
    tn = sum(a == "clean" and b == "clean" for a, b in zip(truth, predicted))
    fp = sum(a == "clean" and b == "stego" for a, b in zip(truth, predicted))
    fn = sum(a == "stego" and b == "clean" for a, b in zip(truth, predicted))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"accuracy": (tp + tn) / len(truth), "precision": precision,
            "recall": recall, "f1": f1}


def validate_weights(weights: Mapping[str, float], tolerance: float = 1e-9) -> None:
    """Reject incomplete, negative, non-finite, or non-normalized weights."""
    if set(weights) != set(WEIGHT_KEYS):
        raise ValueError(f"weights must contain exactly {WEIGHT_KEYS}")
    values = [float(weights[key]) for key in WEIGHT_KEYS]
    if any(not math.isfinite(value) or value < 0 for value in values):
        raise ValueError("weights must be finite and non-negative")
    if not math.isclose(sum(values), 1.0, abs_tol=tolerance):
        raise ValueError("weights must sum to 1")


def ensemble_score(chi: float, rs_raw: float, dh: float,
                   weights: Mapping[str, float]) -> float:
    """Combine normalized inputs, inverting RS before the weighted vote."""
    validate_weights(weights)
    values = (float(chi), float(rs_raw), float(dh))
    if any(not math.isfinite(v) or not 0 <= v <= 1 for v in values):
        raise ValueError("normalized detector inputs must be finite and in [0, 1]")
    return (weights["chi_weight"] * values[0]
            + weights["rs_weight"] * (1 - values[1])
            + weights["dh_weight"] * values[2])


def verify_selected_configuration(selected: Mapping[str, Any],
                                  result_rows: Sequence[Mapping[str, Any]]) -> None:
    """Ensure the selected weight/threshold tuple is an actual result row."""
    keys = (*WEIGHT_KEYS, "threshold")
    try:
        target = tuple(float(selected[key]) for key in keys)
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("selected configuration is incomplete or non-numeric") from exc
    validate_weights({key: selected[key] for key in WEIGHT_KEYS})
    if not 0 <= target[-1] <= 1:
        raise ValueError("threshold must be in [0, 1]")
    for row in result_rows:
        try:
            candidate = tuple(float(row[key]) for key in keys)
        except (KeyError, TypeError, ValueError):
            continue
        if all(math.isclose(a, b, abs_tol=1e-9) for a, b in zip(target, candidate)):
            return
    raise ValueError("selected configuration does not exist in grid-search results")


def validation_rows(rows: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    """Accept calibration rows only when every row is explicitly validation."""
    if not rows:
        raise ValueError("validation rows must not be empty")
    if any(row.get("split") != "validation" for row in rows):
        raise ValueError("only validation rows are permitted")
    return list(rows)
