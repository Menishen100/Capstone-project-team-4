from pathlib import Path
from PIL import Image
import numpy as np

def difference_histogram(channel):
    """
    Build a 511-bin Difference Histogram for one 2-D image channel.

    The histogram represents adjacent-pixel differences from
    -255 through +255

    Parameters:
        channel: 2-D numpy array representing one image channel

    Returns:
        hist: 511-bin numpy array containing difference counts.
    """

    # Make sure the input is a 2-D channel
    channel = np.asarray(channel)

    if channel.ndim != 2:
        raise ValueError(
            "difference_histogram() requires a 2-D image channel."
        )

    # Convert channel to int16 so negative differences are preserved
    channel = np.asarray(channel, dtype=np.int16)

    # Calculate horizontal and vertical adjacent-pixel differences
    horizontal_diff = np.diff(channel, axis=1)
    vertical_diff = np.diff(channel, axis=0)

    # Flatten the difference arrays
    horizontal_flat = horizontal_diff.flatten()
    vertical_flat = vertical_diff.flatten()

    # Combine horizontal and vertical differences
    differences = np.concatenate(
        (horizontal_flat, vertical_flat)
    )

    # Shift differences values from -255 to 255 range to 0 to 510 range
    shifted_differences = differences + 255

    # Build 511-bin DH to capture all possible pixel differences
    hist = np.bincount(
        shifted_differences,
        minlength = 511
    )

    return hist

def histogram_roughness(hist, central_radius = 32):
    """
    Calculate central Difference Histogram roughness and diagnostics.

    The default central region is -32 through +32

    Parameters:
        hist: 511-bin Difference Histogram.
        central_radius: Distance from 0 to include in the central region.

    Returns:
        Dictionary containing roughness and diagnostic metrics.
    """

    hist = np.asarray(hist)

    # Make sure histogram contains all 511 possible pixel differences
    if len(hist) != 511:
        raise ValueError(
            "Difference Histogram must contain 511 bins."
        )

    # Make sure the radius is within the valid DH range
    if central_radius < 0 or central_radius > 255:
        raise ValueError(
            "Central radius must be between 0 and 255."
        )

    histogram_total = hist.sum()

    # Zero difference count is located at index 255
    zero_difference_count = hist[255]

    # Select central region where central_raius = 32
    start = 255 - central_radius
    end = 255 + central_radius + 1

    central_hist = hist[start:end]
    central_total = central_hist.sum()

    # Measure the changes between neighboring histogram bins
    hist_changes = np.diff(central_hist)

    # Only the size of each change matters
    absolute_changes = np.abs(hist_changes)

    # Total bin-to-bin variation
    variation = absolute_changes.sum()

    # Normalize variation by the amount of data in the central region
    roughness = (
        variation / central_total
        if central_total > 0
        else 0.0
    )

    # Proportion of all adjacent pixel differences that equal 0
    zero_difference_fraction = (
        zero_difference_count / histogram_total
        if histogram_total > 0
        else 0.0
    )

    return {
        "roughness": float(roughness),
        "variation": int(variation),
        "central_total": int(central_total),
        "central_radius": central_radius,
        "zero_difference_count": int(zero_difference_count),
        "zero_difference_fraction": float(zero_difference_fraction),
        "histogram_total": int(histogram_total)
    }

def analyze_difference_histogram(image_path):
    """
    Analyze one grayscale or RGB image using Difference Histogram analysis.

    Grayscale:
        - One channel (L) is analyzed.

    RGB:
        - Three channels (R, G, B) are analyzed individually
          and average their roughness values.

    Parameters:
        image_path: Path to the image file to be analyzed.

    Returns:
        Dictionary containing the image-level raw DH roughness
        and per-channel diagnostic.
    """

    image_path = Path(image_path)

    # Make sure the requested image exists
    if not image_path.exists():
        raise FileNotFoundError(
            f"Image file not exist: {image_path}"
        )

    with Image.open(image_path) as img:
        pixels = np.array(img)

        # Grayscale image: Analyzes single L channel
        if img.mode == "L":
            channels = [
            ("L", pixels)
        ]
        
        # RGB image: Analyzes all three channels (R, G, B) individually
        elif img.mode == "RGB":
            channels = [
            ("R", pixels[:, :, 0]),
            ("G", pixels[:, :, 1]),
            ("B", pixels[:, :, 2])
        ]

        # Rejects unsupported image modes (e.g., CMYK, RGBA, etc.)
        else:
            raise ValueError(
                f"Unsupported image mode: {img.mode}"
            )

        # Store diagnostic results for each channel
        channel_results = []

        for channel_name, channel in channels:

            hist = difference_histogram(channel)
            diagnostic = histogram_roughness(hist)

            # Add the channel name to the diagnostic results
            channel_result = {
                "channel": channel_name,
                **diagnostic
            }

            channel_results.append(channel_result)

        # Collects roughness value from each channel
        roughness_values = [
            result["roughness"]
            for result in channel_results
        ]

        # L image: Mean of L channel (one channel)
        # RGB image: Mean of R, G, B channels (three channels)
        raw_dh_roughness = float(
            np.mean(roughness_values)
        )

        return {
            "image": image_path.name,
            "mode": img.mode,
            "raw_dh_roughness": raw_dh_roughness,
            "channels": channel_results
        }

if __name__ == "__main__":

    # Example usage
    image_path = Path(
        "dataset/clean/pair_001_clean.png"

    )

    print(f"Image exists: {image_path.exists()}")

    # Analyze the selected image
    results = analyze_difference_histogram(image_path)

    print(f"\nImage: {results['image']}")
    print(f"Mode: {results['mode']}")

    print("\nChannel Diagnostics:")

    for channel in results["channels"]:
        print(
            f"\n{channel['channel']} Channel"
            f"\nRoughness: "
            f"{channel['roughness']:.4f}"
            f"\nVariation: "
            f"{channel['variation']}"
            f"\nCentral Total: "
            f"{channel['central_total']}"
            f"\nZero Difference Count: "
            f"{channel['zero_difference_count']}"
            f"\nZero Difference Fraction: "
            f"{channel['zero_difference_fraction']:.4f}"
            f"\nHistogram Total: "
            f"{channel['histogram_total']}"
        )

    print(
        f"\nRaw DH Roughness: "
        f"{results['raw_dh_roughness']:.4f}"
    )
    