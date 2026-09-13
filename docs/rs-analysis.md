# RS Analysis Prototype

## Purpose

RS (regular/singular) analysis is a statistical method that observes how LSB
changes affect local pixel smoothness. This Week 4 detector is a prototype: it
provides an explainable signal for later ensemble calibration, not a calibrated
probability or an embedded-payload estimate.

## Input

`RSAnalysisDetector.analyze(image)` receives preprocessed NumPy image data in
one of the shapes produced by `src.preprocessing.load_image`:

- Grayscale: `(height, width)`
- RGB: `(height, width, 3)`

Pixels must use an integer data type with values from 0 through 255. RGB
channels are analyzed independently so that an RS group never crosses channels.

## Method

Each channel is split into non-overlapping groups of four samples. The
discrimination function is the sum of absolute differences between neighbouring
samples in a group. The detector toggles each sample's LSB and compares the
new discrimination with the original:

- A **regular** group becomes rougher after the flip.
- A **singular** group becomes smoother after the flip.
- An **unchanged** group has equal discrimination before and after the flip.

The RS statistic is:

`(regular_groups - singular_groups) / (regular_groups + singular_groups)`

When no groups are classifiable, the statistic is `0.0`. The prototype score is
the absolute RS statistic, clipped to `[0.0, 1.0]`; higher values indicate
greater suspicion according to the current team score convention.

## Output

```python
{
    "score": 0.0,
    "diagnostics": {
        "regular_groups": 0,
        "singular_groups": 0,
        "unchanged_groups": 0,
        "groups_analyzed": 0,
        "rs_statistic": 0.0,
    },
}
```

## Prototype limitations

- The score has not been calibrated against the clean/stego dataset.
- It uses one all-sample LSB flip and a fixed group size of four.
- It does not estimate payload rate.
- Image texture can influence the statistic, so score normalization and
  ensemble weighting require later empirical validation.
