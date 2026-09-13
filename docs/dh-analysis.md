# Difference Histogram (DH) Analysis Prototype

## Purpose

Difference Histogram (DH) analysis is a statistical method that examines 
the differences between neighboring pixel values in an image. The idea is 
that LSB embedding can make small changes to pixel values, which may change 
the shape and smoothness of the image's difference histogram.

This Week 4 detector is a prototype. It produces a raw, explainable Difference Histogram 
roughness value and diagnostic information for later calibration and ensemble use. 
The current raw DH roughness is not a calibrated probability and does not by itself 
classify an image as clean or stego.

## Input

`analyze_difference_histogram(image_path)` receives a path to an image file and opens the image with Pillow.

The current prototype supports:
- Grayscale `(L)` images
- RGB images

Grayscale images are analyzed as one `L` channel. 
RGB images are separated into `R`, `G`, and `B` channels and each channel is analyzed independently.

Each channel must be a two-dimensional array of pixel values. Before adjacent pixel 
differences are calculated, the channel is converted to `np.int16` so that negative differences 
are preserved correctly.

## Method

For each image channel, difference_histogram(channel) calculates differences between neighboring pixels in two directions:
- Horizontal differences using `np.diff(channel, axis=1)`
- Vertical differences using `np.diff(channel, axis=0)`

The horizontal and vertical difference arrays are flattened and combined into one array.

Because 8-bit image pixels range from `0` through `255`, 
the difference between two neighboring pixels can range from `-255` through `+255`. 
Therefore, the detector builds a **511-bin Difference Histogram**.

The difference values are shifted by `+255` before `np.bincount()` is used:
- Difference `-255` maps to histogram index `0`
- Difference `0` maps to histogram index `255`
- Difference `+255` maps to histogram index `510`

The detector then calls `histogram_roughness(hist)` 
to analyze the central portion of the histogram. 
By default, the central radius is `32`, so the prototype examines pixel differences from `-32` through `+32`.

The central histogram roughness is calculated as:

`sum(abs(diff(central_hist))) / central_total`

This measures how much neighboring histogram bins change relative to the total number of differences in the central region.

If the central region contains no differences, roughness is `0.0`.

The detector also records the proportion of all adjacent-pixel differences that are exactly zero:

`zero_difference_count / histogram_total`

For grayscale images, the final raw DH roughness is the roughness of the single `L` channel.

For RGB images, the final raw DH roughness is the mean of the independently calculated `R`, `G`, and `B` channel roughness values.

## Output

`analyze_difference_histogram(image_path)` returns a dictionary in this form:

```python
{
    "image": "pair_001_clean.png",
    "mode": "RGB",
    "raw_dh_roughness": 0.0,
    "channels": [
        {
            "channel": "R",
            "roughness": 0.0,
            "variation": 0,
            "central_total": 0,
            "central_radius": 32,
            "zero_difference_count": 0,
            "zero_difference_fraction": 0.0,
            "histogram_total": 0
        },
        {
            "channel": "G",
            "roughness": 0.0,
            "variation": 0,
            "central_total": 0,
            "central_radius": 32,
            "zero_difference_count": 0,
            "zero_difference_fraction": 0.0,
            "histogram_total": 0
        },
        {
            "channel": "B",
            "roughness": 0.0,
            "variation": 0,
            "central_total": 0,
            "central_radius": 32,
            "zero_difference_count": 0,
            "zero_difference_fraction": 0.0,
            "histogram_total": 0
        }
    ]
}
```
For a grayscale image, the `channels` list contains only the `L` channel.

The diagnostic values mean:

- **roughness** — normalized amount of bin-to-bin variation in the central Difference Histogram.
- **variation** — total absolute change between neighboring central histogram bins.
- **central_total** — number of pixel differences that fall inside the selected central region.
- **central_radius** — distance from zero used for the central region; currently `32` by default.
- **zero_difference_count** — number of adjacent-pixel comparisons with a difference of exactly `0`.
- **zero_difference_fraction** — proportion of all adjacent-pixel differences that equal `0`.
- **histogram_total** — total number of horizontal and vertical adjacent-pixel differences analyzed for the channel.

## Prototype limitations

- The raw DH roughness has not yet been calibrated against the clean/stego dataset.
- raw_dh_roughness is not a probability or final suspiciousness score.
- Raw roughness is not guaranteed to stay between 0.0 and 1.0; later calibration will place detector outputs onto a common score scale.
- The detector currently uses a fixed default central radius of 32, covering differences from -32 through +32.
- The current feature measures central histogram roughness; it is a transparent project-defined DH feature rather than a complete steganography payload estimator.
- Natural image texture can affect histogram shape and roughness, so clean and stego images must be evaluated empirically before deciding which raw values indicate greater suspicion.
- RGB channel roughness values are currently combined using a simple arithmetic mean.
- The detector does not estimate hidden payload size or extract hidden data.
- Final score direction, normalization, threshold selection, and ensemble weighting require later calibration using the team's clean/stego dataset.
