"""Tests for Menishen's Week 7 preliminary validation summary."""

import csv

import pytest

from src.evaluation.summarize_validation import summarize_development_scores, write_summary


FIELDS = [
    "source_id", "label", "filename", "split", "status",
    "chi_square_score", "rs_score", "dh_score",
]


def _row(source_id, label, split, chi, rs, dh):
    return {
        "source_id": source_id,
        "label": label,
        "filename": f"{source_id}_{label}.png",
        "split": split,
        "status": "complete",
        "chi_square_score": str(chi),
        "rs_score": str(rs),
        "dh_score": str(dh),
    }


def _write(path, rows, fields=FIELDS):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def test_summary_excludes_reserved_rows_and_records_candidates(tmp_path):
    source = tmp_path / "scores.csv"
    _write(source, [
        _row("one", "clean", "development", 0.1, 0.8, 0.7),
        _row("one", "stego", "development", 0.4, 0.1, 0.2),
        _row("two", "clean", "development", 0.9, 0.3, 0.3),
        _row("two", "stego", "development", 0.2, 0.2, 0.1),
        _row("reserved", "clean", "validation", 1.0, 1.0, 1.0),
    ])

    summary = summarize_development_scores(source)

    assert summary["row_count"] == 4
    assert summary["detectors"]["Chi-square"]["clean_mean"] == pytest.approx(0.5)
    assert summary["detectors"]["Chi-square"]["direction_observation"] == "lower-stego-on-average"
    assert [row["filename"] for row in summary["detectors"]["Chi-square"]["candidate_fp_rows"]] == ["two_clean.png"]
    assert [row["filename"] for row in summary["detectors"]["RS"]["candidate_fn_rows"]] == ["one_stego.png", "two_stego.png"]


def test_summary_rejects_invalid_scores_and_incomplete_rows(tmp_path):
    source = tmp_path / "scores.csv"
    rows = [_row("one", "clean", "development", 0.1, 0.2, 0.3), _row("one", "stego", "development", 0.4, 0.5, 1.1)]
    _write(source, rows)

    with pytest.raises(ValueError, match="dh_score"):
        summarize_development_scores(source)

    rows[1]["dh_score"] = "0.5"
    rows[1]["status"] = "partial_error"
    _write(source, rows)
    with pytest.raises(ValueError, match="status=complete"):
        summarize_development_scores(source)


def test_summary_writes_required_decision_sections(tmp_path):
    source = tmp_path / "scores.csv"
    output = tmp_path / "summary.md"
    _write(source, [
        _row("one", "clean", "development", 0.1, 0.2, 0.3),
        _row("one", "stego", "development", 0.4, 0.1, 0.2),
    ])

    write_summary(source, output)
    rendered = output.read_text(encoding="utf-8")

    assert "## 1. Development set used" in rendered
    assert "## 2. Score normalization approach" in rendered
    assert "## 4. False-positive and false-negative candidates" in rendered
    assert "## 5. Preprocessing review and decision" in rendered
    assert "Validation and held-out-test rows were excluded" in rendered
