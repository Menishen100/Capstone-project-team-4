"""Chi-square PoV steganalysis prototype."""

from typing import Any

import numpy as np
from scipy.stats import chi2

from .base import DetectorResult, load_grayscale


class ChiSquareDetector:
    """Estimate LSB replacement suspicion from pair-of-values histograms.

    For each pair (2k, 2k+1), the expected count is the pair's average count.
    The statistic tests whether observed pair counts are unusually unequal.
    The score is ``1 - p_value`` so that larger values consistently indicate
    greater suspicion for the ensemble planned in later weeks.
    """

    name = "chi_square"

    def analyze(self, image: Any) -> DetectorResult:
        pixels = load_grayscale(image).ravel()
        if pixels.size < 2:
            raise ValueError("chi-square analysis requires at least two pixels")

        histogram = np.bincount(pixels, minlength=256).astype(float)
        observed_a = histogram[0::2]
        observed_b = histogram[1::2]
        totals = observed_a + observed_b
        valid = totals > 0
        expected = totals[valid] / 2.0
        statistic = float(
            np.sum(((observed_a[valid] - expected) ** 2 + (observed_b[valid] - expected) ** 2) / expected)
        )
        degrees_of_freedom = max(int(np.count_nonzero(valid)) - 1, 1)
        p_value = float(chi2.sf(statistic, degrees_of_freedom))
        score = float(np.clip(1.0 - p_value, 0.0, 1.0))

        return DetectorResult(
            score=score,
            diagnostics={
                "p_value": p_value,
                "chi_square_statistic": statistic,
                "degrees_of_freedom": degrees_of_freedom,
                "pixels_analyzed": int(pixels.size),
                "nonempty_pov_pairs": int(np.count_nonzero(valid)),
                "score_definition": "1 - p_value",
            },
        )
