"""Validate clean source images before stego-pair generation.

The validator intentionally checks the clean collection only.  It does not
embed a payload or generate a stego dataset; those are separate responsibilities.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable

from PIL import Image, UnidentifiedImageError


SUPPORTED_FORMATS = {".png": "PNG", ".bmp": "BMP"}
SUPPORTED_MODES = {"L", "RGB"}
STEGO_NAME_MARKERS = ("stego", "embedded", "payload")
REQUIRED_METADATA_FIELDS = {"source_id", "filename", "source_license_note"}
PLACEHOLDER_LICENSE_NOTES = {"tbd", "pending", "unknown", "n/a", "na", "not available"}


@dataclass(frozen=True)
class ValidationIssue:
    """One problem found while validating the collection."""

    filename: str
    message: str


@dataclass(frozen=True)
class ImageRecord:
    """Validated technical facts for a clean source image."""

    filename: str
    source_id: str
    format: str
    color_mode: str
    width: int
    height: int
    content_hash: str


@dataclass
class DatasetValidationReport:
    """Machine-readable summary of a clean-image validation run."""

    expected_count: int
    discovered_count: int = 0
    valid_count: int = 0
    records: list[ImageRecord] = field(default_factory=list)
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.issues and self.valid_count == self.expected_count

    def to_dict(self) -> dict[str, object]:
        return {
            "expected_count": self.expected_count,
            "discovered_count": self.discovered_count,
            "valid_count": self.valid_count,
            "is_valid": self.is_valid,
            "records": [asdict(record) for record in self.records],
            "issues": [asdict(issue) for issue in self.issues],
        }


def _read_metadata(metadata_path: Path) -> tuple[dict[str, dict[str, str]], list[ValidationIssue]]:
    """Read metadata keyed by filename and detect malformed inventory rows."""
    issues: list[ValidationIssue] = []
    if not metadata_path.is_file():
        return {}, [ValidationIssue(str(metadata_path), "metadata file is missing")]

    with metadata_path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        fields = set(reader.fieldnames or [])
        missing_fields = REQUIRED_METADATA_FIELDS - fields
        if missing_fields:
            missing = ", ".join(sorted(missing_fields))
            return {}, [ValidationIssue(str(metadata_path), f"metadata is missing required columns: {missing}")]

        rows: dict[str, dict[str, str]] = {}
        source_ids: set[str] = set()
        for line_number, row in enumerate(reader, start=2):
            filename = (row.get("filename") or "").strip()
            source_id = (row.get("source_id") or "").strip()
            license_note = (row.get("source_license_note") or "").strip()
            location = filename or f"metadata line {line_number}"
            if not filename or not source_id or not license_note:
                issues.append(ValidationIssue(location, "source_id, filename, and source_license_note are required"))
                continue
            if license_note.casefold() in PLACEHOLDER_LICENSE_NOTES:
                issues.append(ValidationIssue(location, "source_license_note must contain the actual source and license, not a placeholder"))
                continue
            if filename in rows:
                issues.append(ValidationIssue(filename, "duplicate filename in metadata"))
                continue
            if source_id in source_ids:
                issues.append(ValidationIssue(filename, f"duplicate source_id: {source_id}"))
                continue
            rows[filename] = row
            source_ids.add(source_id)
    return rows, issues


def _pixel_hash(image: Image.Image) -> str:
    """Hash decoded pixels, identifying visually identical supported images."""
    canonical = image.copy()
    digest = hashlib.sha256()
    digest.update(canonical.mode.encode("ascii"))
    digest.update(str(canonical.size).encode("ascii"))
    digest.update(canonical.tobytes())
    return digest.hexdigest()


def validate_clean_dataset(
    image_directory: str | Path,
    metadata_path: str | Path,
    *,
    expected_count: int = 100,
    minimum_dimension: int = 1,
) -> DatasetValidationReport:
    """Check a clean-image directory and its source/license inventory.

    Accepted sources are lossless PNG or BMP images in grayscale (``L``) or
    RGB mode.  Every source file must have exactly one metadata row.
    """
    report = DatasetValidationReport(expected_count=expected_count)
    directory = Path(image_directory)
    metadata, metadata_issues = _read_metadata(Path(metadata_path))
    report.issues.extend(metadata_issues)
    if not directory.is_dir():
        report.issues.append(ValidationIssue(str(directory), "clean-image directory is missing"))
        return report

    files = sorted(path for path in directory.iterdir() if path.is_file())
    report.discovered_count = len(files)
    if len(files) != expected_count:
        report.issues.append(ValidationIssue(str(directory), f"expected {expected_count} files, found {len(files)}"))

    hashes: dict[str, str] = {}
    for path in files:
        name_lower = path.name.lower()
        if any(marker in name_lower for marker in STEGO_NAME_MARKERS):
            report.issues.append(ValidationIssue(path.name, "possible stego output found in clean directory"))
        expected_format = SUPPORTED_FORMATS.get(path.suffix.lower())
        if expected_format is None:
            report.issues.append(ValidationIssue(path.name, "unsupported format; only PNG and BMP are allowed"))
            continue
        try:
            with Image.open(path) as opened:
                opened.load()
                detected_format = opened.format
                image = opened.copy()
        except (UnidentifiedImageError, OSError, ValueError) as error:
            report.issues.append(ValidationIssue(path.name, f"unreadable or corrupt image: {error}"))
            continue

        if detected_format != expected_format:
            report.issues.append(ValidationIssue(path.name, f"extension expects {expected_format}, file contains {detected_format}"))
        if image.mode not in SUPPORTED_MODES:
            report.issues.append(ValidationIssue(path.name, f"unsupported color mode: {image.mode}"))
        if image.width < minimum_dimension or image.height < minimum_dimension:
            report.issues.append(ValidationIssue(path.name, f"dimensions must be at least {minimum_dimension} x {minimum_dimension}"))

        row = metadata.get(path.name)
        if row is None:
            report.issues.append(ValidationIssue(path.name, "missing metadata row"))
            continue
        content_hash = _pixel_hash(image)
        if content_hash in hashes:
            report.issues.append(ValidationIssue(path.name, f"duplicate image content; matches {hashes[content_hash]}"))
            continue
        hashes[content_hash] = path.name
        if image.mode in SUPPORTED_MODES and image.width >= minimum_dimension and image.height >= minimum_dimension:
            report.records.append(
                ImageRecord(path.name, row["source_id"].strip(), detected_format, image.mode, image.width, image.height, content_hash)
            )

    for filename in metadata:
        if not (directory / filename).is_file():
            report.issues.append(ValidationIssue(filename, "metadata refers to a missing image file"))
    report.valid_count = len(report.records)
    return report


def main(arguments: Iterable[str] | None = None) -> int:
    """Run validation from the command line and optionally save a JSON report."""
    parser = argparse.ArgumentParser(description="Validate clean images and their source inventory.")
    parser.add_argument("image_directory", type=Path)
    parser.add_argument("metadata", type=Path)
    parser.add_argument("--expected-count", type=int, default=100)
    parser.add_argument("--minimum-dimension", type=int, default=1)
    parser.add_argument("--report", type=Path, help="Write the complete JSON report to this file.")
    args = parser.parse_args(arguments)
    report = validate_clean_dataset(args.image_directory, args.metadata, expected_count=args.expected_count, minimum_dimension=args.minimum_dimension)
    rendered = json.dumps(report.to_dict(), indent=2)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if report.is_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
