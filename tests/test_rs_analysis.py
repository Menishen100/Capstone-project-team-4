"""Unit tests for the RS analysis prototype."""

import numpy as np
import pytest

from src.detectors.rs_analysis import RSAnalysisDetector


def assert_detector_result(result: dict) -> None:
    """Assert the common detector contract and RS-specific diagnostics."""
    assert set(result) == {"score", "diagnostics"}
    assert isinstance(result["score"], float)
    assert 0.0 <= result["score"] <= 1.0
    assert {
        "regular_groups",
        "singular_groups",
        "unchanged_groups",
        "groups_analyzed",
        "rs_statistic",
        "channels_analyzed",
        "samples_analyzed",
    } <= set(result["diagnostics"])


def test_analyzes_grayscale_image() -> None:
    image = np.arange(64, dtype=np.uint8).reshape(8, 8)

    result = RSAnalysisDetector().analyze(image)

    assert_detector_result(result)
    assert result["diagnostics"]["groups_analyzed"] == 16
    assert result["diagnostics"]["channels_analyzed"] == 1
    assert result["diagnostics"]["samples_analyzed"] == 64


def test_analyzes_rgb_image() -> None:
    channel = np.arange(64, dtype=np.uint8).reshape(8, 8)
    image = np.dstack((channel, channel + 1, channel + 2))

    result = RSAnalysisDetector().analyze(image)

    assert_detector_result(result)
    assert result["diagnostics"]["groups_analyzed"] == 48
    assert result["diagnostics"]["channels_analyzed"] == 3
    assert result["diagnostics"]["samples_analyzed"] == 192


def test_score_is_repeatable_for_deterministic_input() -> None:
    image = np.arange(100, dtype=np.uint8).reshape(10, 10)
    detector = RSAnalysisDetector()

    assert detector.analyze(image) == detector.analyze(image.copy())


def test_image_too_small_for_a_group_returns_safe_empty_result() -> None:
    result = RSAnalysisDetector().analyze(np.array([[10, 20, 30]], dtype=np.uint8))

    assert_detector_result(result)
    assert result["score"] == 0.0
    assert result["diagnostics"]["groups_analyzed"] == 0


@pytest.mark.parametrize(
    "image, message",
    [
        (np.zeros((4, 4), dtype=np.float32), "integer"),
        (np.full((4, 4), 256, dtype=np.int16), "range"),
        (np.full((4, 4), -1, dtype=np.int16), "range"),
    ],
)
def test_invalid_pixel_data_is_rejected(image, message) -> None:
    with pytest.raises(ValueError, match=message):
        RSAnalysisDetector().analyze(image)


def test_group_diagnostics_are_consistent_and_input_is_not_modified() -> None:
    image = np.arange(99, dtype=np.uint8).reshape(9, 11)
    original = image.copy()

    result = RSAnalysisDetector().analyze(image)
    diagnostics = result["diagnostics"]

    assert (
        diagnostics["regular_groups"]
        + diagnostics["singular_groups"]
        + diagnostics["unchanged_groups"]
        == diagnostics["groups_analyzed"]
    )
    assert diagnostics["samples_analyzed"] == diagnostics["groups_analyzed"] * 4
    assert -1.0 <= diagnostics["rs_statistic"] <= 1.0
    np.testing.assert_array_equal(image, original)


def test_unsupported_shape_is_rejected() -> None:
    with pytest.raises(ValueError, match="grayscale"):
        RSAnalysisDetector().analyze(np.zeros((4, 4, 2), dtype=np.uint8))
