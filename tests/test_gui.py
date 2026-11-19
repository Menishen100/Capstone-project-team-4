from pathlib import Path

from src import gui
from src.gui import SteganalysisGUI, format_gui_values


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


class FakeStringVar:
    """Small Tk variable substitute for callback-level GUI tests."""

    def __init__(self):
        self.value = "-"

    def set(self, value):
        self.value = value


def make_gui_without_window():
    """Build a GUI controller without opening a Tk window."""
    app = SteganalysisGUI.__new__(SteganalysisGUI)
    app.selected_image = None
    app.image_var = FakeStringVar()
    app.classification_var = FakeStringVar()
    app.ensemble_var = FakeStringVar()
    app.threshold_var = FakeStringVar()
    app.chi_var = FakeStringVar()
    app.rs_var = FakeStringVar()
    app.dh_var = FakeStringVar()
    return app


def test_select_image_stores_selection_and_clears_old_results(monkeypatch):
    app = make_gui_without_window()
    image_path = Path("dataset/clean/pair_081_clean.png")
    app.classification_var.set("Suspicious")
    monkeypatch.setattr(gui.filedialog, "askopenfilename", lambda **_kwargs: str(image_path))

    app.select_image()

    assert app.selected_image == image_path
    assert app.image_var.value == str(image_path)
    assert app.classification_var.value == "-"


def test_analyze_selected_image_displays_classification_and_scores(monkeypatch):
    app = make_gui_without_window()
    image_path = Path("dataset/clean/pair_081_clean.png")
    app.selected_image = image_path
    analysis = {
        "classification": "Clean",
        "ensemble_score": 0.3876,
        "threshold": 0.70,
        "raw_scores": {"chi_square": 0.0, "rs": 0.6217, "dh": 0.5906},
        "normalized_scores": {"chi_square": 0.0, "rs": 0.3783, "dh": 0.4094},
    }
    calls = []
    monkeypatch.setattr(gui, "analyze_image", lambda path: calls.append(path) or analysis)

    app.analyze_selected_image()

    assert calls == [image_path]
    assert app.classification_var.value == "Clean"
    assert app.ensemble_var.value == "0.3876"
    assert app.threshold_var.value == "0.70"
    assert app.chi_var.value == "0.0000 -> 0.0000"
    assert app.rs_var.value == "0.6217 -> 0.3783"
    assert app.dh_var.value == "0.5906 -> 0.4094"


def test_analyze_without_selection_shows_warning(monkeypatch):
    app = make_gui_without_window()
    warnings = []
    monkeypatch.setattr(gui.messagebox, "showwarning", lambda *args: warnings.append(args))

    app.analyze_selected_image()

    assert len(warnings) == 1
    assert warnings[0][0] == "No Image Selected"


def test_analysis_error_is_shown_without_crashing(monkeypatch):
    app = make_gui_without_window()
    app.selected_image = Path("missing.png")
    errors = []
    monkeypatch.setattr(gui, "analyze_image", lambda _path: (_ for _ in ()).throw(OSError("missing file")))
    monkeypatch.setattr(gui.messagebox, "showerror", lambda *args: errors.append(args))

    app.analyze_selected_image()

    assert len(errors) == 1
    assert errors[0][0] == "Analysis Error"
    assert errors[0][1] == "missing file"
