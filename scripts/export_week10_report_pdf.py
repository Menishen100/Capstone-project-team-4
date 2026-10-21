"""Render Arthur's Week 10 calibration verification report to PDF."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "week10-arthur-calibration-verification.md"
OUTPUT = ROOT / "output" / "pdf" / "week10-arthur-calibration-verification.pdf"


def main() -> None:
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ReportTitle", parent=styles["Title"], alignment=TA_CENTER,
        textColor=colors.HexColor("#17324D"), fontSize=20, leading=25,
        spaceAfter=18,
    ))
    styles.add(ParagraphStyle(
        name="Section", parent=styles["Heading2"], textColor=colors.HexColor("#205375"),
        spaceBefore=12, spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="BulletText", parent=styles["BodyText"], leftIndent=16,
        firstLineIndent=-10, spaceAfter=3, leading=11.5, fontSize=9.5,
    ))
    styles.add(ParagraphStyle(
        name="CodeText", parent=styles["Code"], backColor=colors.HexColor("#F1F4F7"),
        borderPadding=7, leftIndent=10, rightIndent=10, spaceBefore=4,
        spaceAfter=8,
    ))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT), pagesize=letter, rightMargin=0.78 * inch,
        leftMargin=0.78 * inch, topMargin=0.62 * inch,
        bottomMargin=0.62 * inch, title="Arthur Week 10 Calibration Verification",
        author="Arthur - Capstone Project Team 4",
    )
    story = []
    in_code = False
    code_lines = []
    for raw in SOURCE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("```"):
            if in_code:
                story.append(Paragraph("<br/>".join(code_lines), styles["CodeText"]))
                code_lines = []
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_lines.append(line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
        elif not line:
            story.append(Spacer(1, 3))
        elif line.startswith("# "):
            story.append(Paragraph(line[2:], styles["ReportTitle"]))
        elif line.startswith("## "):
            story.append(Paragraph(line[3:], styles["Section"]))
        elif line.startswith("- "):
            text = line[2:].replace("`", "")
            story.append(Paragraph("&#8226; " + text, styles["BulletText"]))
        else:
            text = line.replace("`", "")
            story.append(Paragraph(text, styles["BodyText"]))
            story.append(Spacer(1, 5))
    doc.build(story)
    print(OUTPUT)


if __name__ == "__main__":
    main()
