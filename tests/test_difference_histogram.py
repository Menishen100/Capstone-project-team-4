import numpy as np
import pytest
from PIL import Image

from src.detectors.difference_histogram import(
    difference_histogram,
    histogram_roughness,
    analyze_difference_histogram,
    DifferenceHistogramDetector,
)


# ---------------------------------------------------------
# Tests for difference_histogram()
# ---------------------------------------------------------

def test_histogram_has_511_bins():
    channel = np.array([
        [10, 11, 12],
        [10, 11, 12],
        [10, 11, 12]
    ], dtype = np.uint8)

    hist = difference_histogram(channel)

    assert len(hist) == 511


def test_histogram_total_difference_count():
    channel = np.array([
        [10, 11, 12],
        [10, 11, 12],
        [10, 11, 12]
    ], dtype = np.uint8)

    hist = difference_histogram(channel)

    # Horizontal:
    # 3 rows × 2 comparisons = 6
    #
    # Vertical:
    # 2 row gaps × 3 columns = 6
    #
    # Total = 12
    assert hist.sum() == 12


def test_zero_difference_count():
    channel = np.array([
        [10, 11, 12],
        [10, 11, 12],
        [10, 11, 12]
    ], dtype = np.uint8)

    hist = difference_histogram(channel)

    # All 6 vertical differences are 0.
    # Difference 0 maps to index 255.
    assert hist[255] == 6


def test_positive_one_difference_count():
    channel = np.array([
        [10, 11, 12],
        [10, 11, 12],
        [10, 11, 12]
    ], dtype = np.uint8)

    hist = difference_histogram(channel)

    # Every horizontal difference is +1.
    # There are 6 of them.
    #
    # +1 + 255 = index 256
    assert hist[256] == 6


def test_negative_difference_is_preserved():
    channel = np.array([
        [20, 10]
    ], dtype = np.uint8)

    hist = difference_histogram(channel)

    # 10 - 20 = -10
    #
    # -10 + 255 = index 245
    assert hist[245] == 1
    assert hist.sum() == 1


def test_rejects_non_2d_channel():
    channel = np.zeros(
        (3, 3, 3),
        dtype = np.uint8
    )

    with pytest.raises(ValueError):
        difference_histogram(channel)


def test_histogram_rejects_float_dtype():
    channel = np.zeros(
        (3, 3),
        dtype = np.float32
    )

    with pytest.raises(ValueError):
        difference_histogram(channel)


def test_histogram_rejects_negative_values():
    channel = np.zeros(
        (3, 3),
        dtype = np.int16
    )

    channel[0, 0] = -1

    with pytest.raises(ValueError):
        difference_histogram(channel)


def test_histogram_rejects_values_above_255():
    channel = np.zeros(
        (3, 3),
        dtype = np.int16
    )

    channel[0, 0] = 256

    with pytest.raises(ValueError):
        difference_histogram(channel)


# ---------------------------------------------------------
# Tests for histogram_roughness()
# ---------------------------------------------------------

def test_uniform_image_statistics():
    channel = np.array([
        [100, 100, 100],
        [100, 100, 100],
        [100, 100, 100]
    ], dtype = np.uint8)

    hist = difference_histogram(channel)
    result = histogram_roughness(hist)

    # Every adjacent difference is zero.
    assert result["histogram_total"] == 12
    assert result["zero_difference_count"] == 12
    assert result["zero_difference_fraction"] == pytest.approx(1.0)

    # All differences are inside -32...+32.
    assert result["central_total"] == 12

    # One spike at difference 0 produces:
    # rise of 12 + fall of 12 = variation 24.
    assert result["variation"] == 24

    # 24 / 12 = 2.0 raw roughness.
    assert result["roughness"] == pytest.approx(2.0)


def test_default_central_radius():
    hist = np.zeros(511, dtype = int)

    result = histogram_roughness(hist)

    assert result["central_radius"] == 32


