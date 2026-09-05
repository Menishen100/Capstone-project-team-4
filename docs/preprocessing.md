# Image Preprocessing Rules

## Purpose

The preprocessing module provides consistent image handling for all project
detectors. A detector receives a predictable NumPy array without hidden image
changes before it performs its own statistical analysis.

## Supported modes

- Grayscale (`L`)
- RGB (`RGB`)

## Rules

- `src.preprocessing.load_image` accepts a path and verifies that it exists.
- Pillow loads the image, and NumPy arrays are passed to statistical detectors.
- Grayscale and RGB images are preserved in their original modes.
- Any other Pillow image mode is converted to RGB.
- No resizing, filtering, normalization, or other pixel-changing preprocessing
  occurs unless the team explicitly changes this design later.

These rules keep the Chi-square, RS, and Difference Histogram detectors
compatible with the same pipeline while allowing each detector to calculate its
own statistics.

## Detector API convention

Every detector implements `analyze(image)`, where `image` is the preprocessed
NumPy array returned by `load_image`. The method returns a dictionary with this
structure:

```python
{
    "score": 0.0,          # float from 0.0 to 1.0
    "diagnostics": {...},  # detector-specific statistical information
}
```

- `score` is a normalized suspiciousness score between `0.0` and `1.0`.
- Higher scores always mean the image is more suspicious of steganographic
  modification.
- `diagnostics` holds the named statistical values needed to interpret that
  detector's result.
