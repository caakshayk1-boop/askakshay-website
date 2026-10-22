from __future__ import annotations

import copy
import shutil
from pathlib import Path

from pypdf import PdfReader, PdfWriter, Transformation
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "askakshay-free-sampler.pdf"
BUILD = ROOT / ".sampler-build"
OVERVIEW = BUILD / "overview.pdf"
CTA = BUILD / "cta.pdf"

BLUEBOOK = Path(
    "/Users/akshaykumarkothari/omnirush.ai/.opencode/omnirush/inbox/chat-attachments/"
    "ses_ea0d424aaffeKERS2h2P127s0C/621de9c8-b99f-4117-a533-f1b5719af82a-"
    "App-Builders-Bluebook-Capsule-Bites.pdf"
)
ROAM = Path(
    "/Users/akshaykumarkothari/omnirush.ai/.opencode/omnirush/inbox/chat-attachments/"
    "ses_ea0d424aaffeKERS2h2P127s0C/f741a7d1-7848-440b-8dec-2d92c49c0e77-"
    "The-Roam-Edit-Pill-Edition.pdf"
)

W, H = A4
M = 22 * mm

INK = colors.HexColor("#2D2117")
MUTED = colors.HexColor("#6D675F")
BLUE = colors.HexColor("#4A74E8")
SKY = colors.HexColor("#EAF3F8")
LINE = colors.HexColor("#C8D7E1")
OLIVE = colors.HexColor("#8E9870")
WHITE = colors.white


def style(name: str, **kwargs) -> ParagraphStyle:
    base = dict(fontName="Helvetica", fontSize=10, leading=13, textColor=INK)
    base.update(kwargs)
    return ParagraphStyle(name, **base)


def draw_para(c: canvas.Canvas, text: str, x: float, y_top: float, width: float,
              max_height: float, pstyle: ParagraphStyle) -> float:
    """Draw a Paragraph inside a bounded box, shrinking only if necessary."""
    current = pstyle
    for _ in range(12):
        p = Paragraph(text, current)
        _, h = p.wrap(width, max_height)
        if h <= max_height + 0.1:
            p.drawOn(c, x, y_top - h)
            return h
        size = max(7.0, current.fontSize - 0.7)
        current = ParagraphStyle(
            current.name + "-fit",
            parent=current,
            fontSize=size,
            leading=max(8.5, size * 1.22),
        )
    p = Paragraph(text, current)
    _, h = p.wrap(width, max_height)
    p.drawOn(c, x, y_top - min(h, max_height))
    return min(h, max_height)


def rounded_card(c: canvas.Canvas, x: float, y: float, w: float, h: float,
                 fill, stroke=LINE, radius=7, bar=None):
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(0.8)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1)
    if bar:
        c.setFillColor(bar)
        c.roundRect(x, y + h - 7, w, 7, radius, fill=1, stroke=0)
        c.rect(x, y + h - 7, w, 7, fill=1, stroke=0)


