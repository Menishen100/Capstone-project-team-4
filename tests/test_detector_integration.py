"""Compatibility checks for the three Week 4 detector prototypes."""

from numbers import Real

import numpy as np
import pytest
from PIL import Image

from src.detectors import (
    ChiSquareDetector,
    DifferenceHistogramDetector,
    RSAnalysisDetector,
)
from src.preprocessing import load_image


@pytest.mark.parametrize(
    ("mode", "pixels"),
    [
        ("L", np.arange(64, dtype=np.uint8).reshape(8, 8)),
        (
            "RGB",
            np.dstack(
                [
                    np.arange(64, dtype=np.uint8).reshape(8, 8),
                    np.arange(64, dtype=np.uint8).reshape(8, 8) + 1,
                    np.arange(64, dtype=np.uint8).reshape(8, 8) + 2,
                ]
            ),
        ),
    ],
)
def test_all_detectors_follow_the_common_output_convention(tmp_path, mode, pixels):
    """Each detector accepts shared preprocessing output without changing it."""
    image_path = tmp_path / f"sample-{mode.lower()}.png"
    Image.fromarray(pixels, mode=mode).save(image_path)
    image = load_image(image_path)
    original_image = image.copy()

    detectors = {
        "chi-square": ChiSquareDetector(),
        "rs": RSAnalysisDetector(),
        "difference-histogram": DifferenceHistogramDetector(),
    }

    for detector in detectors.values():
        result = detector.analyze(image)

        assert isinstance(result, dict)
        assert "score" in result
        assert "diagnostics" in result
        assert isinstance(result["score"], Real)
        assert 0.0 <= result["score"] <= 1.0
        assert isinstance(result["diagnostics"], dict)
        np.testing.assert_array_equal(image, original_image)
