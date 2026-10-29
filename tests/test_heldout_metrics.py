"""Tests for Arthur's independent Week 11 held-out result verification."""

import pytest

from src.evaluation.calibration_metrics import classification_metrics, ensemble_score
from src.evaluation.heldout_metrics import (
    LOCKED_WEIGHTS,
    confusion_matrix_counts,
    verify_heldout_results,
)


def test_hand_calculated_metrics_and_all_confusion_matrix_cells():
    truth = ["stego", "clean", "clean", "stego"]
    predicted = ["stego", "clean", "stego", "clean"]
    assert confusion_matrix_counts(truth, predicted) == {
        "tp": 1, "tn": 1, "fp": 1, "fn": 1
    }
    assert classification_metrics(truth, predicted) == {
        "accuracy": 0.5, "precision": 0.5, "recall": 0.5, "f1": 0.5
    }


def _valid_artifacts():
    metadata = [{"source_id": f"source-{i:03}", "split": "held_out_test"}
                for i in range(1, 21)]
    rows = []
    for i in range(1, 21):
        for label in ("clean", "stego"):
            components = {"normalized_chi": 0.2, "normalized_rs": 0.1,
                          "normalized_dh": 0.5}
            score = ensemble_score(components["normalized_chi"],
                                   components["normalized_rs"],
                                   components["normalized_dh"], LOCKED_WEIGHTS)
            rows.append({"source_id": f"source-{i:03}", "label": label,
                         **components, "ensemble_score": score,
                         "prediction": "stego" if score >= 0.7 else "clean"})
    summary = {
        "configuration": {"weights": LOCKED_WEIGHTS, "threshold": 0.7},
        "metrics": {"accuracy": 0.5, "precision": 0.5,
                    "recall": 1.0, "f1": 2 / 3},
        "confusion_matrix": {"tp": 20, "tn": 0, "fp": 20, "fn": 0},
    }
    return rows, metadata, summary


def test_verifies_40_heldout_rows_configuration_metrics_and_counts():
    rows, metadata, summary = _valid_artifacts()
    result = verify_heldout_results(rows, metadata, summary)
    assert result["sample_count"] == 40
    assert result["class_counts"] == {"clean": 20, "stego": 20}
    assert result["confusion_matrix"] == {"tp": 20, "tn": 0, "fp": 20, "fn": 0}
    assert result["metrics"] == {"accuracy": 0.5, "precision": 0.5,
                                  "recall": 1.0, "f1": pytest.approx(2 / 3)}


def test_rejects_development_or_validation_rows():
    rows, metadata, summary = _valid_artifacts()
    rows[0]["source_id"] = "source-development"
    with pytest.raises(ValueError, match="only the 20 held-out sources"):
        verify_heldout_results(rows, metadata, summary)


def test_rejects_locked_configuration_change():
    rows, metadata, summary = _valid_artifacts()
    summary["configuration"]["threshold"] = 0.71
    with pytest.raises(ValueError, match="threshold mismatch"):
        verify_heldout_results(rows, metadata, summary)


def test_rejects_wrong_ensemble_math_or_predictions():
    rows, metadata, summary = _valid_artifacts()
    rows[0]["ensemble_score"] = 0.01
    with pytest.raises(ValueError, match="ensemble_score mismatch"):
        verify_heldout_results(rows, metadata, summary)


def test_rejects_incorrect_reported_metric_or_confusion_cell():
    rows, metadata, summary = _valid_artifacts()
    summary["confusion_matrix"]["fp"] = 19
    with pytest.raises(ValueError, match="fp mismatch"):
        verify_heldout_results(rows, metadata, summary)
