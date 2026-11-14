"""Render a compact visual evidence summary from the generated Week 12 CSV."""

from __future__ import annotations

import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "week12_error_cases.csv"
OUTPUT = ROOT / "docs" / "assets" / "week12-progress" / "arthur-week12-error-summary.png"


def main() -> None:
    with INPUT.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    false_negatives = [row for row in rows if row["error_type"] == "false_negative"]
    false_positives = [row for row in rows if row["error_type"] == "false_positive"]

    image = Image.new("RGB", (1600, 900), "#f7f8fa")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    title_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 34)
    subtitle_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 20)
    draw.text((60, 35), "Week 12 held-out error-case analysis", font=title_font, fill="#1d2733")
    draw.text((60, 88), "Official Week 11 rows | locked threshold = 0.70 | read-only analysis", font=subtitle_font, fill="#596574")

    draw.rounded_rectangle((55, 145, 505, 670), radius=16, fill="white", outline="#d8dee7", width=2)
    draw.text((85, 175), "Confusion groups", font=subtitle_font, fill="#1d2733")
    counts = [("TP", 9, "#2e8b57"), ("TN", 16, "#2e8b57"), ("FP", len(false_positives), "#c44747"), ("FN", len(false_negatives), "#c44747")]
    for index, (label, value, color) in enumerate(counts):
        y = 245 + index * 95
        draw.text((90, y + 8), label, font=subtitle_font, fill="#303b48")
        draw.rounded_rectangle((165, y, 165 + value * 15, y + 46), radius=8, fill=color)
        draw.text((180 + value * 15, y + 12), str(value), font=subtitle_font, fill="#1d2733")

    chart = (560, 145, 1540, 670)
    draw.rounded_rectangle(chart, radius=16, fill="white", outline="#d8dee7", width=2)
    draw.text((595, 175), "Ensemble scores by error source", font=subtitle_font, fill="#1d2733")
    left, top, right, bottom = 660, 235, 1490, 575
    low, high = 0.40, 0.83
    for tick in (0.4, 0.5, 0.6, 0.7, 0.8):
        y = bottom - (tick - low) / (high - low) * (bottom - top)
        draw.line((left, y, right, y), fill="#e6e9ee", width=2)
        draw.text((595, y - 8), f"{tick:.1f}", font=font, fill="#596574")
    threshold_y = bottom - (0.70 - low) / (high - low) * (bottom - top)
    for x in range(left, right, 20):
        draw.line((x, threshold_y, min(x + 10, right), threshold_y), fill="#222222", width=2)
    draw.text((right - 125, threshold_y - 28), "threshold 0.70", font=font, fill="#222222")
    cases = [(row, "#c44747", -12) for row in false_negatives] + [(row, "#e38b2c", 12) for row in false_positives]
    n = len(cases)
    for idx, (row, color, offset) in enumerate(cases):
        x = left + 22 + idx * ((right - left - 44) / max(1, n - 1))
        score = float(row["ensemble_score"])
        y = bottom - (score - low) / (high - low) * (bottom - top)
        draw.ellipse((x - 9, y - 9, x + 9, y + 9), fill=color)
        draw.text((x - 14, bottom + 15), row["source_id"][-3:], font=font, fill="#596574")
    draw.text((680, 625), "Red = false negative     Orange = false positive", font=font, fill="#596574")
    draw.text((60, 710), "FN: " + ", ".join(row["source_id"] for row in false_negatives), font=font, fill="#4b5663")
    draw.text((60, 745), "FP: " + ", ".join(row["source_id"] for row in false_positives), font=font, fill="#4b5663")
    draw.text((60, 825), "Generated from data/week12_error_cases.csv", font=font, fill="#596574")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    main()
