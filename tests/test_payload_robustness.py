import csv
import pytest
import src.evaluation.run_payload_robustness as payload_robustness


def test_locked_week12_configuration():
    """Verify that the Week 12 experiment uses the locked configuration."""

    assert payload_robustness.PAYLOAD_RATES == [
        0.10,
        0.25,
        0.50,
        0.75,
        1.00,
    ]

    assert payload_robustness.CHI_WEIGHT == 0.00
    assert payload_robustness.RS_WEIGHT == 0.70
    assert payload_robustness.DH_WEIGHT == 0.30

    assert payload_robustness.DECISION_THRESHOLD == 0.70


def test_get_payload_directory():
    """Verify that payload rates map to the correct Week 12 folders."""

    assert (
        payload_robustness.get_payload_directory(0.10)
        == payload_robustness.EXPERIMENT_DIR / "payload_010"
    )

    assert (
        payload_robustness.get_payload_directory(0.25)
        == payload_robustness.EXPERIMENT_DIR / "payload_025"
    )

    assert (
        payload_robustness.get_payload_directory(0.50)
        == payload_robustness.EXPERIMENT_DIR / "payload_050"
    )

    assert (
        payload_robustness.get_payload_directory(0.75)
        == payload_robustness.EXPERIMENT_DIR / "payload_075"
    )

    assert (
        payload_robustness.get_payload_directory(1.00)
        == payload_robustness.EXPERIMENT_DIR / "payload_100"
    )


def test_summarize_dh_by_payload():
    """Verify that DH results are summarized correctly by payload."""

    dh_results = []

    for index, payload_rate in enumerate(
        payload_robustness.PAYLOAD_RATES
    ):
        base_value = 0.10 * (index + 1)

        dh_results.append(
            {
                "Payload_rate": payload_rate,
                "Raw_dh_roughness": base_value,
                "Dh_score": base_value,
                "Normalized_dh": base_value,
            }
        )

        dh_results.append(
            {
                "Payload_rate": payload_rate,
                "Raw_dh_roughness": base_value + 0.20,
                "Dh_score": base_value + 0.20,
                "Normalized_dh": base_value + 0.20,
            }
        )

    summaries = payload_robustness.summarize_dh_by_payload(
        dh_results
    )

    assert len(summaries) == 5

    for index, summary in enumerate(summaries):

        base_value = 0.10 * (index + 1)

        expected_mean = base_value + 0.10

        assert summary["Image_count"] == 2

        assert summary["Mean_raw_dh_roughness"] == pytest.approx(
            expected_mean
        )

        assert summary["Mean_dh_score"] == pytest.approx(
            expected_mean
        )

        assert summary["Mean_normalized_dh"] == pytest.approx(
            expected_mean
        )


def test_summarize_ensemble_by_payload():
    """Verify ensemble means and detection rates by payload."""

    ensemble_results = []

    for index, payload_rate in enumerate(
        payload_robustness.PAYLOAD_RATES
    ):
        base_score = 0.40 + (0.10 * index)

        ensemble_results.append(
            {
                "Payload_rate": payload_rate,
                "Ensemble_score": base_score,
                "Prediction": "Stego",
            }
        )

        second_prediction = (
            "Stego"
            if index >= 2
            else "Clean"
        )

        ensemble_results.append(
            {
                "Payload_rate": payload_rate,
                "Ensemble_score": base_score + 0.20,
                "Prediction": second_prediction,
            }
        )

    summaries = (
        payload_robustness.summarize_ensemble_by_payload(
            ensemble_results
        )
    )

    assert len(summaries) == 5

    expected_detection_rates = [
        0.50,
        0.50,
        1.00,
        1.00,
        1.00,
    ]

    for index, summary in enumerate(summaries):

        expected_mean = (
            0.50
            + (0.10 * index)
        )

        assert summary["Image_count"] == 2

        assert summary["Mean_ensemble_score"] == pytest.approx(
            expected_mean
        )

        assert summary["Detection_rate"] == pytest.approx(
            expected_detection_rates[index]
        )


def test_save_payload_robustness_csv(
    tmp_path,
    monkeypatch,
):
    """Verify that Week 12 results are written correctly to CSV."""

    temporary_csv = (
        tmp_path
        / "week12_payload_robustness.csv"
    )

    monkeypatch.setattr(
        payload_robustness,
        "RESULT_PATH",
        temporary_csv,
    )

    ensemble_results = [
        {
            "Source_number": 81,
            "Payload_rate": 0.10,
            "Stego_image": "pair_081_stego.png",
            "Chi_score": 0.0,
            "Normalized_chi": 0.0,
            "RS_score": 0.50,
            "Normalized_rs": 0.50,
            "DH_score": 0.40,
            "Normalized_dh": 0.60,
            "Ensemble_score": 0.53,
            "Prediction": "Clean",
            "Expected_label": "Stego",
            "Correct": False,
        },
        {
            "Source_number": 100,
            "Payload_rate": 1.00,
            "Stego_image": "pair_100_stego.png",
            "Chi_score": 1.0,
            "Normalized_chi": 1.0,
            "RS_score": 0.10,
            "Normalized_rs": 0.90,
            "DH_score": 0.20,
            "Normalized_dh": 0.80,
            "Ensemble_score": 0.87,
            "Prediction": "Stego",
            "Expected_label": "Stego",
            "Correct": True,
        },
    ]

    result_path = (
        payload_robustness.save_payload_robustness_csv(
            ensemble_results
        )
    )

    assert result_path == temporary_csv

    assert temporary_csv.exists()

    with temporary_csv.open(
        "r",
        newline = "",
        encoding = "utf-8",
    ) as csv_file:

        reader = csv.DictReader(
            csv_file
        )

        rows = list(
            reader
        )

    assert len(rows) == 2

    assert rows[0]["Source_number"] == "81"
    assert rows[0]["Prediction"] == "Clean"
    assert rows[0]["Correct"] == "False"

    assert rows[1]["Source_number"] == "100"
    assert rows[1]["Prediction"] == "Stego"
    assert rows[1]["Correct"] == "True"