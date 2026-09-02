"""Shared image loading and detector result definitions."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, UnidentifiedImageError


@dataclass(frozen=True)
class DetectorResult:
    """Standard detector output; larger scores always mean more suspicion."""

    score: float
    diagnostics: dict[str, Any]

    def __post_init__(self) -> None:
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("detector score must be in the range [0, 1]")


def load_grayscale(image: str | Path | Image.Image | np.ndarray) -> np.ndarray:
    """Load an image as a 2-D uint8 grayscale array.

    RGB input uses Pillow's documented luminance conversion. Array input may be
    2-D grayscale or 3-D RGB/RGBA; floating-point values must already be in
    the 0..255 range.
    """
    if isinstance(image, (str, Path)):
        try:
            with Image.open(image) as opened:
                return np.asarray(opened.convert("L"), dtype=np.uint8).copy()
        except (UnidentifiedImageError, OSError) as exc:
            raise ValueError(f"unable to read image: {image}") from exc

    if isinstance(image, Image.Image):
        return np.asarray(image.convert("L"), dtype=np.uint8).copy()

    array = np.asarray(image)
    if array.ndim == 3:
        if array.shape[2] not in (3, 4):
            raise ValueError("color arrays must have 3 or 4 channels")
        array = np.asarray(Image.fromarray(_as_uint8(array)).convert("L"))
    elif array.ndim != 2:
        raise ValueError("image input must be a 2-D grayscale or 3-D color array")

    return _as_uint8(array).copy()


def _as_uint8(array: np.ndarray) -> np.ndarray:
    if not np.issubdtype(array.dtype, np.number):
        raise ValueError("image array must contain numeric values")
    if not np.all(np.isfinite(array)) or np.min(array) < 0 or np.max(array) > 255:
        raise ValueError("image values must be finite and in the range 0..255")
    return np.rint(array).astype(np.uint8)
