"""Optional graphical interface for the Multi-Feature Steganalysis Toolkit."""

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from src.cli import analyze_image


def format_gui_values(analysis):
    """Convert an analysis result into strings for GUI display."""

    raw_scores = analysis["raw_scores"]
    normalized_scores = analysis["normalized_scores"]

    return {
        "classification": str(analysis["classification"]),
        "ensemble_score": f"{float(analysis['ensemble_score']):.4f}",
        "threshold": f"{float(analysis['threshold']):.2f}",
        "chi_square": (
            f"{float(raw_scores['chi_square']):.4f}"
            f" -> "
            f"{float(normalized_scores['chi_square']):.4f}"
        ),
        "rs": (
            f"{float(raw_scores['rs']):.4f}"
            f" -> "
            f"{float(normalized_scores['rs']):.4f}"
        ),
        "dh": (
            f"{float(raw_scores['dh']):.4f}"
            f" -> "
            f"{float(normalized_scores['dh']):.4f}"
        ),
    }


class SteganalysisGUI:
    """Simple user interface for analyzing one image at a time."""

    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Feature Steganalysis Toolkit")
        self.root.geometry("700x500")

        self.selected_image = None

        self.image_var = tk.StringVar(
            value = "No image selected"
        )

        self.classification_var = tk.StringVar(
            value = "-"
        )

        self.ensemble_var = tk.StringVar(
            value = "-"
        )

        self.threshold_var = tk.StringVar(
            value = "-"
        )

        self.chi_var = tk.StringVar(
            value = "-"
        )

        self.rs_var = tk.StringVar(
            value = "-"
        )

        self.dh_var = tk.StringVar(
            value = "-"
        )

        self.build_interface()


    def build_interface(self):
        """Create the GUI controls."""

        title = ttk.Label(
            self.root,
            text = "Multi-Feature Steganalysis Toolkit",
            font = ("Arial", 18, "bold"),
        )

        title.pack(
            pady = (20, 10)
        )

        subtitle = ttk.Label(
            self.root,
            text = "Release-Candidate Image Analysis",
        )

        subtitle.pack(
            pady = (0, 20)
        )

        image_frame = ttk.LabelFrame(
            self.root,
            text = "Image Selection",
            padding=15,
        )

        image_frame.pack(
            fill = "x",
            padx = 20,
            pady = 10,
        )

        image_label = ttk.Label(
            image_frame,
            textvariable = self.image_var,
            wraplength = 620,
        )

        image_label.pack(
            pady = (0, 10)
        )

        select_button = ttk.Button(
            image_frame,
            text = "Select Image",
            command = self.select_image,
        )

        select_button.pack(
            side = "left",
            padx = 5,
        )

        analyze_button = ttk.Button(
            image_frame,
            text = "Analyze",
            command = self.analyze_selected_image,
        )

        analyze_button.pack(
            side = "left",
            padx = 5,
        )

        results_frame = ttk.LabelFrame(
            self.root,
            text = "Analysis Results",
            padding = 15,
        )

        results_frame.pack(
            fill = "both",
            expand = True,
            padx = 20,
            pady = 10,
        )

        self.add_result_row(
            results_frame,
            0,
            "Final Classification:",
            self.classification_var,
        )

        self.add_result_row(
            results_frame,
            1,
            "Ensemble Score:",
            self.ensemble_var,
        )

        self.add_result_row(
            results_frame,
            2,
            "Decision Threshold:",
            self.threshold_var,
        )

        self.add_result_row(
            results_frame,
            3,
            "Chi-square:",
            self.chi_var,
        )

        self.add_result_row(
            results_frame,
            4,
            "RS:",
            self.rs_var,
        )

        self.add_result_row(
            results_frame,
            5,
            "Difference Histogram:",
            self.dh_var,
        )

        explanation = ttk.Label(
            results_frame,
            text=(
                "Detector scores are displayed as "
                "raw score -> direction-aligned suspiciousness."
            ),
            wraplength = 600,
        )

        explanation.grid(
            row = 6,
            column = 0,
            columnspan = 2,
            sticky = "w",
            pady = (15, 0),
        )


    def add_result_row(
        self,
        parent,
        row,
        label_text,
        value_variable,
    ):
        """Add one labeled result to the results panel."""

        label = ttk.Label(
            parent,
            text = label_text,
        )

        label.grid(
            row = row,
            column = 0,
            sticky = "w",
            padx = (0, 20),
            pady = 6,
        )

        value = ttk.Label(
            parent,
            textvariable = value_variable,
        )

        value.grid(
            row = row,
            column = 1,
            sticky = "w",
            pady = 6,
        )


    def select_image(self):
        """Allow the user to choose an image."""

        filename = filedialog.askopenfilename(
            title = "Select Image",
            filetypes=[
                (
                    "Image files",
                    "*.png *.jpg *.jpeg *.bmp *.tif *.tiff",
                ),
                (
                    "All files",
                    "*.*",
                ),
            ],
        )

        if not filename:
            return

        self.selected_image = Path(filename)

        self.image_var.set(
            str(self.selected_image)
        )

        self.clear_results()


    def analyze_selected_image(self):
        """Analyze the currently selected image."""

        if self.selected_image is None:
            messagebox.showwarning(
                "No Image Selected",
                "Select an image before running the analysis.",
            )

            return

        try:
            analysis = analyze_image(
                self.selected_image
            )

        except (OSError, ValueError, RuntimeError) as error:
            messagebox.showerror(
                "Analysis Error",
                str(error),
            )

            return

        values = format_gui_values(
            analysis
        )

        self.classification_var.set(
            values["classification"]
        )

        self.ensemble_var.set(
            values["ensemble_score"]
        )

        self.threshold_var.set(
            values["threshold"]
        )

        self.chi_var.set(
            values["chi_square"]
        )

        self.rs_var.set(
            values["rs"]
        )

        self.dh_var.set(
            values["dh"]
        )


    def clear_results(self):
        """Clear results when a new image is selected."""

        self.classification_var.set("-")
        self.ensemble_var.set("-")
        self.threshold_var.set("-")
        self.chi_var.set("-")
        self.rs_var.set("-")
        self.dh_var.set("-")


def main():
    """Launch the graphical interface."""

    root = tk.Tk()

    SteganalysisGUI(
        root
    )

    root.mainloop()


if __name__ == "__main__":
    main()