"""Tests for the Week 9 reproducible weighted-voting baseline."""

import math

import pytest

from src.ensemble.voting import (
    EQUAL_WEIGHT_BASELINE,
    EnsembleConfig,
    combine_detector_scores,
)


def test_equal_weight_baseline_aligns_scores_and_reports_diagnostics():
    result = combine_detector_scores(
        {"chi_square": 0.8, "rs": 0.2, "dh": 0.2}
    )

    assert result["label"] == "Suspicious"
    assert result["ensemble_score"] == pytest.approx(0.8)
    diagnostics = result["diagnostics"]
    assert diagnostics["normalized_scores"] == {
        "chi_square": 0.8,
        "rs": 0.8,
        "dh": 0.8,
    }
    assert diagnostics["weights"] == {
        "chi_square": pytest.approx(1.0 / 3.0),
        "rs": pytest.approx(1.0 / 3.0),
        "dh": pytest.approx(1.0 / 3.0),
    }
    assert diagnostics["threshold"] == 0.5
    assert diagnostics["configuration"] == "equal_weight_baseline"
    assert diagnostics["calibrated"] is False


def test_baseline_labels_scores_below_threshold_clean():
    result = combine_detector_scores(
        {"chi_square": 0.1, "rs": 0.9, "dh": 0.9}
    )

    assert result["ensemble_score"] == pytest.approx((0.1 + 0.1 + 0.1) / 3.0)
    assert result["label"] == "Clean"


def test_baseline_threshold_is_inclusive_for_suspicious_label():
    result = combine_detector_scores(
        {"chi_square": 0.5, "rs": 0.5, "dh": 0.5}
    )

    assert result["ensemble_score"] == 0.5
    assert result["label"] == "Suspicious"


def test_custom_weighted_configuration_is_applied_reproducibly():
    config = EnsembleConfig(
        chi_square_weight=0.5,
        rs_weight=0.25,
        dh_weight=0.25,
        threshold=0.6,
    )
    scores = {"chi_square": 0.8, "rs": 0.2, "dh": 0.2}

    first = combine_detector_scores(scores, config)
    second = combine_detector_scores(scores, config)

    assert first == second
    assert first["ensemble_score"] == pytest.approx(0.8)
    assert first["label"] == "Suspicious"
    assert first["diagnostics"]["configuration"] == "custom_weighted_configuration"


@pytest.mark.parametrize(
    "config",
    [
        EnsembleConfig(0.5, 0.25, 0.25, 0.5),
    ],
)
def test_valid_configuration_weights_sum_to_one(config):
    assert math.isclose(sum(config.weights), 1.0)


@pytest.mark.parametrize(
    "arguments",
    [
        {"chi_square_weight": 0.5, "rs_weight": 0.25, "dh_weight": 0.2},
        {"chi_square_weight": -0.1, "rs_weight": 0.6, "dh_weight": 0.5},
        {"chi_square_weight": True, "rs_weight": 0.0, "dh_weight": 0.0},
        {"chi_square_weight": float("nan"), "rs_weight": 0.0, "dh_weight": 0.0},
        {"chi_square_weight": float("inf"), "rs_weight": 0.0, "dh_weight": 0.0},
        {"threshold": -0.01},
        {"threshold": 1.01},
        {"threshold": float("nan")},
    ],
)
def test_invalid_configuration_is_rejected(arguments):
    with pytest.raises(ValueError):
        EnsembleConfig(**arguments)


@pytest.mark.parametrize("missing_detector", ["chi_square", "rs", "dh"])
def test_missing_detector_score_is_rejected(missing_detector):
    scores = {"chi_square": 0.3, "rs": 0.3, "dh": 0.3}
    scores.pop(missing_detector)

    with pytest.raises(ValueError, match=missing_detector):
        combine_detector_scores(scores)


def test_invalid_raw_detector_score_is_rejected():
    with pytest.raises(ValueError, match="finite numeric"):
        combine_detector_scores({"chi_square": 0.2, "rs": 1.2, "dh": 0.2})


def test_non_mapping_scores_are_rejected():
    with pytest.raises(ValueError, match="mapping"):
        combine_detector_scores([0.2, 0.2, 0.2])


def test_equal_weight_baseline_is_explicit_and_reusable():
    assert EQUAL_WEIGHT_BASELINE.weights == (
        pytest.approx(1.0 / 3.0),
        pytest.approx(1.0 / 3.0),
        pytest.approx(1.0 / 3.0),
    )
    assert EQUAL_WEIGHT_BASELINE.threshold == 0.5
