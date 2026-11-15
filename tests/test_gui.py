from src.gui import format_gui_values


def test_format_gui_values():
    """GUI should format an existing analysis result without changing it."""

    analysis = {
        "classification": "Suspicious",
        "ensemble_score": 0.806477,
        "threshold": 0.70,
        "raw_scores": {
            "chi_square": 0.1000,
            "rs": 0.2000,
            "dh": 0.3000,
        },
        "normalized_scores": {
            "chi_square": 0.1000,
            "rs": 0.8000,
            "dh": 0.7000,
        },
    }

    values = format_gui_values(
        analysis
    )

    assert values["classification"] == "Suspicious"

    assert values["ensemble_score"] == "0.8065"

    assert values["threshold"] == "0.70"

    assert values["chi_square"] == "0.1000 -> 0.1000"

    assert values["rs"] == "0.2000 -> 0.8000"

    assert values["dh"] == "0.3000 -> 0.7000"