"""Consistent image loading for statistical steganalysis detectors."""

from pathlib import Path

import numpy as np
from PIL import Image

SUPPORTED_MODES = ("L", "RGB")


def load_image(image_path: str | Path) -> np.ndarray:
    """Load an image as an unchanged grayscale or RGB NumPy array.

    Images already in ``L`` or ``RGB`` mode retain that mode. Other Pillow
    modes are converted to RGB so every detector receives a predictable array
    shape. This function deliberately does not resize, filter, normalize, or
    otherwise modify pixel values.

    Args:
        image_path: Path to an image that Pillow can open.

    Returns:
        A NumPy array with shape ``(height, width)`` for grayscale images or
        ``(height, width, 3)`` for RGB images.

    Raises:
        FileNotFoundError: If ``image_path`` does not identify an existing
            file.
    """
    path = Path(image_path)
    if not path.is_file():
        raise FileNotFoundError(f"Image file not found: {path}")

    with Image.open(path) as opened_image:
        image = (
            opened_image.copy()
            if opened_image.mode in SUPPORTED_MODES
            else opened_image.convert("RGB")
        )

    return np.asarray(image)