def test_rejects_wrong_histogram_length():
    hist = np.zeros(100, dtype = int)

    with pytest.raises(ValueError):
        histogram_roughness(hist)


def test_rejects_non_1d_histogram():
    hist = np.zeros(
        (511, 1),
        dtype = int
    )

    with pytest.raises(ValueError):
        histogram_roughness(hist)


@pytest.mark.parametrize(
    "central_radius",
    [
        32.5,
        True
    ]
)
def test_rejects_invalid_central_radius_type(central_radius):
    hist = np.zeros(
        511,
        dtype = int
    )

    with pytest.raises(ValueError):
        histogram_roughness(
            hist,
            central_radius = central_radius
        )


def test_rejects_negative_central_radius():
    hist = np.zeros(511, dtype = int)

    with pytest.raises(ValueError):
        histogram_roughness(
            hist,
            central_radius=-1
        )


def test_rejects_too_large_central_radius():
    hist = np.zeros(511, dtype = int)

    with pytest.raises(ValueError):
        histogram_roughness(
            hist,
            central_radius=256
        )


# ---------------------------------------------------------
# Tests for analyze_difference_histogram()
# ---------------------------------------------------------

def test_analyze_grayscale_image(tmp_path):
    pixels = np.array([
        [10, 11, 12],
        [10, 11, 12],
        [10, 11, 12]
    ], dtype = np.uint8)

    image_path = tmp_path / "test_grayscale.png"

    image = Image.fromarray(pixels)
    image.save(image_path)

    result = analyze_difference_histogram(
        image_path
    )

    assert result["image"] == "test_grayscale.png"
    assert result["mode"] == "L"

    # Grayscale should have one channel.
    assert len(result["channels"]) == 1

    assert result["channels"][0]["channel"] == "L"

    # With one channel, image-level roughness should
    # equal the L-channel roughness.
    assert result["raw_dh_roughness"] == pytest.approx(
        result["channels"][0]["roughness"]
    )


def test_analyze_rgb_image(tmp_path):
    pixels = np.zeros(
        (3, 3, 3),
        dtype = np.uint8
    )

    # Give the channels different pixel patterns.
    pixels[:, :, 0] = [
        [10, 11, 12],
        [10, 11, 12],
        [10, 11, 12]
    ]

    pixels[:, :, 1] = [
        [20, 20, 20],
        [20, 20, 20],
        [20, 20, 20]
    ]

    pixels[:, :, 2] = [
        [30, 31, 32],
        [31, 32, 33],
        [32, 33, 34]
    ]

    image_path = tmp_path / "test_rgb.png"

    image = Image.fromarray(pixels)
    image.save(image_path)

    result = analyze_difference_histogram(
        image_path
    )

    assert result["mode"] == "RGB"

    # RGB should produce exactly three channel results.
    assert len(result["channels"]) == 3

    channel_names = [
        channel["channel"]
        for channel in result["channels"]
    ]

    assert channel_names == [
        "R",
        "G",
        "B"
    ]

    # Verify image-level DH roughness is the average
    # of R, G, and B roughness.
    expected_average = np.mean([
        channel["roughness"]
        for channel in result["channels"]
    ])

    assert result["raw_dh_roughness"] == pytest.approx(
        expected_average
    )


def test_missing_image_raises_error(tmp_path):
    missing_path = tmp_path / "missing.png"

    with pytest.raises(FileNotFoundError):
        analyze_difference_histogram(
            missing_path
        )


def test_unsupported_image_mode(tmp_path):
    pixels = np.zeros(
        (3, 3, 4),
        dtype = np.uint8
    )

    image_path = tmp_path / "test_rgba.png"

    image = Image.fromarray(pixels)
    image.save(image_path)

    with pytest.raises(ValueError):
        analyze_difference_histogram(
            image_path
        )


# ---------------------------------------------------------
# Tests for DifferenceHistogramDetector
# ---------------------------------------------------------

