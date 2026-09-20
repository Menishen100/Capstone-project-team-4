"""Tests for Menishen's reproducible paired-dataset workflow."""

import csv
from collections import Counter

import numpy as np
import pytest
from PIL import Image

from src.evaluation.generate_dataset import (
    DEFAULT_SPLIT_COUNTS,
    METADATA_FIELDS,
    assign_splits,
    generate_paired_dataset,
    validate_paired_dataset,
)


def write_clean_collection(root, count):
    clean = root / "clean"
    clean.mkdir()
    inventory = root / "clean_metadata.csv"
    rows = []
    for index in range(1, count + 1):
        filename = f"pair_{index:03d}_clean.png"
        pixels = np.full(
            (8, 8, 3), (index, index * 2 % 256, index * 3 % 256), dtype=np.uint8
        )
        Image.fromarray(pixels, mode="RGB").save(clean / filename, format="PNG")
        rows.append({"source_id": f"source-{index:03d}", "filename": filename,
                     "source_license_note": f"CC0 test fixture {index}"})
    with inventory.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle,
            fieldnames=["source_id", "filename", "source_license_note"])
        writer.writeheader()
        writer.writerows(rows)
    return clean, inventory


def test_generation_creates_pairs_and_complete_metadata(tmp_path):
    clean, inventory = write_clean_collection(tmp_path, 4)
    stego = tmp_path / "stego"
    metadata = tmp_path / "metadata.csv"
    splits = {"development": 2, "validation": 1, "held_out_test": 1}
    rows = generate_paired_dataset(
        clean, inventory, stego, metadata, payload_rate=0.25,
        master_seed=20260920, expected_count=4, split_counts=splits)
    assert len(rows) == 4
    assert set(rows[0]) == set(METADATA_FIELDS)
    assert all((stego / row["stego_filename"]).is_file() for row in rows)
    report = validate_paired_dataset(
        metadata, clean, stego, expected_count=4, split_counts=splits)
    assert report.is_valid
    assert report.split_counts == splits


def test_hundred_pair_target_uses_the_required_60_20_20_splits(tmp_path):
    clean, inventory = write_clean_collection(tmp_path, 100)
    stego = tmp_path / "stego"
    metadata = tmp_path / "metadata.csv"
    rows = generate_paired_dataset(
        clean, inventory, stego, metadata, payload_rate=0.25,
        master_seed=20260920)
    assert len(rows) == 100
    assert Counter(row["split"] for row in rows) == DEFAULT_SPLIT_COUNTS
    assert validate_paired_dataset(metadata, clean, stego).is_valid


def test_pairs_are_reproducible_with_the_same_seed_and_config(tmp_path):
    clean, inventory = write_clean_collection(tmp_path, 4)
    splits = {"development": 2, "validation": 1, "held_out_test": 1}
    first_rows = generate_paired_dataset(
        clean, inventory, tmp_path / "stego-one", tmp_path / "first.csv",
        payload_rate=0.25, master_seed=99, expected_count=4, split_counts=splits)
    second_rows = generate_paired_dataset(
        clean, inventory, tmp_path / "stego-two", tmp_path / "second.csv",
        payload_rate=0.25, master_seed=99, expected_count=4, split_counts=splits)
    assert first_rows == second_rows
    for row in first_rows:
        assert ((tmp_path / "stego-one" / row["stego_filename"]).read_bytes()
                == (tmp_path / "stego-two" / row["stego_filename"]).read_bytes())


def test_validator_rejects_a_pair_with_the_wrong_stego_mapping(tmp_path):
    clean, inventory = write_clean_collection(tmp_path, 4)
    stego = tmp_path / "stego"
    metadata = tmp_path / "metadata.csv"
    splits = {"development": 2, "validation": 1, "held_out_test": 1}
    generate_paired_dataset(
        clean, inventory, stego, metadata, payload_rate=0.25,
        master_seed=2, expected_count=4, split_counts=splits)
    with metadata.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    rows[0]["stego_filename"] = "different_stego.png"
    with metadata.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=METADATA_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    report = validate_paired_dataset(
        metadata, clean, stego, expected_count=4, split_counts=splits)
    assert not report.is_valid
    assert any("does not match" in issue.message for issue in report.issues)


def test_generator_refuses_unvalidated_clean_sources(tmp_path):
    clean, inventory = write_clean_collection(tmp_path, 4)
    with inventory.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle,
            fieldnames=["source_id", "filename", "source_license_note"])
        writer.writeheader()
    with pytest.raises(ValueError, match="clean dataset validation failed"):
        generate_paired_dataset(
            clean, inventory, tmp_path / "stego", tmp_path / "metadata.csv",
            payload_rate=0.25, master_seed=2, expected_count=4,
            split_counts={"development": 2, "validation": 1, "held_out_test": 1})


def test_split_assignment_requires_exact_target_count():
    source_ids = [f"source-{index:03d}" for index in range(100)]
    assignments = assign_splits(source_ids)
    assert Counter(assignments.values()) == DEFAULT_SPLIT_COUNTS
    with pytest.raises(ValueError, match="source count"):
        assign_splits(source_ids[:-1])
