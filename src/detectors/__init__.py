"""Detector implementations and shared detector contracts."""

from .base import DetectorResult, load_grayscale
from .chi_square import ChiSquareDetector

__all__ = ["ChiSquareDetector", "DetectorResult", "load_grayscale"]
