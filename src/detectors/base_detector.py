"""Common contract for statistical steganalysis detectors."""

from abc import ABC, abstractmethod
from typing import Any

import numpy as np


class BaseDetector(ABC):
    """Define the result convention shared by all image detectors.

    Implementations receive a preprocessed NumPy image array from
    :func:`src.preprocessing.load_image` and return a dictionary with a
    normalized suspiciousness ``score`` and detector-specific ``diagnostics``.
    A score of 0.0 represents the lowest suspicion and 1.0 the highest.
    """

    @abstractmethod
    def analyze(self, image: np.ndarray) -> dict[str, Any]:
        """Analyze a preprocessed image and return its steganalysis result.

        Args:
            image: A NumPy array in grayscale ``(height, width)`` or RGB
                ``(height, width, 3)`` form.

        Returns:
            A dictionary with this shape::

                {
                    "score": float,       # suspiciousness in [0.0, 1.0]
                    "diagnostics": {...}, # detector-specific statistics
                }

            Higher ``score`` values must always indicate greater suspicion of
            steganographic modification.
        """
