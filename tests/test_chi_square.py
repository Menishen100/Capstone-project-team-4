import numpy as np
import pytest

from src.detectors.chi_square import ChiSquareDetector


def test_chi_square_returns_valid_result():
    image = np.random.default_rng(7).integers(
        0, 256, (100, 100), dtype=np.uint8
    )

    result = ChiSquareDetector().analyze(image)

    assert 0.0 <= result["score"] <= 1.0
    assert "chi_square" in result["diagnostics"]
    assert "p_value" in result["diagnostics"]
    assert result["diagnostics"]["value_pairs_analyzed"] > 0
    assert result["diagnostics"]["samples_analyzed"] == image.size


def test_balanced_value_pairs_return_high_score():
    image = np.repeat(
        np.arange(256, dtype=np.uint8), 4
    ).reshape(32, 32)

    result = ChiSquareDetector().analyze(image)

    assert result["diagnostics"]["chi_square"] == pytest.approx(0.0)
    assert result["diagnostics"]["p_value"] == pytest.approx(1.0)
    assert result["score"] == pytest.approx(1.0)


def test_too_small_image_is_rejected():
    with pytest.raises(ValueError, match="at least two pixels"):
        ChiSquareDetector().analyze(
            np.array([[1]], dtype=np.uint8)
        )


@pytest.mark.parametrize(
    "image",
    [
        np.arange(64, dtype=np.uint8).reshape(8, 8),
        np.dstack([np.arange(64, dtype=np.uint8).reshape(8, 8)] * 3),
    ],
)
def test_grayscale_and_rgb_inputs_have_sane_diagnostics(image):
    result = ChiSquareDetector().analyze(image)
    diagnostics = result["diagnostics"]

    assert isinstance(result["score"], float)
    assert 0.0 <= result["score"] <= 1.0
    assert isinstance(diagnostics["chi_square"], float)
    assert diagnostics["chi_square"] >= 0.0
    assert isinstance(diagnostics["p_value"], float)
    assert 0.0 <= diagnostics["p_value"] <= 1.0
    assert isinstance(diagnostics["value_pairs_analyzed"], int)
    assert diagnostics["value_pairs_analyzed"] > 0
    assert diagnostics["samples_analyzed"] == image.size


@pytest.mark.parametrize(
    "image, message",
    [
        (np.array([[1.0, 2.0]], dtype=np.float32), "integer"),
        (np.array([[0, 256]], dtype=np.int16), "range"),
        (np.array([[0, -1]], dtype=np.int16), "range"),
    ],
)
def test_invalid_pixel_data_is_rejected(image, message):
    with pytest.raises(ValueError, match=message):
        ChiSquareDetector().analyze(image)


def test_result_is_deterministic_and_input_is_not_modified():
    image = np.arange(64, dtype=np.uint8).reshape(8, 8)
    original = image.copy()
    detector = ChiSquareDetector()

    first = detector.analyze(image)
    second = detector.analyze(image)

    assert first == second
    np.testing.assert_array_equal(image, original)
