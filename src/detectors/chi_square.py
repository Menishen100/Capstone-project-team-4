"""Chi-square pair-of-values prototype for LSB steganalysis."""

from typing import Any

import numpy as np
from scipy.stats import chisquare


class ChiSquareDetector:
    """Detect possible LSB replacement using pixel-value pairs."""

    def analyze(self, image: Any) -> dict[str, Any]:
        pixels = np.asarray(image)

        if pixels.size < 2:
            raise ValueError("chi-square analysis requires at least two pixels")

        if not np.issubdtype(pixels.dtype, np.integer):
            raise ValueError("image pixels must use an integer data type")

        if np.any(pixels < 0) or np.any(pixels > 255):
            raise ValueError("image pixel values must be in the range 0 to 255")

        histogram = np.bincount(pixels.ravel(), minlength=256)

        observed = []
        expected = []

        for value in range(0, 256, 2):
            pair_total = histogram[value] + histogram[value + 1]

            if pair_total == 0:
                continue

            observed.extend([histogram[value], histogram[value + 1]])
            expected.extend([pair_total / 2, pair_total / 2])

        statistic, p_value = chisquare(observed, expected)

        return {
            "score": float(p_value),
            "diagnostics": {
                "chi_square": float(statistic),
                "p_value": float(p_value),
            },
        }