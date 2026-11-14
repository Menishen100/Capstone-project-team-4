"""Arthur's CLI integration and detector parity checks."""

import subprocess
import sys

import numpy as np
import pytest
from PIL import Image

from src import cli
from src.cli import analyze_image, main
from src.detectors import ChiSquareDetector, DifferenceHistogramDetector, RSAnalysisDetector
from src.ensemble.voting import combine_detector_scores
from src.evaluation.run_heldout_evaluation import LOCKED_CONFIG
from src.preprocessing import load_image


@pytest.mark.parametrize("mode", ["L", "RGB"])
def test_cli_matches_direct_pipeline_for_supported_modes(tmp_path, capsys, mode):
    rng = np.random.default_rng(42)
    shape = (64, 64) if mode == "L" else (64, 64, 3)
    pixels = rng.integers(0, 256, size=shape, dtype=np.uint8)
    path = tmp_path / f"sample-{mode}.png"
    Image.fromarray(pixels, mode=mode).save(path)

    image = load_image(path)
    raw_scores = {
        "chi_square": ChiSquareDetector().analyze(image)["score"],
        "rs": RSAnalysisDetector().analyze(image)["score"],
        "dh": DifferenceHistogramDetector().analyze(image)["score"],
    }
    expected = combine_detector_scores(raw_scores, LOCKED_CONFIG)
    actual = analyze_image(path)

    assert actual["raw_scores"] == pytest.approx(raw_scores)
    assert actual["ensemble_score"] == pytest.approx(expected["ensemble_score"])
    assert actual["classification"] == expected["label"]
    assert actual["weights"] == pytest.approx(
        {"chi_square": 0.0, "rs": 0.7, "dh": 0.3}
    )
    assert actual["threshold"] == 0.70
    assert main([str(path)]) == 0
    output = capsys.readouterr().out
    for expected_line in (
        "Final classification:",
        "Ensemble score (not a probability):",
        "Chi-square:",
        "RS:",
        "DH:",
    ):
        assert expected_line in output


@pytest.mark.parametrize("invocation", [["-m", "src.cli"], ["src/cli.py"]])
def test_both_documented_invocation_forms_work(tmp_path, invocation):
    path = tmp_path / "image.png"
    Image.fromarray(np.arange(256, dtype=np.uint8).reshape(16, 16)).save(path)
    completed = subprocess.run(
        [sys.executable, *invocation, str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert "Final classification:" in completed.stdout
    assert "Ensemble score" in completed.stdout


def test_threshold_boundary_uses_existing_voting_rule():
    at_threshold = combine_detector_scores(
        {"chi_square": 0.0, "rs": 0.0, "dh": 1.0}, LOCKED_CONFIG
    )
    below = combine_detector_scores(
        {"chi_square": 0.0, "rs": 0.01, "dh": 1.0}, LOCKED_CONFIG
    )
    assert at_threshold["ensemble_score"] == pytest.approx(0.70)
    assert at_threshold["label"] == "Suspicious"
    assert below["ensemble_score"] < 0.70
    assert below["label"] == "Clean"


def test_corrupt_and_unsupported_files_fail_cleanly(tmp_path, capsys):
    path = tmp_path / "broken.png"
    path.write_bytes(b"not an image")
    with pytest.raises(SystemExit) as error:
        main([str(path)])
    assert error.value.code == 2
    stderr = capsys.readouterr().err
    assert "could not analyze" in stderr
    assert "Traceback" not in stderr

    path = tmp_path / "notes.txt"
    path.write_text("not a supported image", encoding="utf-8")
    with pytest.raises(SystemExit) as error:
        main([str(path)])
    assert error.value.code == 2
    assert "could not analyze" in capsys.readouterr().err


def test_missing_path_fails_cleanly(tmp_path, capsys):
    with pytest.raises(SystemExit) as error:
        main([str(tmp_path / "missing.png")])
    assert error.value.code == 2
    stderr = capsys.readouterr().err
    assert "could not analyze" in stderr
    assert "Traceback" not in stderr


def test_detector_failure_is_reported_without_traceback(tmp_path, monkeypatch, capsys):
    path = tmp_path / "image.png"
    Image.fromarray(np.zeros((12, 12), dtype=np.uint8)).save(path)

    class BrokenDetector:
        def analyze(self, _image):
            raise RuntimeError("detector unavailable")

    monkeypatch.setattr(
        cli,
        "default_detectors",
        lambda: {
            "chi_square": BrokenDetector(),
            "rs": BrokenDetector(),
            "dh": BrokenDetector(),
        },
    )
    with pytest.raises(SystemExit) as error:
        main([str(path)])
    assert error.value.code == 2
    stderr = capsys.readouterr().err
    assert "detector analysis failed: detector unavailable" in stderr
    assert "Traceback" not in stderr


def test_missing_image_argument_uses_argparse_error(capsys):
    with pytest.raises(SystemExit) as error:
        main([])
    assert error.value.code == 2
    assert "the following arguments are required: image" in capsys.readouterr().err
