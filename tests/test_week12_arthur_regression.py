"""Freeze diagnostic score behavior on representative official Week 11 rows."""

import pytest

from src.ensemble.normalization import normalize_chi_square, normalize_rs
from src.evaluation.analyze_arthur_week12 import detector_summary
from src.evaluation.analyze_week12_errors import classify_cases, load_official_predictions


def test_official_false_negative_and_false_positive_source_ids_remain_stable():
    groups = classify_cases(load_official_predictions("data/week11_heldout_predictions.csv"))
    assert [row["source_id"] for row in groups["false_negative"]] == [
        "source-081", "source-082", "source-085", "source-090", "source-091",
        "source-092", "source-094", "source-097", "source-098", "source-099", "source-100",
    ]
    assert [row["source_id"] for row in groups["false_positive"]] == [
        "source-083", "source-084", "source-088", "source-096",
    ]


def test_official_known_false_negative_score_is_reproducibly_read():
    rows = load_official_predictions("data/week11_heldout_predictions.csv")
    known = next(row for row in rows if row["source_id"] == "source-081" and row["label"] == "stego")
    assert float(known["ensemble_score"]) == pytest.approx(0.478368044288772)
    assert float(known["rs_score"]) == pytest.approx(0.5152473038304203)


def test_official_rs_inversion_and_chi_normalization_are_frozen():
    assert normalize_rs(0.25) == pytest.approx(0.75)
    assert normalize_chi_square(0.25) == pytest.approx(0.25)


def test_detector_group_means_are_computed_for_all_four_cells():
    summary = detector_summary(load_official_predictions("data/week11_heldout_predictions.csv"))
    assert [summary[cell]["count"] for cell in ("true_positive", "true_negative", "false_positive", "false_negative")] == [9, 16, 4, 11]
    assert summary["false_negative"]["mean_normalized_rs"] >= 0.0
