import csv
from pathlib import Path
import numpy as np
from PIL import Image

from src.detectors.difference_histogram import(
    DifferenceHistogramDetector,
)

CLEAN_DIR = Path("dataset/clean")
STEGO_DIR = Path("dataset/stego")
METADATA_PATH = Path("data/metadata.csv")

def test_real_dataset_images_run_through_detector():
    detector = DifferenceHistogramDetector()

    clean_images = sorted(
        CLEAN_DIR.glob("*.png")
    )

    stego_images = sorted(
        STEGO_DIR.glob("*.png")
    )

    assert len(clean_images) == 100
    assert len(stego_images) == 100

    image_paths = (
        clean_images
        + stego_images
    )

    for image_path in image_paths:
        with Image.open(image_path) as image:
            pixels = np.array(image)

        result = detector.analyze(pixels)

        assert 0.0 <= result["score"] <= 1.0
        assert "diagnostics" in result
        assert "channels" in result["diagnostics"]


def test_real_clean_dataset_modes():
    """Each clean image must match its recorded metadata mode, not its number."""
    with METADATA_PATH.open(newline="", encoding="utf-8") as handle:
        metadata_rows = list(csv.DictReader(handle))

    assert len(metadata_rows) == 100
    for row in metadata_rows:
        image_path = CLEAN_DIR / row["clean_filename"]

        with Image.open(image_path) as image:
            assert image.mode == row["color_mode"]


def test_clean_and_stego_modes_match():

    for number in range(1, 101):

        clean_path = CLEAN_DIR / (
            f"pair_{number:03d}_clean.png"
        )

        stego_path = STEGO_DIR / (
            f"pair_{number:03d}_stego.png"
        )

        with Image.open(clean_path) as clean:
            with Image.open(stego_path) as stego:
                assert clean.mode == stego.mode


def test_real_dataset_histogram_totals():
    detector = DifferenceHistogramDetector()

    image_paths = (
        sorted(CLEAN_DIR.glob("*.png"))
        + sorted(STEGO_DIR.glob("*.png"))
    )
    
    for image_path in image_paths:
        with Image.open(image_path) as image:
            pixels = np.array(image)
    
        result = detector.analyze(pixels)

        channels = result["diagnostics"]["channels"]

        for channel in channels:
            assert channel["histogram_total"] == 130560
