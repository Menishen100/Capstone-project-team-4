import pytest

from src.evaluation.analyze_week12_dh_errors import (
    classify_outcome,
    count_outcomes,
    summarize_dh_by_outcome,
)


def test_classify_outcome():
    """Verify TP, TN, FP, and FN classifications."""

    assert classify_outcome(
        {
            "label": "stego",
            "prediction": "stego",
        }
    ) == "TP"

    assert classify_outcome(
        {
            "label": "clean",
            "prediction": "clean",
        }
    ) == "TN"

    assert classify_outcome(
        {
            "label": "clean",
            "prediction": "stego",
        }
    ) == "FP"

    assert classify_outcome(
        {
            "label": "stego",
            "prediction": "clean",
        }
    ) == "FN"


def test_classify_outcome_ignores_case_and_spaces():
    """Verify label formatting does not affect classification."""

    row = {
        "label": " Stego ",
        "prediction": " CLEAN ",
    }

    assert classify_outcome(row) == "FN"


def test_count_outcomes():
    """Verify TP, TN, FP, and FN counts."""

    rows = [
        {
            "label": "stego",
            "prediction": "stego",
        },
        {
            "label": "stego",
            "prediction": "stego",
        },
        {
            "label": "clean",
            "prediction": "clean",
        },
        {
            "label": "clean",
            "prediction": "stego",
        },
        {
            "label": "stego",
            "prediction": "clean",
        },
    ]

    counts = count_outcomes(rows)

    assert counts["TP"] == 2
    assert counts["TN"] == 1
    assert counts["FP"] == 1
    assert counts["FN"] == 1


def test_summarize_dh_by_outcome():
    """Verify normalized DH statistics for each outcome group."""

    rows = [
        {
            "label": "stego",
            "prediction": "stego",
            "normalized_dh": "0.80",
        },
        {
            "label": "stego",
            "prediction": "stego",
            "normalized_dh": "0.60",
        },
        {
            "label": "clean",
            "prediction": "clean",
            "normalized_dh": "0.40",
        },
        {
            "label": "clean",
            "prediction": "clean",
            "normalized_dh": "0.60",
        },
        {
            "label": "clean",
            "prediction": "stego",
            "normalized_dh": "0.90",
        },
        {
            "label": "clean",
            "prediction": "stego",
            "normalized_dh": "0.70",
        },
        {
            "label": "stego",
            "prediction": "clean",
            "normalized_dh": "0.50",
        },
        {
            "label": "stego",
            "prediction": "clean",
            "normalized_dh": "0.30",
        },
    ]

    summaries = summarize_dh_by_outcome(rows)

    assert summaries["TP"]["Count"] == 2
    assert summaries["TP"]["Mean"] == pytest.approx(0.70)
    assert summaries["TP"]["Median"] == pytest.approx(0.70)
    assert summaries["TP"]["Min"] == pytest.approx(0.60)
    assert summaries["TP"]["Max"] == pytest.approx(0.80)

    assert summaries["TN"]["Count"] == 2
    assert summaries["TN"]["Mean"] == pytest.approx(0.50)
    assert summaries["TN"]["Median"] == pytest.approx(0.50)
    assert summaries["TN"]["Min"] == pytest.approx(0.40)
    assert summaries["TN"]["Max"] == pytest.approx(0.60)

    assert summaries["FP"]["Count"] == 2
    assert summaries["FP"]["Mean"] == pytest.approx(0.80)
    assert summaries["FP"]["Median"] == pytest.approx(0.80)
    assert summaries["FP"]["Min"] == pytest.approx(0.70)
    assert summaries["FP"]["Max"] == pytest.approx(0.90)

    assert summaries["FN"]["Count"] == 2
    assert summaries["FN"]["Mean"] == pytest.approx(0.40)
    assert summaries["FN"]["Median"] == pytest.approx(0.40)
    assert summaries["FN"]["Min"] == pytest.approx(0.30)
    assert summaries["FN"]["Max"] == pytest.approx(0.50)