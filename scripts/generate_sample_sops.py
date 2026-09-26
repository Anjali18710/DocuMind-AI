"""
Generates the illustrative sample SOP PDFs used by the demo.

    python scripts/generate_sample_sops.py

Writes:
  data/raw/*.pdf                 — loaded into the knowledge base on first run
  data/raw/..._SCANNED.pdf       — image-only PDF (tests OCR)
  data/samples/..._Rev04.pdf     — newer revision to demo automatic replacement

Needs a Unicode TTF font (DejaVu Sans). Pass --font /path/to/font.ttf if it
is not found automatically. The three original SOPs in data/raw/ are not touched.
"""

import argparse
import os
import random
import sys
from pathlib import Path

from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
from sample_sop_content import REVISION_DEMO, SCANNED_SOP, SOPS  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DISCLAIMER = "Illustrative sample SOP created for the DocuMind AI demo. Not an official SAIL document."
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "C:/Windows/Fonts/DejaVuSans.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "/Library/Fonts/Arial Unicode.ttf",
]


def find_font(explicit=None):
    for path in [explicit] + FONT_CANDIDATES:
        if path and os.path.exists(path):
            return path
    raise SystemExit("No TTF font found. Pass --font /path/to/DejaVuSans.ttf")


def header_lines(sop):
    return [
        sop["file"].replace(".pdf", ""),
        "BOKARO STEEL PLANT — ILLUSTRATIVE SAMPLE",
        "Standard Operating Procedure",
        f"SOP No: {sop['sop_no']}",
        f"Title: {sop['title']}",
        f"Department: {sop['department']}",
        f"Revision: {sop['revision']}",
        f"Date: {sop['date']}",
    ]


class SopPDF(FPDF):
    def footer(self):
        self.set_y(-12)
        self.set_font("Body", size=7)
        self.set_text_color(120, 120, 120)
        self.cell(0, 5, f"{DISCLAIMER}   Page {self.page_no()}", align="C")
        self.set_text_color(0, 0, 0)


def write_text_pdf(sop, out_path, font):
    pdf = SopPDF(format="A4")
    pdf.add_font("Body", "", font)
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    width = pdf.w - pdf.l_margin - pdf.r_margin
    for i, line in enumerate(header_lines(sop)):
        pdf.set_font("Body", size=13 if i in (1, 2) else 10)
        pdf.multi_cell(width, 6, line, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    for line in sop["body"].strip().split("\n"):
        is_heading = line[:2].strip().rstrip(".").isdigit() and line.split(" ", 1)[-1].isupper()
        pdf.set_font("Body", size=11 if is_heading else 10)
        if is_heading:
            pdf.ln(1.5)
        pdf.multi_cell(width, 5.6, line, new_x="LMARGIN", new_y="NEXT")
    pdf.output(str(out_path))


def write_scanned_pdf(sop, out_path, font):
    """Render the SOP as a slightly skewed greyscale 'photocopy' — no text layer."""
    random.seed(7)
    page_w, page_h = 1654, 2339  # A4 at 200 DPI
    img = Image.new("L", (page_w, page_h), 250)
    draw = ImageDraw.Draw(img)
    f_body = ImageFont.truetype(font, 30)
    f_head = ImageFont.truetype(font, 36)
    y = 110
    lines = header_lines(sop) + [""] + sop["body"].strip().split("\n")
    for i, line in enumerate(lines):
        fnt = f_head if i in (1, 2) else f_body
        draw.text((120, y), line, fill=25, font=fnt)
        y += 50 if fnt is f_head else 44
    draw.text((120, page_h - 90), DISCLAIMER, fill=110, font=ImageFont.truetype(font, 20))
    # photocopy look: speckle noise, slight blur, slight rotation
    for _ in range(4000):
        img.putpixel((random.randrange(page_w), random.randrange(page_h)), random.randint(150, 220))
    img = img.filter(ImageFilter.GaussianBlur(0.6)).rotate(0.6, fillcolor=250, expand=False)
    tmp = out_path.with_suffix(".png")
    img.save(tmp)
    pdf = FPDF(format="A4")
    pdf.add_page()
    pdf.image(str(tmp), x=0, y=0, w=210, h=297)
    pdf.output(str(out_path))
    tmp.unlink()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--font")
    font = find_font(parser.parse_args().font)
    raw, samples = ROOT / "data" / "raw", ROOT / "data" / "samples"
    raw.mkdir(parents=True, exist_ok=True)
    samples.mkdir(parents=True, exist_ok=True)
    for sop in SOPS:
        write_text_pdf(sop, raw / sop["file"], font)
        print("✓", sop["file"])
    write_scanned_pdf(SCANNED_SOP, raw / SCANNED_SOP["file"], font)
    print("✓", SCANNED_SOP["file"], "(scanned)")
    write_text_pdf(REVISION_DEMO, samples / REVISION_DEMO["file"], font)
    print("✓", "samples/" + REVISION_DEMO["file"])


if __name__ == "__main__":
    main()
