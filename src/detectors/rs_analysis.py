"""RS (regular/singular) analysis prototype for LSB steganalysis.

The detector compares each pixel group's local roughness before and after an
LSB flip.  It reports the regular/singular imbalance as an uncalibrated,
bounded suspiciousness score.
"""

from typing import Any

import numpy as np

from .base_detector import BaseDetector


class RSAnalysisDetector(BaseDetector):
    """Analyze LSB-flip effects on groups of four image samples."""

    _GROUP_SIZE = 4

    @staticmethod
    def _validate_image(image: Any) -> np.ndarray:
        """Validate preprocessing output and return its samples as uint8."""
        pixels = np.asarray(image)

        if pixels.ndim not in (2, 3) or (pixels.ndim == 3 and pixels.shape[2] != 3):
            raise ValueError("image must be a grayscale (H, W) or RGB (H, W, 3) array")
        if not np.issubdtype(pixels.dtype, np.integer):
            raise ValueError("image pixels must use an integer data type")
        if np.any(pixels < 0) or np.any(pixels > 255):
            raise ValueError("image pixel values must be in the range 0 to 255")

        return pixels.astype(np.uint8, copy=False)

    @staticmethod
    def _discrimination(group: np.ndarray) -> int:
        """Return a group's sum of adjacent absolute differences."""
        values = group.astype(np.int16, copy=False)
        return int(np.abs(np.diff(values)).sum())

    def analyze(self, image: Any) -> dict[str, Any]:
        """Return an RS-style suspiciousness score and named diagnostics.

        Samples are read in non-overlapping groups of four. A group is
        *regular* when toggling every sample's LSB increases the group
        discrimination and *singular* when it decreases it. RGB arrays are
        evaluated channel-by-channel, avoiding groups that mix colour channels.
        """
        pixels = self._validate_image(image)
        channels = (pixels,) if pixels.ndim == 2 else np.moveaxis(pixels, -1, 0)

        regular = singular = unchanged = groups_analyzed = 0
        for channel in channels:
            samples = channel.ravel()
            group_count = samples.size // self._GROUP_SIZE
            groups_analyzed += group_count

            for group in samples[: group_count * self._GROUP_SIZE].reshape(
                group_count, self._GROUP_SIZE
            ):
                original = self._discrimination(group)
                # XOR safely toggles an LSB for the complete uint8 range.
                flipped = self._discrimination(np.bitwise_xor(group, np.uint8(1)))

                if flipped > original:
                    regular += 1
                elif flipped < original:
                    singular += 1
                else:
                    unchanged += 1

        classified_groups = regular + singular
        rs_statistic = (
            (regular - singular) / classified_groups if classified_groups else 0.0
        )

        return {
            "score": float(np.clip(abs(rs_statistic), 0.0, 1.0)),
            "diagnostics": {
                "regular_groups": regular,
                "singular_groups": singular,
                "unchanged_groups": unchanged,
                "groups_analyzed": groups_analyzed,
                "rs_statistic": float(rs_statistic),
            },
        }