def draw_overview(path: Path):
    c = canvas.Canvas(str(path), pagesize=A4)
    c.setTitle("Ask Akshay — Free Sampler")
    c.setAuthor("Ask Akshay")

    # Header band.
    c.setFillColor(INK)
    c.rect(0, H - 82 * mm, W, 82 * mm, fill=1, stroke=0)
    c.setFillColor(BLUE)
    c.rect(0, H - 86 * mm, W, 4 * mm, fill=1, stroke=0)
    draw_para(c, "<b>ASK AKSHAY</b>  /  THE BOOKSHELF", M, H - 16 * mm, W - 2 * M, 10 * mm,
              style("kicker", fontSize=10, leading=12, textColor=WHITE, tracking=1.2))
    draw_para(c, "FREE SAMPLE", W - M - 92, H - 16 * mm, 92, 10 * mm,
              style("sample", fontSize=9, leading=11, textColor=WHITE, alignment=2))
    draw_para(c, "Two books for useful work.", M, H - 31 * mm, W - 2 * M, 18 * mm,
              style("hero", fontName="Helvetica-Bold", fontSize=25, leading=29, textColor=WHITE))
    draw_para(c, "A sampler from <i>The App Builder's Bluebook</i> and <i>The Roam Edit</i>.",
              M, H - 51 * mm, W - 2 * M, 16 * mm,
              style("subhero", fontSize=12, leading=16, textColor=colors.HexColor("#F3F0EA")))

    # Intro.
    y = H - 108 * mm
    draw_para(c, "A QUICK LOOK INSIDE", M, y, W - 2 * M, 9 * mm,
              style("section", fontName="Helvetica-Bold", fontSize=11, leading=13, textColor=INK))
    y -= 12 * mm
    bullets = [
        "Selected pages from two practical, visual learning books.",
        "One helps you build a useful app with discipline.",
        "The other helps you turn travel taste into a trusted brand.",
    ]
    for item in bullets:
        c.setFillColor(BLUE)
        c.circle(M + 3, y - 3, 3, fill=1, stroke=0)
        draw_para(c, item, M + 14, y + 2, W - 2 * M - 14, 9 * mm,
                  style("bullet", fontSize=10.5, leading=14, textColor=MUTED))
        y -= 10 * mm

    # Safe two-column cards. The long Bluebook title is a Paragraph in a fixed box.
    gap = 10 * mm
    card_w = (W - 2 * M - gap) / 2
    card_h = 73 * mm
    # Leave a deliberate gap after the bullet list so the cards never collide
    # with the last line even if a viewer uses a different PDF text renderer.
    card_y = H - 245 * mm
    rounded_card(c, M, card_y, card_w, card_h, WHITE, bar=BLUE)
    rounded_card(c, M + card_w + gap, card_y, card_w, card_h, WHITE, bar=OLIVE)
    inner = 9 * mm
    draw_para(c, "CAPSULE BITES", M + inner, card_y + card_h - 17 * mm, card_w - 2 * inner, 8 * mm,
              style("label1", fontName="Helvetica-Bold", fontSize=9, leading=11, textColor=MUTED))
    draw_para(c, "THE APP BUILDER'S BLUEBOOK", M + inner, card_y + card_h - 29 * mm,
              card_w - 2 * inner, 23 * mm,
              style("cardtitle1", fontName="Helvetica-Bold", fontSize=15.5, leading=18.5, textColor=INK))
    draw_para(c, "55 bite-sized capsules for turning a daily problem into a working app, a credible launch and a real business.",
              M + inner, card_y + 28 * mm, card_w - 2 * inner, 25 * mm,
              style("cardbody1", fontSize=10.5, leading=14, textColor=MUTED))

    x2 = M + card_w + gap
    draw_para(c, "THE PILL EDITION", x2 + inner, card_y + card_h - 17 * mm, card_w - 2 * inner, 8 * mm,
              style("label2", fontName="Helvetica-Bold", fontSize=9, leading=11, textColor=MUTED))
    draw_para(c, "THE ROAM EDIT", x2 + inner, card_y + card_h - 29 * mm,
              card_w - 2 * inner, 18 * mm,
              style("cardtitle2", fontName="Helvetica-Bold", fontSize=15.5, leading=18.5, textColor=INK))
    draw_para(c, "Seventeen digestible lessons for building a travel guide Instagram brand people trust and use.",
              x2 + inner, card_y + 28 * mm, card_w - 2 * inner, 25 * mm,
              style("cardbody2", fontSize=10.5, leading=14, textColor=MUTED))

    # Footer note.
    # Keep the footer wholly below the cards; the separator must never run
    # through card content even when fonts are substituted by a PDF viewer.
    footer_y = 20 * mm
    c.setStrokeColor(LINE)
    c.setLineWidth(0.8)
    c.line(M, footer_y + 22 * mm, W - M, footer_y + 22 * mm)
    draw_para(c, "WHAT YOU'LL SEE", M, footer_y + 17 * mm, W - 2 * M, 8 * mm,
              style("foothead", fontName="Helvetica-Bold", fontSize=10.5, leading=13, textColor=INK))
    draw_para(c, "Original title pages, a representative lesson, and a practical toolkit / diagram page from each book.",
              M, footer_y + 8 * mm, W - 2 * M, 10 * mm,
              style("footbody", fontSize=9.5, leading=12, textColor=MUTED))
    draw_para(c, "Keep the pages that make you want to build or go.", W - M - 205, footer_y - 2 * mm, 205, 10 * mm,
              style("aside", fontName="Helvetica-Oblique", fontSize=9.5, leading=12, textColor=MUTED, alignment=2))
    c.showPage()
    c.save()


