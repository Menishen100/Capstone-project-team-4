import csv
import json
import pytest
from src.evaluation.review_dh import (
    format_review,
    main,
    review_development_dh,
)


FIELDNAMES = [
    "source_id",
    "label",
    "filename",
    "split",
    "status",
    "dh_score",
    "dh_raw_roughness",
    "dh_diagnostics",
]


def _score(raw_roughness):
    return raw_roughness / (1.0 + raw_roughness)


def _diagnostics(
    mode,
    zero_fraction = 0.25,
    variation = 50000,
    central_total = 127000,
    histogram_total = 130560,
):
    if mode == "L":
        channel_names = ["L"]
    elif mode == "RGB":
        channel_names = ["R", "G", "B"]
    else:
        raise ValueError("mode must be L or RGB")

    channels = []

    for channel_name in channel_names:
        channels.append(
            {
                "channel": channel_name,
                "zero_difference_fraction": zero_fraction,
                "variation": variation,
                "central_total": central_total,
                "histogram_total": histogram_total,
            }
        )

    return json.dumps(
        {
            "channels": channels,
        }
    )


def _row(
    source_id,
    label,
    filename,
    mode,
    raw_roughness,
    *,
    split = "development",
    status = "complete",
    score = None,
    histogram_total = 130560
):
    if score is None:
        score = _score(raw_roughness)

    return {
        "source_id": source_id,
        "label": label,
        "filename": filename,
        "split": split,
        "status": status,
        "dh_score": str(score),
        "dh_raw_roughness": str(raw_roughness),
        "dh_diagnostics": _diagnostics(
            mode,
            histogram_total = histogram_total,
        ),
    }


def _write_scores(path, rows):
    with path.open(
        "w",
        newline = "",
        encoding = "utf-8",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames = FIELDNAMES,
        )

        writer.writeheader()
        writer.writerows(rows)


def _valid_rows():
    return [
        _row(
            "source-001",
            "clean",
            "pair_001_clean.png",
            "RGB",
            1.0,
        ),
        _row(
            "source-001",
            "stego",
            "pair_001_stego.png",
            "RGB",
            0.5,
        ),
        _row(
            "source-051",
            "clean",
            "pair_051_clean.png",
            "L",
            0.25,
        ),
        _row(
            "source-051",
            "stego",
            "pair_051_stego.png",
            "L",
            0.4,
        ),
    ]


def test_review_summarizes_development_row(tmp_path):
    score_path = tmp_path / "scores.csv"

    rows = _valid_rows()

    rows.append(
        _row(
            "source-999",
            "clean",
            "ignored.png",
            "L",
            1.0,
            split = "validation"
        )
    )

    _write_scores(
        score_path,
        rows,
    )

    review = review_development_dh(score_path)

    assert review["clean_count"] == 2
    assert review["stego_count"] == 2
    assert review["pair_count"] == 2

    assert review["stego_higher_count"] == 1
    assert review["stego_lower_count"] == 1
    assert review["equal_score_count"] == 0

    assert review["candidate_fp_count"] == 1
    assert review["candidate_fn_count"] == 0

    assert review["normalization_verified"] is True
    assert review["all_scores_in_range"] is True

    assert review["clean_rgb_count"] == 1
    assert review["clean_grayscale_count"] == 1
    assert review["stego_rgb_count"] == 1
    assert review["stego_grayscale_count"] == 1

    assert review["histogram_total_verified"] is True

    assert review["clean_score_min"] == pytest.approx(0.2)
    assert review["clean_score_max"] == pytest.approx(0.5)

    assert review["stego_score_min"] == pytest.approx(0.4 / 1.4)
    assert review["stego_score_max"] == pytest.approx(0.5 / 1.5)

    assert review["clean_rgb_mean_score"] == pytest.approx(0.5)
    assert review["clean_grayscale_mean_score"] == pytest.approx(0.2)

    assert review["stego_rgb_mean_score"] == pytest.approx(0.5 / 1.5)
    assert review["stego_grayscale_mean_score"] == pytest.approx(0.4 / 1.4)

    assert review["candidate_fp_summaries"][0]["source_id"] == "source-001"
    assert review["candidate_fp_summaries"][0]["label"] == "clean"
    assert (
        review["candidate_fp_summaries"][0]["reason"]
        == "clean score exceeded every stego score"
    )


def test_review_detects_normalization_mismatch(tmp_path):
    score_path = tmp_path / "scores.csv"

    rows = _valid_rows()

    rows[0]["dh_score"] = "0.4"

    _write_scores(
        score_path,
        rows,
    )

    review = review_development_dh(score_path)

    assert review["normalization_verified"] is False
    assert len(review["normalization_mismatches"]) == 1


def test_review_rejects_invalid_diagnostics_json(tmp_path):
    score_path = tmp_path / "scores.csv"

    rows = _valid_rows()

    rows[0]["dh_diagnostics"] = "not valid json"

    _write_scores(
        score_path,
        rows,
    )

    with pytest.raises(
        ValueError,
        match = "valid JSON",
    ):
        review_development_dh(score_path)


def test_review_rejects_mismatched_source_ids(tmp_path):
    score_path = tmp_path / "scores.csv"

    rows = _valid_rows()

    rows[3]["source_id"] = "source-999"

    _write_scores(
        score_path,
        rows,
    )

    with pytest.raises(
        ValueError,
        match = "matching source_id",
    ):
        review_development_dh(score_path)


def test_review_detects_histogram_total_mismatch(tmp_path):
    score_path = tmp_path / "scores.csv"

    rows = _valid_rows()

    rows[0]["dh_diagnostics"] = _diagnostics(
        "RGB",
        histogram_total = 100,
    )

    _write_scores(
        score_path,
        rows,
    )

    review = review_development_dh(score_path)

    assert review["histogram_total_verified"] is False
    assert len(review["histogram_total_mismatches"]) == 1


def test_review_reports_candidate_false_negative(tmp_path):
    score_path = tmp_path / "scores.csv"

    rows = _valid_rows()

    rows[3] = _row(
        "source-051",
        "stego",
        "pair_051_stego.png",
        "L",
        0.1,
    )

    _write_scores(
        score_path,
        rows,
    )

    review = review_development_dh(score_path)

    assert review["candidate_fn_count"] == 1

    candidate = review["candidate_fn_summaries"][0]

    assert candidate["source_id"] == "source-051"
    assert candidate["filename"] == "pair_051_stego.png"
    assert candidate["label"] == "stego"
    assert candidate["reason"] == (
        "stego score was below every clean score"
    )

    output = format_review(review)

    assert "Detailed Candidate Stego Case Diagnostics:" in output
    assert "pair_051_stego.png" in output


def test_format_review_and_main(tmp_path, capsys):
    score_path = tmp_path / "scores.csv"

    _write_scores(
        score_path,
        _valid_rows(),
    )

    review = review_development_dh(score_path)

    output = format_review(review)

    assert "Difference Histogram (DH)" in output
    assert "Normalization:" in output
    assert "Paired Clean/Stego Comparison" in output
    assert "Preprocessing Consistency Check:" in output
    assert "Clean Min/Max:" in output
    assert "Stego Min/Max:" in output
    assert "Image Mode Review:" in output
    assert "Clean RGB Mean Score:" in output
    assert "Clean Grayscale Mean Score:" in output
    assert "Detailed Candidate Clean Case Diagnostics:" in output

    exit_code = main(
        [
            "--scores",
            str(score_path),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Difference Histogram (DH)" in captured.out