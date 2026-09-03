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