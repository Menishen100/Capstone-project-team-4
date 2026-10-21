"""Run Arthur's focused tests and save their terminal output as a PNG."""

from pathlib import Path
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
TEST = "tests/test_calibration_metrics.py"
OUTPUT = ROOT / "docs" / "assets" / "week10-progress" / "arthur-calibration-tests.png"


def main() -> int:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", TEST, "-q"], cwd=ROOT,
        capture_output=True, text=True,
    )
    lines = [f"> python -m pytest {TEST} -q", "", *result.stdout.splitlines()]
    if result.stderr.strip():
        lines.extend(["", *result.stderr.splitlines()])
    lines.append("")
    lines.append(f"Process exit code: {result.returncode}")

    font_path = Path("C:/Windows/Fonts/consola.ttf")
    font = ImageFont.truetype(str(font_path), 22) if font_path.exists() else ImageFont.load_default()
    line_height = 34
    width, height = 1200, max(190, 92 + line_height * len(lines))
    image = Image.new("RGB", (width, height), "#111827")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((24, 20, width - 24, height - 20), radius=14,
                           fill="#0b1220", outline="#334155", width=2)
    draw.text((48, 37), "Arthur Week 10 | Calibration verification", font=font,
              fill="#93c5fd")
    y = 83
    for line in lines:
        color = "#86efac" if "passed" in line or "exit code: 0" in line else "#e5e7eb"
        draw.text((48, y), line, font=font, fill=color)
        y += line_height
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT)
    print("\n".join(lines))
    print(f"Evidence image: {OUTPUT}")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
