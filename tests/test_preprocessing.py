"""Unit tests for shared image preprocessing."""

import numpy as np
import pytest
from PIL import Image

from src.preprocessing import load_image


def test_load_image_preserves_rgb_image(tmp_path):
    """RGB images remain three-channel uint8 arrays."""
    pixels = np.array(
        [[[1, 2, 3], [4, 5, 6]], [[7, 8, 9], [10, 11, 12]]], dtype=np.uint8
    )
    image_path = tmp_path / "rgb.png"
    Image.fromarray(pixels, mode="RGB").save(image_path)

    loaded = load_image(image_path)

    assert isinstance(loaded, np.ndarray)
    assert loaded.shape == (2, 2, 3)
    assert loaded.dtype == np.uint8
    np.testing.assert_array_equal(loaded, pixels)


def test_load_image_preserves_grayscale_image(tmp_path):
    """Grayscale images remain two-dimensional uint8 arrays."""
    pixels = np.array([[0, 127], [200, 255]], dtype=np.uint8)
    image_path = tmp_path / "grayscale.png"
    Image.fromarray(pixels, mode="L").save(image_path)

    loaded = load_image(image_path)

    assert isinstance(loaded, np.ndarray)
    assert loaded.shape == (2, 2)
    assert loaded.dtype == np.uint8
    np.testing.assert_array_equal(loaded, pixels)


def test_load_image_raises_for_missing_file(tmp_path):
    """An absent path raises the documented error before Pillow is called."""
    with pytest.raises(FileNotFoundError):
        load_image(tmp_path / "does-not-exist.png")


def test_load_image_converts_unsupported_mode_to_rgb(tmp_path):
    """Unsupported Pillow modes are converted to a three-channel RGB array."""
    pixels = np.array([[[10, 20, 30, 40], [50, 60, 70, 80]]], dtype=np.uint8)
    source_image = Image.fromarray(pixels, mode="RGBA")
    image_path = tmp_path / "rgba.png"
    source_image.save(image_path)

    loaded = load_image(image_path)

    assert isinstance(loaded, np.ndarray)
    assert loaded.shape == (1, 2, 3)
    assert loaded.dtype == np.uint8
    np.testing.assert_array_equal(loaded, np.asarray(source_image.convert("RGB")))
