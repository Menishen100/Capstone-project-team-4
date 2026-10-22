"""Independent hand checks for Week 10 calibration metric safeguards."""

import pytest

from src.evaluation.calibration_metrics import (
    classification_metrics,
    ensemble_score,
    predictions_from_scores,
    validate_weights,
    validation_rows,
    verify_selected_configuration,
)


def test_metrics_match_hand_calculated_example():
    # TP=1, TN=2, FP=0, FN=1; precision=1, recall=1/2, F1=2/3.
    result = classification_metrics(
        ["clean", "stego", "stego", "clean"],
        ["clean", "stego", "clean", "clean"],
    )
    assert result == {"accuracy": 0.75, "precision": 1.0,
                      "recall": 0.5, "f1": pytest.approx(2 / 3)}


def test_metrics_zero_divisions_are_zero():
    assert classification_metrics(["clean", "clean"], ["clean", "clean"]) == {
        "accuracy": 1.0, "precision": 0.0, "recall": 0.0, "f1": 0.0
    }


def test_threshold_includes_equality_as_stego():
    assert predictions_from_scores([0.49, 0.5, 0.51], 0.5) == [
        "clean", "stego", "stego"
    ]


def test_ensemble_inverts_rs_before_vote_and_accepts_normalized_dh():
    weights = {"chi_weight": 0.0, "rs_weight": 1.0, "dh_weight": 0.0}
    assert ensemble_score(0.2, 0.2, 0.7, weights) == pytest.approx(0.8)
    assert ensemble_score(0.2, 0.8, 0.7, weights) == pytest.approx(0.2)
    assert ensemble_score(0.2, 0.5, 0.7, {
        "chi_weight": 0.0, "rs_weight": 0.0, "dh_weight": 1.0
    }) == pytest.approx(0.7)


@pytest.mark.parametrize("weights", [
    {"chi_weight": 0.2, "rs_weight": 0.2, "dh_weight": 0.2},
    {"chi_weight": -0.1, "rs_weight": 0.5, "dh_weight": 0.6},
    {"chi_weight": 0.5, "rs_weight": 0.5},
])
def test_invalid_weights_are_rejected(weights):
    with pytest.raises(ValueError):
        validate_weights(weights)


def test_selection_must_exist_in_result_rows():
    rows = [{"chi_weight": 0.5, "rs_weight": 0.3,
             "dh_weight": 0.2, "threshold": 0.5}]
    verify_selected_configuration(rows[0], rows)
    with pytest.raises(ValueError, match="does not exist"):
        verify_selected_configuration({**rows[0], "threshold": 0.55}, rows)


@pytest.mark.parametrize("split", ["held_out_test", "test"])
def test_validation_metric_inputs_reject_held_out_rows(split):
    # Guard for callers converting score-table rows into validation metrics.
    row = {"split": split, "label": "clean", "score": 0.1}
    with pytest.raises(ValueError, match="validation"):
        validation_rows([row])


def test_validation_rows_accept_only_validation_split():
    row = {"split": "validation", "label": "stego", "score": 0.8}
    assert validation_rows([row]) == [row]
