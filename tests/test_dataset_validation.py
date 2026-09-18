import csv

import pytest
from PIL import Image

from src.evaluation.validate_dataset import validate_clean_dataset


def _write_image(path, mode="RGB", pixels=None):
    if pixels is None:
        pixels = 0 if mode == "L" else (10, 20, 30, 255) if mode == "RGBA" else (10, 20, 30)
    Image.new(mode, (4, 3), pixels).save(path)


def _write_metadata(path, rows):
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["source_id", "filename", "source_license_note"])
        writer.writeheader()
        writer.writerows(rows)


def _row(filename, source_id="source-1"):
    return {"source_id": source_id, "filename": filename, "source_license_note": "CC0 test fixture"}


def test_valid_png_passes_and_reports_technical_facts(tmp_path):
    images = tmp_path / "clean"
    images.mkdir()
    _write_image(images / "clean.png")
    metadata = tmp_path / "metadata.csv"
    _write_metadata(metadata, [_row("clean.png")])

    report = validate_clean_dataset(images, metadata, expected_count=1)

    assert report.is_valid
    assert report.records[0].color_mode == "RGB"
    assert (report.records[0].width, report.records[0].height) == (4, 3)


def test_valid_bmp_passes(tmp_path):
    images = tmp_path / "clean"
    images.mkdir()
    _write_image(images / "clean.bmp", mode="L")
    metadata = tmp_path / "metadata.csv"
    _write_metadata(metadata, [_row("clean.bmp")])

    assert validate_clean_dataset(images, metadata, expected_count=1).is_valid


def test_corrupt_image_fails_without_stopping_validation(tmp_path):
    images = tmp_path / "clean"
    images.mkdir()
    (images / "broken.png").write_bytes(b"not an image")
    metadata = tmp_path / "metadata.csv"
    _write_metadata(metadata, [_row("broken.png")])

    report = validate_clean_dataset(images, metadata, expected_count=1)

    assert not report.is_valid
    assert any("unreadable or corrupt" in issue.message for issue in report.issues)


def test_unsupported_format_and_stego_name_are_rejected(tmp_path):
    images = tmp_path / "clean"
    images.mkdir()
    (images / "stego.jpg").write_bytes(b"not an image")
    metadata = tmp_path / "metadata.csv"
    _write_metadata(metadata, [_row("stego.jpg")])

    messages = [issue.message for issue in validate_clean_dataset(images, metadata, expected_count=1).issues]

    assert any("possible stego" in message for message in messages)
    assert any("unsupported format" in message for message in messages)


def test_duplicate_source_id_is_rejected(tmp_path):
    images = tmp_path / "clean"
    images.mkdir()
    _write_image(images / "one.png")
    _write_image(images / "two.png", pixels=(20, 30, 40))
    metadata = tmp_path / "metadata.csv"
    _write_metadata(metadata, [_row("one.png", "same"), _row("two.png", "same")])

    report = validate_clean_dataset(images, metadata, expected_count=2)

    assert any("duplicate source_id" in issue.message for issue in report.issues)


def test_placeholder_license_note_is_rejected(tmp_path):
    images = tmp_path / "clean"
    images.mkdir()
    _write_image(images / "clean.png")
    metadata = tmp_path / "metadata.csv"
    _write_metadata(metadata, [{"source_id": "source-1", "filename": "clean.png", "source_license_note": "TBD"}])

    report = validate_clean_dataset(images, metadata, expected_count=1)

    assert any("not a placeholder" in issue.message for issue in report.issues)


def test_invalid_color_mode_is_rejected(tmp_path):
    images = tmp_path / "clean"
    images.mkdir()
    _write_image(images / "rgba.png", mode="RGBA")
    metadata = tmp_path / "metadata.csv"
    _write_metadata(metadata, [_row("rgba.png")])

    report = validate_clean_dataset(images, metadata, expected_count=1)

    assert any("unsupported color mode" in issue.message for issue in report.issues)


def test_count_and_duplicate_pixels_are_reported(tmp_path):
    images = tmp_path / "clean"
    images.mkdir()
    _write_image(images / "one.png")
    _write_image(images / "two.png")
    metadata = tmp_path / "metadata.csv"
    _write_metadata(metadata, [_row("one.png", "one"), _row("two.png", "two")])

    report = validate_clean_dataset(images, metadata, expected_count=3)

    assert any("expected 3 files, found 2" in issue.message for issue in report.issues)
    assert any("duplicate image content" in issue.message for issue in report.issues)
