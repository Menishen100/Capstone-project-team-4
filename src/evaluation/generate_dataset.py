"""Generate and validate reproducible clean/stego image pairs.

This module coordinates Arthur's clean-image validator with Exzavier's LSB
embedder. It deliberately does not implement an embedding algorithm.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable, Mapping

from src.evaluation.validate_dataset import validate_clean_dataset
from src.lsb_embedder import embed_lsb


METADATA_FIELDS = (
    "source_id", "clean_filename", "stego_filename", "payload_rate",
    "random_seed", "color_mode", "width", "height", "split", "format",
    "source_license_note", "generation_status", "payload_bytes",
    "capacity_bits", "embedded_bits", "changed_values",
)
DEFAULT_SPLIT_COUNTS = {
    "development": 60,
    "validation": 20,
    "held_out_test": 20,
}


@dataclass(frozen=True)
class PairingIssue:
    """One paired-dataset integrity issue."""

    location: str
    message: str


@dataclass
class PairingValidationReport:
    """Machine-readable result of paired-dataset validation."""

    expected_pairs: int
    pair_count: int = 0
    split_counts: dict[str, int] = field(default_factory=dict)
    issues: list[PairingIssue] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.issues and self.pair_count == self.expected_pairs

    def to_dict(self) -> dict[str, object]:
        return {
            "expected_pairs": self.expected_pairs,
            "pair_count": self.pair_count,
            "split_counts": self.split_counts,
            "is_valid": self.is_valid,
            "issues": [asdict(issue) for issue in self.issues],
        }


def expected_stego_filename(clean_filename: str) -> str:
    """Map one clean filename to its one expected stego counterpart."""
    path = Path(clean_filename)
    stem = path.stem
    stem = f"{stem[:-6]}_stego" if stem.endswith("_clean") else f"{stem}_stego"
    return f"{stem}.png"


def seed_for_source(master_seed: int, source_id: str) -> int:
    """Derive a stable per-source seed from one master seed."""
    digest = hashlib.sha256(f"{master_seed}:{source_id}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") & ((1 << 63) - 1)


def assign_splits(
    source_ids: Iterable[str],
    split_counts: Mapping[str, int] = DEFAULT_SPLIT_COUNTS,
) -> dict[str, str]:
    """Assign each source to one split in stable source-ID order."""
    ordered_ids = sorted(source_ids)
    if len(ordered_ids) != sum(split_counts.values()):
        raise ValueError("source count must equal the configured split total")
    assignments: dict[str, str] = {}
    position = 0
    for split, count in split_counts.items():
        if count < 0:
            raise ValueError("split counts must be non-negative")
        for source_id in ordered_ids[position : position + count]:
            assignments[source_id] = split
        position += count
    return assignments


def read_clean_inventory(path: Path) -> dict[str, dict[str, str]]:
    """Read the validated source/license inventory keyed by clean filename."""
    with path.open(newline="", encoding="utf-8") as handle:
        return {
            row["filename"].strip(): {
                "source_id": row["source_id"].strip(),
                "source_license_note": row["source_license_note"].strip(),
            }
            for row in csv.DictReader(handle)
        }


def write_metadata(path: Path, rows: list[dict[str, object]]) -> None:
    """Write paired metadata using the documented schema."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=METADATA_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def validate_paired_dataset(
    metadata_path: str | Path,
    clean_directory: str | Path,
    stego_directory: str | Path,
    *,
    expected_count: int = 100,
    split_counts: Mapping[str, int] = DEFAULT_SPLIT_COUNTS,
) -> PairingValidationReport:
    """Verify pair mappings, filenames, required metadata, and split counts."""
    report = PairingValidationReport(expected_pairs=expected_count)
    metadata_path = Path(metadata_path)
    clean_directory = Path(clean_directory)
    stego_directory = Path(stego_directory)

    if expected_count != sum(split_counts.values()):
        report.issues.append(PairingIssue("configuration", "expected_count must equal split total"))
        return report
    if not metadata_path.is_file():
        report.issues.append(PairingIssue(str(metadata_path), "metadata file is missing"))
        return report

    with metadata_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing_columns = set(METADATA_FIELDS) - set(reader.fieldnames or [])
        if missing_columns:
            report.issues.append(PairingIssue(
                str(metadata_path),
                "metadata is missing required columns: " + ", ".join(sorted(missing_columns)),
            ))
            return report
        rows = list(reader)

    report.pair_count = len(rows)
    source_ids: set[str] = set()
    clean_names: set[str] = set()
    stego_names: set[str] = set()
    observed_splits: Counter[str] = Counter()

    for line_number, row in enumerate(rows, start=2):
        location = f"metadata line {line_number}"
        missing_values = [
            field for field in METADATA_FIELDS if not (row.get(field) or "").strip()
        ]
        if missing_values:
            report.issues.append(PairingIssue(
                location, "missing required values: " + ", ".join(missing_values)
            ))
            continue

        source_id = row["source_id"].strip()
        clean_name = row["clean_filename"].strip()
        stego_name = row["stego_filename"].strip()
        split = row["split"].strip()
        for value, values, label in (
            (source_id, source_ids, "source_id"),
            (clean_name, clean_names, "clean filename"),
            (stego_name, stego_names, "stego filename"),
        ):
            if value in values:
                report.issues.append(PairingIssue(location, f"duplicate {label}: {value}"))
            values.add(value)

        if split not in split_counts:
            report.issues.append(PairingIssue(location, f"unsupported split: {split}"))
        else:
            observed_splits[split] += 1
        if stego_name != expected_stego_filename(clean_name):
            report.issues.append(PairingIssue(
                location, "stego filename does not match the clean source mapping"
            ))
        if not (clean_directory / clean_name).is_file():
            report.issues.append(PairingIssue(location, f"clean image is missing: {clean_name}"))
        if not (stego_directory / stego_name).is_file():
            report.issues.append(PairingIssue(location, f"stego image is missing: {stego_name}"))
        try:
            if int(row["random_seed"]) < 0:
                raise ValueError
            float(row["payload_rate"])
            int(row["width"])
            int(row["height"])
        except ValueError:
            report.issues.append(PairingIssue(
                location, "payload rate, seed, width, and height must be numeric"
            ))

    report.split_counts = dict(observed_splits)
    if len(rows) != expected_count:
        report.issues.append(PairingIssue(
            str(metadata_path), f"expected {expected_count} pairs, found {len(rows)}"
        ))
    for split, expected in split_counts.items():
        if observed_splits[split] != expected:
            report.issues.append(PairingIssue(
                split, f"expected {expected} pairs, found {observed_splits[split]}"
            ))

    disk_clean_names = {
        path.name for path in clean_directory.iterdir() if path.is_file()
    } if clean_directory.is_dir() else set()
    if disk_clean_names != clean_names:
        report.issues.append(PairingIssue(
            str(clean_directory), "clean directory filenames do not match metadata pairs"
        ))
    return report


