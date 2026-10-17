"""Tests for detector score-direction alignment."""

import math

import pytest

from src.ensemble.normalization import normalize_chi_square, normalize_rs, normalize_dh


@pytest.mark.parametrize("score", [0.0, 0.5, 1.0])
def test_chi_square_is_bounded_and_direction_is_unchanged(score):
    result = normalize_chi_square(score)

    assert result == score
    assert 0.0 <= result <= 1.0


@pytest.mark.parametrize(
    ("score", "expected"), [(0.0, 1.0), (0.5, 0.5), (1.0, 0.0)]
)
def test_rs_is_inverted_and_bounded(score, expected):
    result = normalize_rs(score)

    assert result == expected
    assert 0.0 <= result <= 1.0


@pytest.mark.parametrize(
    ("score", "expected"), [(0.0, 1.0), (0.25, 0.75), (0.5, 0.5), (1.0, 0.0)]
)
def test_dh_is_inverted_and_bounded(score, expected):
    result = normalize_dh(score)

    assert result == expected
    assert 0.0 <= result <= 1.0


def test_normalization_is_deterministic():
    for normalize in (normalize_chi_square, normalize_rs, normalize_dh):
        assert normalize(0.37) == normalize(0.37)


def test_higher_chi_square_input_remains_higher():
    assert normalize_chi_square(0.8) > normalize_chi_square(0.2)


def test_lower_rs_input_becomes_more_suspicious():
    assert normalize_rs(0.2) > normalize_rs(0.8)


def test_lower_dh_input_becomes_more_suspicious():
    assert normalize_dh(0.2) > normalize_dh(0.8)


@pytest.mark.parametrize("normalize", [normalize_chi_square, normalize_rs, normalize_dh])
@pytest.mark.parametrize(
    "score", [-0.01, 1.01, float("nan"), float("inf"), -float("inf"), True, "0.5"]
)
def test_invalid_scores_are_rejected(normalize, score):
    with pytest.raises(ValueError):
        normalize(score)