def draw_cta(path: Path):
    c = canvas.Canvas(str(path), pagesize=A4)
    c.setTitle("Ask Akshay — Continue Reading")
    c.setAuthor("Ask Akshay")
    c.setFillColor(INK)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(BLUE)
    c.rect(M, H - 42 * mm, 44 * mm, 3 * mm, fill=1, stroke=0)
    draw_para(c, "END NOTE  /  SAMPLE EDITION", M, H - 28 * mm, W - 2 * M, 10 * mm,
              style("cta_kicker", fontName="Helvetica-Bold", fontSize=10, leading=12, textColor=WHITE))
    draw_para(c, "This is a sampler.", M, H - 61 * mm, W - 2 * M, 20 * mm,
              style("cta_title", fontName="Helvetica-Bold", fontSize=27, leading=31, textColor=WHITE))
    draw_para(c, "The full books go further, page by page.", M, H - 78 * mm, W - 2 * M, 14 * mm,
              style("cta_sub", fontSize=14, leading=18, textColor=colors.HexColor("#F3F0EA")))

    y = H - 117 * mm
    draw_para(c, "Inside this preview", M, y, W - 2 * M, 10 * mm,
              style("cta_head", fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=WHITE))
    y -= 13 * mm
    for item in [
        "selected pages from The App Builder's Bluebook",
        "selected pages from The Roam Edit — The Pill Edition",
        "a small taste of the frameworks, prompts and visual tools inside",
    ]:
        draw_para(c, "• " + item, M + 6, y, W - 2 * M - 6, 10 * mm,
                  style("cta_bullet", fontSize=11, leading=14, textColor=colors.HexColor("#DDD7CE")))
        y -= 11 * mm

    draw_para(c, "Find the complete editions at", M, 112 * mm, W - 2 * M, 12 * mm,
              style("cta_find", fontSize=11, leading=14, textColor=colors.HexColor("#DDD7CE")))
    # URL is deliberately boxed and wrapped as a Paragraph rather than a raw long string.
    c.setFillColor(colors.HexColor("#263F92"))
    c.roundRect(M, 87 * mm, 82 * mm, 16 * mm, 5, fill=1, stroke=0)
    draw_para(c, "<b><font color='#FFFFFF'>askakshay.com/store</font></b>", M + 5 * mm, 99 * mm,
              72 * mm, 10 * mm,
              style("cta_url", fontName="Helvetica-Bold", fontSize=14, leading=17, textColor=WHITE))
    draw_para(c, "Thanks for reading. Build something useful. Choose a better route.", M, 49 * mm, W - 2 * M, 12 * mm,
              style("cta_thanks", fontSize=10, leading=13, textColor=colors.HexColor("#DDD7CE")))
    draw_para(c, "askakshay.com/store", M, 20 * mm, W - 2 * M, 10 * mm,
              style("cta_footer", fontSize=9, leading=11, textColor=colors.HexColor("#9AAFFF")))
    c.showPage()
    c.save()


def scaled_source_page(source_page, target_w=W, target_h=H):
    page = copy.copy(source_page)
    sw = float(page.mediabox.width)
    sh = float(page.mediabox.height)
    scale = min(target_w / sw, target_h / sh)
    tx = (target_w - sw * scale) / 2
    ty = (target_h - sh * scale) / 2
    page.add_transformation(Transformation().scale(scale, scale).translate(tx / scale, ty / scale))
    page.mediabox.lower_left = (0, 0)
    page.mediabox.upper_right = (target_w, target_h)
    page.cropbox.lower_left = (0, 0)
    page.cropbox.upper_right = (target_w, target_h)
    return page


def build():
    BUILD.mkdir(exist_ok=True)
    draw_overview(OVERVIEW)
    draw_cta(CTA)
    blue = PdfReader(str(BLUEBOOK))
    roam = PdfReader(str(ROAM))
    overview = PdfReader(str(OVERVIEW))
    cta = PdfReader(str(CTA))

    writer = PdfWriter()
    writer.add_page(overview.pages[0])
    # Bluebook: cover, representative capsule, and toolkit plan.
    for index in (0, 5, 66):
        writer.add_page(scaled_source_page(blue.pages[index]))
    # Roam Edit: cover, representative pill opener, and diagram page.
    for index in (0, 6, 8):
        writer.add_page(scaled_source_page(roam.pages[index]))
    writer.add_page(cta.pages[0])
    with OUT.open("wb") as f:
        writer.write(f)
    shutil.rmtree(BUILD, ignore_errors=True)


if __name__ == "__main__":
    build()
