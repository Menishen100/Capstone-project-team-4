import numpy as np
import pytest
from PIL import Image

from src.detectors.base import DetectorResult, load_grayscale
from src.detectors.chi_square import ChiSquareDetector


def test_grayscale_and_rgb_inputs_use_common_shape() -> None:
    grayscale = np.arange(64, dtype=np.uint8).reshape(8, 8)
    rgb = np.repeat(grayscale[:, :, None], 3, axis=2)

    assert load_grayscale(grayscale).shape == (8, 8)
    np.testing.assert_array_equal(load_grayscale(rgb), grayscale)


def test_pillow_image_and_png_path_are_supported(tmp_path) -> None:
    image = Image.fromarray(np.full((8, 8), 128, dtype=np.uint8), mode="L")
    path = tmp_path / "sample.png"
    image.save(path)

    np.testing.assert_array_equal(load_grayscale(image), load_grayscale(path))


def test_invalid_image_inputs_fail_clearly() -> None:
    with pytest.raises(ValueError, match="2-D grayscale or 3-D"):
        load_grayscale(np.zeros((8,), dtype=np.uint8))
    with pytest.raises(ValueError, match="at least two pixels"):
        ChiSquareDetector().analyze(np.array([[1]], dtype=np.uint8))


def test_chi_square_returns_standardized_result() -> None:
    image = np.tile(np.arange(256, dtype=np.uint8), (16, 1))

    result = ChiSquareDetector().analyze(image)

    assert isinstance(result, DetectorResult)
    assert 0.0 <= result.score <= 1.0
    assert result.diagnostics["pixels_analyzed"] == image.size
    assert result.diagnostics["score_definition"] == "1 - p_value"
    assert 0.0 <= result.diagnostics["p_value"] <= 1.0


def test_balanced_pair_counts_have_low_suspicion() -> None:
    image = np.repeat(np.arange(256, dtype=np.uint8), 4).reshape(32, 32)

    result = ChiSquareDetector().analyze(image)

    assert result.diagnostics["chi_square_statistic"] == pytest.approx(0.0)
    assert result.diagnostics["p_value"] == pytest.approx(1.0)
    assert result.score == pytest.approx(0.0)