def test_detector_returns_score_and_diagnostics():
    image = np.array([
        [10, 11, 12],
        [10, 11, 12],
        [10, 11, 12]
    ], dtype = np.uint8)

    detector = DifferenceHistogramDetector()

    result = detector.analyze(image)

    assert "score" in result
    assert "diagnostics" in result

    assert "raw_roughness" in result["diagnostics"]
    assert "channels" in result["diagnostics"]


def test_detector_score_is_between_zero_and_one():
    image = np.array([
        [10, 11, 12],
        [10, 11, 12],
        [10, 11, 12]
    ], dtype = np.uint8)

    detector = DifferenceHistogramDetector()

    result = detector.analyze(image)

    assert 0.0 <= result["score"] <= 1.0


def test_detector_grayscale_diagnostics():
    image = np.array([
        [10, 11, 12],
        [10, 11, 12],
        [10, 11, 12]
    ], dtype = np.uint8)

    detector = DifferenceHistogramDetector()

    result = detector.analyze(image)

    channels = result["diagnostics"]["channels"]

    assert len(channels) == 1
    assert channels[0]["channel"] == "L"

    assert result["diagnostics"]["raw_roughness"] == pytest.approx(
        channels[0]["roughness"]
    )


def test_detector_rgb_has_three_channels():
    image = np.zeros(
        (3, 3, 3),
        dtype = np.uint8
    )

    detector = DifferenceHistogramDetector()

    result = detector.analyze(image)

    channels = result["diagnostics"]["channels"]

    assert len(channels) == 3

    channel_names = [
        channel["channel"]
        for channel in channels
    ]

    assert channel_names == [
        "R",
        "G",
        "B"
    ]


def test_detector_rejects_float_dtype():
    image = np.zeros(
        (3, 3),
        dtype = np.float32
    )

    detector = DifferenceHistogramDetector()

    with pytest.raises(ValueError):
        detector.analyze(image)


def test_detector_rejects_negative_pixel_values():
    image = np.zeros(
        (3, 3),
        dtype = np.int16
    )

    image[0, 0] = -1

    detector = DifferenceHistogramDetector()

    with pytest.raises(ValueError):
        detector.analyze(image)


def test_detector_rejects_pixel_values_above_255():
    image = np.zeros(
        (3, 3),
        dtype = np.int16
    )

    image[0, 0] = 256

    detector = DifferenceHistogramDetector()

    with pytest.raises(ValueError):
        detector.analyze(image)


@pytest.mark.parametrize(
    "shape",
    [
        (9,),
        (3, 3, 1),
        (3, 3, 4),
        (2, 3, 3, 3)
    ]
)
def test_detector_rejects_invalid_shape(shape):
    image = np.zeros(
        shape,
        dtype = np.uint8
    )

    detector = DifferenceHistogramDetector()
    
    with pytest.raises(ValueError):
        detector.analyze(image)


def test_detector_is_repeatable():
    image = np.array([
        [10, 11, 12],
        [10, 11, 12],
        [10, 11, 12]
    ], dtype = np.uint8)

    detector = DifferenceHistogramDetector()

    first = detector.analyze(image)
    second = detector.analyze(image)

    assert first == second


def test_detector_does_not_modify_input():
    image = np.array([
        [10, 11, 12],
        [10, 11, 12],
        [10, 11, 12]
    ], dtype = np.uint8)

    original = image.copy()

    detector = DifferenceHistogramDetector()

    detector.analyze(image)

    assert np.array_equal(
        image,
        original
    )


def test_detector_histogram_total_is_correct():
    image = np.array([
        [10, 11, 12],
        [10, 11, 12],
        [10, 11, 12]
    ], dtype = np.uint8)

    detector = DifferenceHistogramDetector()

    result = detector.analyze(image)

    channel = result["diagnostics"]["channels"][0]

    assert channel["histogram_total"] == 12
