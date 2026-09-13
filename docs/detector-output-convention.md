# Detector Output Convention

## Purpose

Every standalone detector uses the same interface so it can receive shared
image preprocessing output and later participate in the team's ensemble
without changing its public result structure.

## Required interface

Each detector exposes `analyze(image)`, where `image` is preprocessed NumPy
image data from `src.preprocessing.load_image`. The method returns:

```python
{
    "score": float,
    "diagnostics": dict,
}
```

The input is a grayscale `(height, width)` array or an RGB
`(height, width, 3)` array. Detectors must not modify that input.

## Score rules

- `score` is at least `0.0` and at most `1.0`.
- Higher values indicate greater suspicion of steganographic modification.
- `diagnostics` contains the named statistical values that explain a specific
  detector result.

## Current standalone detectors

- Chi-square
- RS Analysis
- Difference Histogram

All three detectors can analyze the same grayscale or RGB preprocessing output
and return the common result structure. The cross-detector integration test
verifies this contract and verifies that detector calls leave the input array
unchanged.

## Prototype score interpretation

Week 4 scores are prototype suspiciousness scores, not calibrated
probabilities. The Difference Histogram adapter uses the monotonic bounded
mapping `raw_roughness / (1 + raw_roughness)` so its existing raw roughness
feature can participate in the shared interface. Final score normalization,
calibration, thresholds, and ensemble weighting remain later planned work and
must be established from empirical clean/stego evaluation data.
