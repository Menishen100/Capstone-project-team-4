"""Tests for ensemble detector-score input validation"""

import csv
import pytest
from src.ensemble.check_ensemble_inputs import validate_ensemble_inputs


FIELDNAMES = [
    "source_id",
    "label",
    "split",
    "chi_square_score",
    "rs_score",
    "dh_score",
    "status",
]


def _write_score_csv(tmp_path, rows, fieldnames = FIELDNAMES):
    """Write a temporary detector-score CSV for one test."""

    score_path = tmp_path / "detector_scores.csv"

    with score_path.open(
        "w",
        newline = "",
        encoding = "utf-8",
    ) as handle:

        writer = csv.DictWriter(
            handle,
            fieldnames = fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)

    return score_path


def _valid_development_rows():
    """Return one valid clean/stego development pair."""

    return [
        {
            "source_id": "source-001",
            "label": "clean",
            "split": "development",
            "chi_square_score": "0.20",
            "rs_score": "0.30",
            "dh_score": "0.40",
            "status": "complete",
        },
        {
            "source_id": "source-001",
            "label": "stego",
            "split": "development",
            "chi_square_score": "0.60",
            "rs_score": "0.70",
            "dh_score": "0.80",
            "status": "complete",
        },
    ]


def test_valid_development_rows_are_accepted(tmp_path):
    rows = _valid_development_rows()

    score_path = _write_score_csv(
        tmp_path,
        rows,
    )

    summary = validate_ensemble_inputs(
        score_path
    )

    assert summary["rows_checked"] == 2
    assert summary["clean_count"] == 1
    assert summary["stego_count"] == 1
    assert summary["invalid_row_count"] == 0
    assert summary["required_columns_present"] is True


def test_missing_detector_column_is_rejected(tmp_path):
    rows = _valid_development_rows()

    fieldnames = [
        "source_id",
        "label",
        "split",
        "chi_square_score",
        "rs_score",
        "status",
    ]

    rows_without_dh = []

    for row in rows:
        new_row = row.copy()
        new_row.pop("dh_score")
        rows_without_dh.append(new_row)

    score_path = _write_score_csv(
        tmp_path,
        rows_without_dh,
        fieldnames = fieldnames,
    )

    with pytest.raises(
        ValueError,
        match = "Missing required columns",
    ):
        validate_ensemble_inputs(score_path)


def test_missing_detector_score_is_rejected(tmp_path):
    rows = _valid_development_rows()

    rows[0]["dh_score"] = ""

    score_path = _write_score_csv(
        tmp_path,
        rows,
    )

    with pytest.raises(
        ValueError,
        match = "dh_score is missing",
    ):
        validate_ensemble_inputs(score_path)


def test_out_of_range_score_is_rejected(tmp_path):
    rows = _valid_development_rows()

    rows[0]["dh_score"] = "1.25"

    score_path = _write_score_csv(
        tmp_path,
        rows,
    )

    with pytest.raises(
        ValueError,
        match = "dh_score must be between 0.0 and 1.0",
    ):
        validate_ensemble_inputs(score_path)


def test_nonnumeric_score_is_rejected(tmp_path):
    rows = _valid_development_rows()

    rows[0]["rs_score"] = "hello"
    
    score_path = _write_score_csv(
        tmp_path,
        rows,
    )
    
    with pytest.raises(
        ValueError,
        match = "rs_score must be numeric",
    ):
        validate_ensemble_inputs(score_path)


@pytest.mark.parametrize(
    "invalid_score",
    [
        "nan",
        "inf",
        "-inf",
    ],
)
def test_nonfinite_scores_are_rejected(
    tmp_path,
    invalid_score,
):
    rows = _valid_development_rows()

    rows[0]["chi_square_score"] = invalid_score

    score_path = _write_score_csv(
        tmp_path,
        rows,
    )

    with pytest.raises(
        ValueError,
        match = "chi_square_score must be finite",
    ):
        validate_ensemble_inputs(score_path)


def test_incomplete_status_is_rejected(tmp_path):
    rows = _valid_development_rows()

    rows[0]["status"] = "incomplete"
    
    score_path = _write_score_csv(
        tmp_path,
        rows,
    )
    
    with pytest.raises(
        ValueError,
        match = "Does not have complete status",
    ):
        validate_ensemble_inputs(score_path)


def test_invalid_label_is_rejected(tmp_path):
    rows = _valid_development_rows()

    rows[0]["label"] = "unknown"
    
    score_path = _write_score_csv(
        tmp_path,
        rows,
    )
    
    with pytest.raises(
        ValueError,
        match = "Has invalid label",
    ):
        validate_ensemble_inputs(score_path)


def test_development_data_requires_clean_rows(tmp_path):
    rows = _valid_development_rows()

    rows = [
        row
        for row in rows
        if row["label"] == "stego"
    ]
    
    score_path = _write_score_csv(
        tmp_path,
        rows,
    )
    
    with pytest.raises(
        ValueError,
        match = "Development data contains no clean rows",
    ):
        validate_ensemble_inputs(score_path)


def test_development_data_requires_stego_rows(tmp_path):
    rows = _valid_development_rows()

    rows = [
        row
        for row in rows
        if row["label"] == "clean"
    ]
    
    score_path = _write_score_csv(
        tmp_path,
        rows,
    )
    
    with pytest.raises(
        ValueError,
        match = "Development data contains no stego rows",
    ):
        validate_ensemble_inputs(score_path)


def test_no_development_rows_are_rejected(tmp_path):
    rows = _valid_development_rows()

    for row in rows:
        row["split"] = "validation"
    
    score_path = _write_score_csv(
        tmp_path,
        rows,
    )
    
    with pytest.raises(
        ValueError,
        match = "No development rows found",
    ):
        validate_ensemble_inputs(score_path)


def test_validation_and_held_out_rows_are_excluded(tmp_path):
    rows = _valid_development_rows()

    rows.extend(
        [
            {
              "source_id": "source-002",
              "label": "clean",
              "split": "validation",
              "chi_square_score": "",
              "rs_score": "",
              "dh_score": "",
              "status": "incomplete",  
            },
            {
                "source_id": "source-003",
                "label": "stego",
                "split": "held_out_test",
                "chi_square_score": "",
                "rs_score": "",
                "dh_score": "",
                "status": "incomplete",
            }
        ]
    )

    score_path = _write_score_csv(
        tmp_path,
        rows,
    )

    summary = validate_ensemble_inputs(
        score_path
    )

    assert summary["rows_checked"] == 2
    assert summary["clean_count"] == 1
    assert summary["stego_count"] == 1