def generate_paired_dataset(
    clean_directory: str | Path,
    clean_inventory_path: str | Path,
    stego_directory: str | Path,
    metadata_path: str | Path,
    *,
    payload_rate: float,
    master_seed: int,
    expected_count: int = 100,
    split_counts: Mapping[str, int] = DEFAULT_SPLIT_COUNTS,
    overwrite: bool = False,
) -> list[dict[str, object]]:
    """Generate one deterministic stego image per validated clean source."""
    if not isinstance(master_seed, int) or isinstance(master_seed, bool) or master_seed < 0:
        raise ValueError("master_seed must be a non-negative integer")
    if expected_count != sum(split_counts.values()):
        raise ValueError("expected_count must equal the configured split total")

    clean_directory = Path(clean_directory)
    clean_inventory_path = Path(clean_inventory_path)
    stego_directory = Path(stego_directory)
    metadata_path = Path(metadata_path)
    clean_report = validate_clean_dataset(
        clean_directory, clean_inventory_path, expected_count=expected_count
    )
    if not clean_report.is_valid:
        details = "; ".join(
            f"{issue.filename}: {issue.message}" for issue in clean_report.issues[:5]
        )
        raise ValueError(f"clean dataset validation failed: {details}")

    inventory = read_clean_inventory(clean_inventory_path)
    assignments = assign_splits(
        (record.source_id for record in clean_report.records), split_counts
    )
    stego_directory.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []

    for record in sorted(clean_report.records, key=lambda item: item.source_id):
        clean_path = clean_directory / record.filename
        stego_name = expected_stego_filename(record.filename)
        stego_path = stego_directory / stego_name
        if stego_path.exists() and not overwrite:
            raise FileExistsError(
                f"refusing to overwrite existing stego output: {stego_path}"
            )

        random_seed = seed_for_source(master_seed, record.source_id)
        embedding = embed_lsb(
            clean_path, payload_rate=payload_rate, random_seed=random_seed,
            stego_dir=stego_directory,
        )
        rows.append({
            "source_id": record.source_id,
            "clean_filename": record.filename,
            "stego_filename": stego_name,
            "payload_rate": embedding["Payload_rate"],
            "random_seed": random_seed,
            "color_mode": record.color_mode,
            "width": record.width,
            "height": record.height,
            "split": assignments[record.source_id],
            "format": record.format,
            "source_license_note": inventory[record.filename]["source_license_note"],
            "generation_status": "generated",
            "payload_bytes": embedding["Payload_bytes"],
            "capacity_bits": embedding["Capacity_bits"],
            "embedded_bits": embedding["Embedded_bits"],
            "changed_values": embedding["Changed_values"],
        })

    write_metadata(metadata_path, rows)
    report = validate_paired_dataset(
        metadata_path, clean_directory, stego_directory,
        expected_count=expected_count, split_counts=split_counts,
    )
    if not report.is_valid:
        raise RuntimeError("generated dataset failed validation: " + "; ".join(
            issue.message for issue in report.issues
        ))
    return rows


def main(arguments: Iterable[str] | None = None) -> int:
    """Run paired-dataset generation from the command line."""
    parser = argparse.ArgumentParser(
        description="Generate validated clean/stego pairs and reproducible metadata."
    )
    parser.add_argument("clean_directory", type=Path)
    parser.add_argument("clean_inventory", type=Path)
    parser.add_argument("stego_directory", type=Path)
    parser.add_argument("metadata", type=Path)
    parser.add_argument("--payload-rate", type=float, default=0.25)
    parser.add_argument("--seed", type=int, default=20260920)
    parser.add_argument("--expected-count", type=int, default=100)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(arguments)

    try:
        rows = generate_paired_dataset(
            args.clean_directory, args.clean_inventory, args.stego_directory,
            args.metadata, payload_rate=args.payload_rate, master_seed=args.seed,
            expected_count=args.expected_count, overwrite=args.overwrite,
        )
    except (FileExistsError, RuntimeError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps({
        "generation_status": "generated",
        "pair_count": len(rows),
        "metadata": str(args.metadata),
        "splits": dict(Counter(row["split"] for row in rows)),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
