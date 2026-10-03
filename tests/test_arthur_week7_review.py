"""Tests for Arthur's development-only Chi-square/RS review."""

import csv

import pytest

from src.evaluation.review_arthur_detectors import review_development_scores


FIELDS = ["source_id", "label", "filename", "split", "status", "chi_square_score", "rs_score"]


def write_scores(path, rows, fields=FIELDS):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def rows():
    return [
        {"source_id": "one", "label": "clean", "filename": "one-clean.png", "split": "development", "status": "complete", "chi_square_score": "0.1", "rs_score": "0.2"},
        {"source_id": "one", "label": "stego", "filename": "one-stego.png", "split": "development", "status": "complete", "chi_square_score": "0.4", "rs_score": "0.5"},
        {"source_id": "two", "label": "clean", "filename": "two-clean.png", "split": "development", "status": "complete", "chi_square_score": "0.9", "rs_score": "0.8"},
        {"source_id": "two", "label": "stego", "filename": "two-stego.png", "split": "development", "status": "complete", "chi_square_score": "0.2", "rs_score": "0.1"},
    ]


def test_review_computes_statistics_and_candidate_files(tmp_path):
    path = tmp_path / "scores.csv"
    write_scores(path, rows())

    review = review_development_scores(path)

    chi = review["Chi-square"]
    assert chi["clean_mean"] == pytest.approx(0.5)
    assert chi["stego_median"] == pytest.approx(0.3)
    assert [row["filename"] for row in chi["candidate_fp_rows"]] == ["two-clean.png"]
    assert chi["candidate_fn_rows"] == []
    assert set(review) == {"Chi-square", "RS"}


@pytest.mark.parametrize("split", ["validation", "held_out_test"])
def test_review_rejects_reserved_splits(tmp_path, split):
    path = tmp_path / "scores.csv"
    data = rows()
    data[-1]["split"] = split
    write_scores(path, data)

    with pytest.raises(ValueError, match="only development"):
        review_development_scores(path)


def test_review_rejects_missing_detector_column(tmp_path):
    path = tmp_path / "scores.csv"
    fields = [field for field in FIELDS if field != "rs_score"]
    write_scores(path, [{field: value for field, value in row.items() if field in fields} for row in rows()], fields)

    with pytest.raises(ValueError, match="rs_score"):
        review_development_scores(path)


@pytest.mark.parametrize("bad_score", ["-0.01", "1.01", "nan", "invalid"])
def test_review_rejects_invalid_score_bounds(tmp_path, bad_score):
    path = tmp_path / "scores.csv"
    data = rows()
    data[0]["chi_square_score"] = bad_score
    write_scores(path, data)

    with pytest.raises(ValueError, match="chi_square_score"):
        review_development_scores(path)
