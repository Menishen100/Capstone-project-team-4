"""Arthur's CLI integration and detector parity checks."""

import json
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

    direct_pixels = load_image(path)
    detector_scores = {
        "chi_square": ChiSquareDetector().analyze(direct_pixels)["score"],
        "rs": RSAnalysisDetector().analyze(direct_pixels)["score"],
        "dh": DifferenceHistogramDetector().analyze(direct_pixels)["score"],
    }
    expected = combine_detector_scores(detector_scores, LOCKED_CONFIG)
    actual = analyze_image(path)

    assert actual["detector_scores"] == pytest.approx(detector_scores)
    assert actual["ensemble_score"] == pytest.approx(expected["ensemble_score"])
    assert actual["label"] == expected["label"]
    assert actual["diagnostics"]["weights"] == pytest.approx(
        {"chi_square": 0.0, "rs": 0.7, "dh": 0.3}
    )
    assert actual["diagnostics"]["threshold"] == 0.70
    assert main([str(path)]) == 0
    output = capsys.readouterr().out
    for expected_line in ("Result:", "Ensemble Score:", "Chi-square:", "RS:", "DH:"):
        assert expected_line in output


def test_json_output_reports_pipeline_result(tmp_path, capsys):
    path = tmp_path / "image.png"
    Image.fromarray(np.arange(256, dtype=np.uint8).reshape(16, 16)).save(path)
    assert main(["--json", str(path)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["label"] in {"Clean", "Suspicious"}
    assert set(result["detector_scores"]) == {"chi_square", "rs", "dh"}


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
    assert "Result:" in completed.stdout
    assert "Ensemble Score:" in completed.stdout


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


@pytest.mark.parametrize("filename,contents", [("broken.png", b"not an image")])
def test_bad_images_fail_cleanly(tmp_path, capsys, filename, contents):
    path = tmp_path / filename
    path.write_bytes(contents)
    assert main([str(path)]) == 2
    captured = capsys.readouterr()
    assert "Error:" in captured.err
    assert "Traceback" not in captured.err


def test_missing_and_unsupported_paths_fail_cleanly(tmp_path, capsys):
    assert main([str(tmp_path / "missing.png")]) == 2
    assert "does not exist" in capsys.readouterr().err
    path = tmp_path / "notes.txt"
    path.write_text("not a supported image", encoding="utf-8")
    assert main([str(path)]) == 2
    assert "cannot read image" in capsys.readouterr().err


def test_unsupported_image_format_fails_cleanly(tmp_path, capsys):
    path = tmp_path / "animated.gif"
    Image.fromarray(np.zeros((12, 12), dtype=np.uint8)).save(path, format="GIF")
    assert main([str(path)]) == 2
    assert "unsupported image format: GIF" in capsys.readouterr().err


def test_detector_failure_is_reported_without_traceback(tmp_path, monkeypatch, capsys):
    path = tmp_path / "image.png"
    Image.fromarray(np.zeros((12, 12), dtype=np.uint8)).save(path)

    class BrokenDetector:
        def analyze(self, _pixels):
            raise RuntimeError("detector unavailable")

    monkeypatch.setattr(cli, "ChiSquareDetector", BrokenDetector)
    assert main([str(path)]) == 2
    error = capsys.readouterr().err
    assert "detector analysis failed: detector unavailable" in error
    assert "Traceback" not in error


def test_missing_image_argument_uses_argparse_error(capsys):
    with pytest.raises(SystemExit) as error:
        main([])
    assert error.value.code == 2
    assert "image path is required" in capsys.readouterr().err
