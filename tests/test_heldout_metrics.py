"""Tests for Arthur's independent Week 11 held-out result verification."""

import pytest

from src.ensemble.normalization import normalize_chi_square, normalize_dh, normalize_rs
from src.ensemble.voting import EnsembleConfig, combine_detector_scores
from src.evaluation.calibration_metrics import classification_metrics
from src.evaluation.heldout_metrics import (
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
    metadata = [{"source_id": f"source-{i:03}", "split": "held_out_test",
                 "clean_filename": f"pair_{i:03}_clean.png",
                 "stego_filename": f"pair_{i:03}_stego.png"}
                for i in range(1, 21)]
    rows = []
    for i in range(1, 21):
        for label in ("clean", "stego"):
            suspicious = (label == "stego" and i <= 10) or (label == "clean" and i > 10)
            raw = {"chi_square": 0.2, "rs": 0.1 if suspicious else 0.9,
                   "dh": 0.1 if suspicious else 0.9}
            normalized = {"normalized_chi": normalize_chi_square(raw["chi_square"]),
                          "normalized_rs": normalize_rs(raw["rs"]),
                          "normalized_dh": normalize_dh(raw["dh"])}
            decision = combine_detector_scores(
                raw, EnsembleConfig(chi_square_weight=0.0, rs_weight=0.7,
                                    dh_weight=0.3, threshold=0.7)
            )
            rows.append({
                "source_id": f"source-{i:03}", "label": label,
                "filename": f"pair_{i:03}_{label}.png", "split": "held_out_test",
                "chi_square_score": raw["chi_square"], "rs_score": raw["rs"],
                "dh_score": raw["dh"], **normalized,
                "ensemble_score": decision["ensemble_score"],
                "prediction": "stego" if decision["label"] == "Suspicious" else "clean",
            })
    summary = {
        "configuration": {"chi_square_weight": 0.0, "rs_weight": 0.7,
                           "dh_weight": 0.3, "threshold": 0.7},
        "metrics": {"accuracy": 0.5, "precision": 0.5,
                    "recall": 0.5, "f1": 0.5},
        "confusion_matrix": {"true_positive": 10, "true_negative": 10,
                             "false_positive": 10, "false_negative": 10},
        "evaluation_split": "held_out_test",
        "image_counts": {"clean": 20, "stego": 20, "total": 40},
    }
    return rows, metadata, summary


def test_verifies_40_heldout_rows_configuration_metrics_and_counts():
    rows, metadata, summary = _valid_artifacts()
    result = verify_heldout_results(rows, metadata, summary)
    assert result["sample_count"] == 40
    assert result["class_counts"] == {"clean": 20, "stego": 20}
    assert result["confusion_matrix"] == {"tp": 10, "tn": 10, "fp": 10, "fn": 10}
    assert result["metrics"] == {"accuracy": 0.5, "precision": 0.5,
                                  "recall": 0.5, "f1": 0.5}


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
