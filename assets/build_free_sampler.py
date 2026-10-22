from __future__ import annotations

import html
import shutil
from pathlib import Path
from typing import Any

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "askakshay-free-sampler-v2.pdf"
BUILD = ROOT / ".sampler-build"

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
M = 18 * mm
CONTENT_W = W - 2 * M

NAVY = colors.HexColor("#162333")
NAVY_2 = colors.HexColor("#20344A")
INK = colors.HexColor("#2B211A")
MUTED = colors.HexColor("#68757D")
PAPER = colors.HexColor("#F3F8FA")
WHITE = colors.white
BLUE = colors.HexColor("#4D9BC8")
BLUE_DARK = colors.HexColor("#275F83")
SKY = colors.HexColor("#DDECF3")
SKY_2 = colors.HexColor("#EAF4F8")
OLIVE = colors.HexColor("#39451F")
OLIVE_2 = colors.HexColor("#6B7A55")
OLIVE_LIGHT = colors.HexColor("#E4E9DE")
BROWN = colors.HexColor("#4D2A16")
WARM = colors.HexColor("#F4ECE5")
LILAC = colors.HexColor("#E7ECFA")
GREEN = colors.HexColor("#E6F1E9")
CORAL = colors.HexColor("#F07A51")
LINE = colors.HexColor("#BCD2DE")


def pstyle(name: str, **kwargs) -> ParagraphStyle:
    base = {
        "fontName": "Helvetica",
        "fontSize": 10,
        "leading": 13,
        "textColor": INK,
        "spaceAfter": 0,
        "spaceBefore": 0,
    }
    base.update(kwargs)
    return ParagraphStyle(name, **base)  # type: ignore[arg-type]


def fit_style(st: ParagraphStyle, scale: float) -> ParagraphStyle:
    size = max(6.8, st.fontSize * scale)
    return ParagraphStyle(
        f"{st.name}-{scale:.2f}",
        parent=st,
        fontSize=size,
        leading=max(size * 1.18, st.leading * scale),
    )


def draw_para(
    c: canvas.Canvas,
    text: str,
    x: float,
    y_top: float,
    width: float,
    max_height: float,
    st: ParagraphStyle,
    align: int | None = None,
) -> float:
    """Draw wrapped text inside a bounded box; never emit an unconstrained string."""
    if align is not None:
        st = ParagraphStyle(f"{st.name}-align", parent=st, alignment=align)
    for scale in (1.0, 0.94, 0.88, 0.82, 0.76, 0.70, 0.64):
        candidate = st if scale == 1.0 else fit_style(st, scale)
        para = Paragraph(text, candidate)
        _, height = para.wrap(width, max_height)
        if height <= max_height + 0.2:
            para.drawOn(c, x, y_top - height)
            return height
    para = Paragraph(text, fit_style(st, 0.60))
    _, height = para.wrap(width, max_height)
    para.drawOn(c, x, y_top - min(height, max_height))
    return min(height, max_height)


def safe(text: str) -> str:
    return html.escape(text, quote=False)


def rect(c: canvas.Canvas, x: float, y: float, w: float, h: float, fill, stroke=None, radius=0):
    c.setFillColor(fill)
    c.setStrokeColor(stroke or fill)
    c.setLineWidth(0.75)
    if radius:
        c.roundRect(x, y, w, h, radius, fill=1, stroke=1 if stroke else 0)
    else:
        c.rect(x, y, w, h, fill=1, stroke=1 if stroke else 0)


def line(c: canvas.Canvas, x1: float, y1: float, x2: float, y2: float, color=LINE, width=0.7):
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.line(x1, y1, x2, y2)


def circle(c: canvas.Canvas, x: float, y: float, r: float, fill, stroke=None, width=0.8):
    c.setFillColor(fill)
    c.setStrokeColor(stroke or fill)
    c.setLineWidth(width)
    c.circle(x, y, r, fill=1, stroke=1 if stroke else 0)


def label(c, text, x, y_top, width, color=BLUE, align=TA_LEFT, size=8.2):
    return draw_para(
        c,
        f"<b>{safe(text.upper())}</b>",
        x,
        y_top,
        width,
        10 * mm,
        pstyle("label", fontName="Helvetica-Bold", fontSize=size, leading=size + 2, textColor=color, alignment=align, charSpace=1.8),
    )


def title(c, text, x, y_top, width, max_h=24 * mm, color=INK, size=25.0, leading=28.0, font="Times-Bold"):
    return draw_para(
        c,
        text,
        x,
        y_top,
        width,
        max_h,
        pstyle("title", fontName=font, fontSize=size, leading=leading, textColor=color),
    )


def body(c, text, x, y_top, width, max_h, color=INK, size=10.2, leading=13.4, align=TA_LEFT):
    return draw_para(
        c,
        text,
        x,
        y_top,
        width,
        max_h,
        pstyle("body", fontSize=size, leading=leading, textColor=color, alignment=align),
    )


def footer(c: canvas.Canvas, page: int, dark=False, section="ASK AKSHAY / FREE SAMPLER"):
    color = colors.HexColor("#B9C9D2") if dark else colors.HexColor("#8BA3AE")
    line(c, M, 14 * mm, W - M, 14 * mm, color=color, width=0.6)
    body(c, section, M, 10.5 * mm, 75 * mm, 5 * mm, color=color, size=7.3, leading=8.5)
    body(c, f"{page:02d}", W - M - 12 * mm, 10.5 * mm, 12 * mm, 5 * mm, color=color, size=8, leading=9, align=TA_RIGHT)


def chip(c, text, x, y, w, h, fill, color=WHITE, stroke=None, size=8.2):
    rect(c, x, y, w, h, fill, stroke=stroke, radius=h / 2)
    body(c, text, x + 3 * mm, y + h - 3.2 * mm, w - 6 * mm, h - 4 * mm, color=color, size=size, leading=size + 1.5, align=TA_CENTER)


def numbered(c, number, text, x, y_top, width, color=BLUE, text_color=INK, size=10.2):
    circle(c, x + 4 * mm, y_top - 4 * mm, 4 * mm, color)
    body(c, str(number), x + 1.5 * mm, y_top - 1.8 * mm, 5 * mm, 5 * mm, color=WHITE, size=8.5, leading=9, align=TA_CENTER)
    return body(c, text, x + 12 * mm, y_top, width - 12 * mm, 12 * mm, color=text_color, size=size, leading=size * 1.35)


def card(c, x, y, w, h, fill=WHITE, stroke=LINE, radius=5, top_bar=None):
    rect(c, x, y, w, h, fill, stroke=stroke, radius=radius)
    if top_bar:
        rect(c, x, y + h - 2.2 * mm, w, 2.2 * mm, top_bar, stroke=None)


def section_head(c, kicker, heading, x=M, y_top=H - 22 * mm, width=CONTENT_W, color=INK, accent=BLUE):
    label(c, kicker, x, y_top, width, color=accent)
    y = y_top - 10 * mm
    h = title(c, heading, x, y, width, 25 * mm, color=color, size=25, leading=28)
    line(c, x, y - h - 4 * mm, x + 42 * mm, y - h - 4 * mm, color=accent, width=1.8)
    return y - h - 9 * mm


def draw_cover(c: canvas.Canvas):
    rect(c, 0, 0, W, H, NAVY)
    rect(c, 0, H - 5 * mm, W, 5 * mm, CORAL)
    # Fine editorial grid.
    for i in range(1, 8):
        line(c, M + i * 22 * mm, 22 * mm, M + i * 22 * mm, H - 22 * mm, NAVY_2, 0.35)
    label(c, "ASK AKSHAY / THE BOOKSHELF", M, H - 18 * mm, 95 * mm, color=WHITE, size=8.8)
    label(c, "FREE EDITORIAL SAMPLER", W - M - 60 * mm, H - 18 * mm, 60 * mm, color=CORAL, align=TA_RIGHT, size=7.8)
    title(c, "Useful work.\nBetter judgement.", M, H - 38 * mm, CONTENT_W, 34 * mm, color=WHITE, size=31, leading=33)
    body(c, "Two practical books, one shared operating system: choose a real problem, make the next decision easier, and keep the evidence visible.", M, H - 76 * mm, 118 * mm, 24 * mm, color=colors.HexColor("#DDE9EF"), size=12.4, leading=16.2)
    line(c, M, H - 108 * mm, W - M, H - 108 * mm, CORAL, 1.5)

    panel_y = 49 * mm
    panel_h = 94 * mm
    gap = 8 * mm
    pw = (CONTENT_W - gap) / 2
    card(c, M, panel_y, pw, panel_h, fill=colors.HexColor("#1E4260"), stroke=BLUE, radius=6, top_bar=BLUE)
    card(c, M + pw + gap, panel_y, pw, panel_h, fill=colors.HexColor("#3C4928"), stroke=OLIVE_2, radius=6, top_bar=OLIVE_2)
    label(c, "01 / BUILD", M + 8 * mm, panel_y + panel_h - 13 * mm, pw - 16 * mm, color=colors.HexColor("#B9E2F4"), size=8.4)
    title(c, "The App\nBuilder's Bluebook", M + 8 * mm, panel_y + panel_h - 25 * mm, pw - 16 * mm, 26 * mm, color=WHITE, size=18, leading=19.5)
    body(c, "55 capsules for turning a recurring problem into a useful app, a credible launch and an operable business.", M + 8 * mm, panel_y + 46 * mm, pw - 16 * mm, 19 * mm, color=colors.HexColor("#D9EDF5"), size=9.8, leading=12.2)
    for i, t in enumerate(("DISCOVER", "DELIVER", "TRUST", "REACH", "SURVIVE")):
        chip(c, t, M + 8 * mm + (i % 3) * 25 * mm, panel_y + 18 * mm - (i // 3) * 10 * mm, 22 * mm, 6.5 * mm, fill=NAVY_2, color=colors.HexColor("#B9E2F4"), stroke=BLUE, size=6.5)

    x2 = M + pw + gap
    label(c, "02 / ROAM", x2 + 8 * mm, panel_y + panel_h - 13 * mm, pw - 16 * mm, color=colors.HexColor("#D7E2B5"), size=8.4)
    title(c, "The Roam\nEdit", x2 + 8 * mm, panel_y + panel_h - 25 * mm, pw - 16 * mm, 26 * mm, color=WHITE, size=22, leading=23)
    body(c, "17 pills for turning travel taste into useful content, a loyal audience and a real business.", x2 + 8 * mm, panel_y + 46 * mm, pw - 16 * mm, 19 * mm, color=colors.HexColor("#E4EAD7"), size=9.8, leading=12.2)
    # Route / pill motif.
    line(c, x2 + 12 * mm, panel_y + 19 * mm, x2 + pw - 12 * mm, panel_y + 19 * mm, OLIVE_2, 1.5)
    for i in range(5):
        circle(c, x2 + 15 * mm + i * 15 * mm, panel_y + 19 * mm, 3.2 * mm, fill=OLIVE_LIGHT, stroke=OLIVE_2, width=0.8)
    body(c, "INSPIRE  ->  TRUST  ->  GUIDE  ->  SELL", x2 + 8 * mm, panel_y + 9 * mm, pw - 16 * mm, 6 * mm, color=colors.HexColor("#D7E2B5"), size=7, leading=8, align=TA_CENTER)

    body(c, "A 10-page preview of the ideas, diagrams and actions inside.", M, 31 * mm, 110 * mm, 7 * mm, color=colors.HexColor("#B9C9D2"), size=8.4, leading=10)
    body(c, "askakshay.com/store", W - M - 48 * mm, 31 * mm, 48 * mm, 7 * mm, color=CORAL, size=8.4, leading=10, align=TA_RIGHT)
    footer(c, 1, dark=True, section="ASK AKSHAY / BOOKS THAT MOVE")


def draw_how_to_read(c: canvas.Canvas):
    rect(c, 0, 0, W, H, PAPER)
    y = section_head(c, "HOW TO READ THIS SAMPLER", "Read for the move, not the mood", color=INK, accent=BLUE)
    body(c, "Each book is built as a sequence of small decisions. The sampler keeps that rhythm: orient yourself, see the framework, then try one action before you move on.", M, y, CONTENT_W, 18 * mm, color=MUTED, size=11.2, leading=15)

    y -= 23 * mm
    gap = 6 * mm
    cw = (CONTENT_W - 2 * gap) / 3
    cards = [
        ("01 / SCAN", "Find the promise", "Read the one-line thesis and the diagram. If you can repeat the idea, it is doing its job.", BLUE, SKY),
        ("02 / READ", "Notice the sequence", "Look for the order: problem -> evidence -> action. The order is the lesson, not decoration.", BLUE_DARK, WHITE),
        ("03 / APPLY", "Do one useful thing", "Write the sentence, score the idea, or draft the first card. A small action turns a sample into a signal.", CORAL, WARM),
    ]
    for i, (k, h, t, accent, fill) in enumerate(cards):
        x = M + i * (cw + gap)
        card(c, x, y - 42 * mm, cw, 42 * mm, fill=fill, stroke=LINE, radius=5, top_bar=accent)
        label(c, k, x + 6 * mm, y - 7 * mm, cw - 12 * mm, color=accent, size=7.6)
        title(c, h, x + 6 * mm, y - 16 * mm, cw - 12 * mm, 12 * mm, color=INK, size=14, leading=15.5)
        body(c, t, x + 6 * mm, y - 29 * mm, cw - 12 * mm, 12 * mm, color=MUTED, size=8.6, leading=11)

    y -= 54 * mm
    label(c, "THE ANATOMY OF A GOOD PAGE", M, y, CONTENT_W, color=BLUE)
    line(c, M, y - 5 * mm, W - M, y - 5 * mm, LINE)
    band_y = y - 43 * mm
    bw = (CONTENT_W - 3 * gap) / 4
    anatomy = [
        ("BITE", "One sentence worth carrying."),
        ("FRAMEWORK", "A model that makes the choice visible."),
        ("EXAMPLE", "A believable situation, not a slogan."),
        ("ACTION", "A 15-minute move you can finish today."),
    ]
    for i, (k, t) in enumerate(anatomy):
        x = M + i * (bw + gap)
        card(c, x, band_y, bw, 31 * mm, fill=WHITE, stroke=LINE, radius=4, top_bar=BLUE if i < 2 else OLIVE_2)
        label(c, k, x + 5 * mm, band_y + 23 * mm, bw - 10 * mm, color=BLUE if i < 2 else OLIVE_2, size=7.2)
        body(c, t, x + 5 * mm, band_y + 14 * mm, bw - 10 * mm, 11 * mm, color=INK, size=8.8, leading=11.2)

    strip_y = 44 * mm
    rect(c, M, strip_y, CONTENT_W, 27 * mm, fill=NAVY, stroke=None, radius=5)
    label(c, "THE ONLY RULE", M + 8 * mm, strip_y + 20 * mm, 45 * mm, color=CORAL, size=7.8)
    body(c, "Read one idea. Do the smallest version. Measure what changed. Then decide whether it deserves another page.", M + 8 * mm, strip_y + 13 * mm, CONTENT_W - 16 * mm, 10 * mm, color=WHITE, size=13, leading=16)
    footer(c, 2, section="HOW TO READ / SCAN -> READ -> APPLY")


def draw_bluebook_overview(c: canvas.Canvas):
    rect(c, 0, 0, W, H, PAPER)
    y = section_head(c, "THE APP BUILDER'S BLUEBOOK", "A field manual for owning the result", color=INK, accent=BLUE)
    body(c, "The Bluebook is not a coding course. It is an ownership course for people who want to use AI, Claude Code or Codex without outsourcing judgement.", M, y, CONTENT_W, 18 * mm, color=MUTED, size=11.2, leading=15)

    y -= 25 * mm
    # Left timeline.
    left_w = 92 * mm
    label(c, "THE SIX-LEVEL JOURNEY", M, y, left_w, color=BLUE)
    line(c, M + 8 * mm, y - 13 * mm, M + 8 * mm, y - 92 * mm, BLUE, 1.2)
    levels = [
        ("I", "Foundation", "Think like a builder"),
        ("II", "Validate", "Prove, then shape"),
        ("III", "Build", "Ship with AI"),
        ("IV", "Protect", "Data, AI, security"),
        ("V", "Launch", "Users and revenue"),
        ("VI", "Operate", "Run like an owner"),
    ]
    for i, (num, name, desc) in enumerate(levels):
        yy = y - 16 * mm - i * 14 * mm
        circle(c, M + 8 * mm, yy, 4.8 * mm, fill=BLUE if i < 3 else BLUE_DARK)
        body(c, num, M + 5.1 * mm, yy + 2.1 * mm, 5.8 * mm, 5 * mm, color=WHITE, size=7.5, leading=8, align=TA_CENTER)
        body(c, f"<b>{name}</b><br/><font color='#68757D'>{desc}</font>", M + 17 * mm, yy + 5 * mm, left_w - 20 * mm, 12 * mm, color=INK, size=9.1, leading=11.2)

    # Right editorial notes.
    rx = M + 105 * mm
    rw = W - M - rx
    label(c, "THE EDITORIAL PROMISE", rx, y, rw, color=CORAL)
    card(c, rx, y - 41 * mm, rw, 35 * mm, fill=BROWN, stroke=BROWN, radius=5, top_bar=CORAL)
    body(c, "A useful app is a repeatable promise delivered to a reachable group of people.", rx + 6 * mm, y - 14 * mm, rw - 12 * mm, 15 * mm, color=WHITE, size=13.2, leading=16)
    label(c, "WHAT CHANGES AFTER READING", rx, y - 50 * mm, rw, color=BLUE)
    notes = [
        ("You stop", "starting with features and start with a painful, reachable workflow."),
        ("You start", "climbing evidence before you build the polished version."),
        ("You keep", "the human in charge of trust, money, privacy and scope."),
    ]
    yy = y - 61 * mm
    for i, (head, text) in enumerate(notes):
        card(c, rx, yy - 18 * mm, rw, 16 * mm, fill=WHITE if i != 1 else SKY, stroke=LINE, radius=4, top_bar=BLUE if i != 2 else OLIVE_2)
        body(c, f"<b>{head}</b> {text}", rx + 5 * mm, yy - 6 * mm, rw - 10 * mm, 9 * mm, color=INK, size=8.7, leading=11)
        yy -= 20 * mm

    # Bottom row: operating stance.
    bottom_y = 40 * mm
    label(c, "THE SHARED STANCE", M, bottom_y + 27 * mm, CONTENT_W, color=BLUE)
    stance = [
        ("Evidence", "Compliments are a start. Repeat behaviour is stronger."),
        ("Control", "AI drafts; the owner approves the consequences."),
        ("Smallness", "A complete narrow slice beats a broad unfinished app."),
    ]
    gap = 5 * mm
    sw = (CONTENT_W - 2 * gap) / 3
    for i, (h, t) in enumerate(stance):
        x = M + i * (sw + gap)
        card(c, x, bottom_y, sw, 21 * mm, fill=WHITE, stroke=LINE, radius=4, top_bar=CORAL if i == 0 else BLUE)
        body(c, f"<b>{h}</b><br/><font color='#68757D'>{t}</font>", x + 5 * mm, bottom_y + 15 * mm, sw - 10 * mm, 12 * mm, color=INK, size=8.6, leading=10.8)
    footer(c, 3, section="BLUEBOOK / EDITORIAL OVERVIEW")


def draw_bluebook_framework(c: canvas.Canvas):
    rect(c, 0, 0, W, H, SKY_2)
    y = section_head(c, "BLUEBOOK VISUAL FRAMEWORK", "Five jobs. One evidence-led build loop.", color=INK, accent=BLUE)
    body(c, "The Bluebook keeps the builder honest by asking two questions: which job is weakest, and what evidence would move it one rung higher?", M, y, CONTENT_W, 17 * mm, color=MUTED, size=10.8, leading=14.2)

    y -= 23 * mm
    label(c, "THE FIVE JOBS EVERY APP MUST DO", M, y, CONTENT_W, color=BLUE)
    gap = 3.5 * mm
    jw = (CONTENT_W - 4 * gap) / 5
    jobs = [
        ("01", "Discover", "Is this a real problem?"),
        ("02", "Deliver", "Does the result help?"),
        ("03", "Trust", "Can people rely on it?"),
        ("04", "Reach", "Can the right people find it?"),
        ("05", "Survive", "Can you operate it?"),
    ]
    for i, (n, h, t) in enumerate(jobs):
        x = M + i * (jw + gap)
        card(c, x, y - 31 * mm, jw, 25 * mm, fill=BROWN if i in (1, 4) else WHITE, stroke=BLUE, radius=4, top_bar=BLUE)
        label(c, n, x + 4 * mm, y - 8 * mm, jw - 8 * mm, color=CORAL if i in (1, 4) else BLUE, size=7)
        body(c, f"<b>{h}</b><br/><font color='{ '#F5EEE8' if i in (1,4) else '#68757D'}'>{t}</font>", x + 4 * mm, y - 15 * mm, jw - 8 * mm, 10 * mm, color=WHITE if i in (1, 4) else INK, size=8.2, leading=10.2)

    mid_y = y - 45 * mm
    left_w = 82 * mm
    right_x = M + 95 * mm
    right_w = W - M - right_x
    label(c, "THE EVIDENCE LADDER", M, mid_y, left_w, color=BLUE)
    ladder = [
        ("01", "Idea", "in your head"),
        ("02", "Conversation", "recent problem"),
        ("03", "Manual result", "they try it"),
        ("04", "Behaviour", "they share data"),
        ("05", "Return", "without chasing"),
        ("06", "Commitment", "pay, refer, ask"),
    ]
    ly = mid_y - 11 * mm
    for i, (n, h, t) in enumerate(ladder):
        yy = ly - i * 11 * mm
        fill = WHITE if i < 3 else (SKY if i == 3 else GREEN)
        card(c, M, yy - 7.5 * mm, left_w, 8.5 * mm, fill=fill, stroke=LINE, radius=3, top_bar=BLUE if i < 4 else OLIVE_2)
        body(c, f"<b>{n}</b>  {h}  <font color='#68757D'>{t}</font>", M + 4 * mm, yy - 2.6 * mm, left_w - 8 * mm, 5.5 * mm, color=INK, size=7.8, leading=9)
        if i < len(ladder) - 1:
            line(c, M + left_w / 2, yy - 8 * mm, M + left_w / 2, yy - 10 * mm, BLUE, 0.7)
    body(c, "STRONGER EVIDENCE ->", M, 51 * mm, left_w, 6 * mm, color=BLUE_DARK, size=7.2, leading=8, align=TA_RIGHT)

    label(c, "THE BUILD LOOP", right_x, mid_y, right_w, color=CORAL)
    loop_y = mid_y - 13 * mm
    steps = [
        ("Inspect", "see the current state"),
        ("Plan", "name scope and risk"),
        ("Change", "edit one narrow part"),
        ("Verify", "run the smallest proof"),
        ("Review", "read the diff"),
        ("Record", "update the memory"),
    ]
    bw = (right_w - 4 * gap) / 3
    for i, (h, t) in enumerate(steps):
        row, col = divmod(i, 3)
        x = right_x + col * (bw + gap)
        yy = loop_y - row * 27 * mm
        card(c, x, yy - 20 * mm, bw, 20 * mm, fill=WHITE if i not in (2, 5) else BROWN, stroke=BLUE, radius=4, top_bar=CORAL if i in (2, 5) else BLUE)
        body(c, f"<b>{h}</b><br/><font color='{ '#F4ECE5' if i in (2,5) else '#68757D'}'>{t}</font>", x + 4 * mm, yy - 7 * mm, bw - 8 * mm, 12 * mm, color=WHITE if i in (2, 5) else INK, size=8.4, leading=10.4)
    body(c, "The loop is the product owner's quality system.", right_x, 55 * mm, right_w, 8 * mm, color=BLUE_DARK, size=9.2, leading=11, align=TA_CENTER)
    rect(c, M, 28 * mm, CONTENT_W, 16 * mm, fill=NAVY, stroke=None, radius=4)
    body(c, "When every job is not equal, the weakest job becomes the next piece of work — not another feature.", M + 6 * mm, 38 * mm, CONTENT_W - 12 * mm, 8 * mm, color=WHITE, size=10.5, leading=13, align=TA_CENTER)
    footer(c, 4, section="BLUEBOOK / FIVE JOBS + EVIDENCE + LOOP")


def draw_bluebook_lesson(c: canvas.Canvas):
    rect(c, 0, 0, W, H, PAPER)
    y = section_head(c, "BLUEBOOK / ORIGINAL LESSON", "Build the smallest credible slice", color=INK, accent=BLUE)
    label(c, "CAPSULE 15 / BUILD WITH EVIDENCE", M, y, CONTENT_W, color=BLUE_DARK, size=7.8)
    y -= 10 * mm
    card(c, M, y - 25 * mm, CONTENT_W, 22 * mm, fill=BROWN, stroke=BROWN, radius=5, top_bar=BLUE)
    label(c, "THE BITE", M + 7 * mm, y - 8 * mm, 35 * mm, color=colors.HexColor("#B9E2F4"), size=7.8)
    body(c, "One complete outcome through the whole system beats ten disconnected screens.", M + 7 * mm, y - 14 * mm, CONTENT_W - 14 * mm, 10 * mm, color=WHITE, size=13.4, leading=16)

    y -= 34 * mm
    left_w = 83 * mm
    right_x = M + 93 * mm
    right_w = W - M - right_x
    label(c, "WHY IT MATTERS", M, y, left_w, color=BLUE)
    body(c, "A vertical slice is the smallest path from a real trigger to a real next action. It exposes whether the interface, rules, storage and promise agree before you spend time on the rest of the product.", M, y - 8 * mm, left_w, 32 * mm, color=INK, size=9.6, leading=12.4)
    label(c, "THE MICRO-BRIEF", right_x, y, right_w, color=CORAL)
    card(c, right_x, y - 43 * mm, right_w, 37 * mm, fill=WHITE, stroke=LINE, radius=4, top_bar=CORAL)
    body(c, "<b>Trigger</b> morning starts<br/><b>Input</b> scattered tasks<br/><b>Process</b> rank by urgency, impact and effort<br/><b>Output</b> editable order + reason<br/><b>Next</b> start the first task", right_x + 5 * mm, y - 12 * mm, right_w - 10 * mm, 27 * mm, color=INK, size=8.2, leading=10.3)

    y -= 52 * mm
    label(c, "DO THIS TODAY", M, y, CONTENT_W, color=BLUE)
    line(c, M, y - 5 * mm, W - M, y - 5 * mm, LINE)
    steps = [
        "Write the user outcome as four to six verbs from trigger to next action.",
        "List only the fields and states this path needs: empty, loading, success and error.",
        "Build the thin end-to-end version, then let one real person use it without coaching.",
    ]
    sy = y - 12 * mm
    for i, text in enumerate(steps, 1):
        numbered(c, i, text, M, sy, CONTENT_W, color=BLUE, size=9.7)
        sy -= 13 * mm

    by = 43 * mm
    gap = 5 * mm
    bw = (CONTENT_W - gap) / 2
    boxes = [
        ("DAYFLOW IN ACTION", "The first DayFlow slice is: add task -> save task -> show reason -> mark complete. No login, calendar or AI chat yet.", WARM, CORAL),
        ("TRAP TO AVOID", "Building every page's layout first, then discovering that the data does not connect.", LILAC, BLUE_DARK),
        ("DONE WHEN", "A stranger can complete the path and you can point to the evidence that the result helped.", GREEN, OLIVE_2),
        ("LEVEL UP", "Name each slice after the user outcome, not the feature: 'Get today's plan' beats 'Task module'.", BROWN, CORAL),
    ]
    for i, (h, text, fill, accent) in enumerate(boxes):
        row, col = divmod(i, 2)
        x = M + col * (bw + gap)
        yy = by + (1 - row) * 24 * mm
        card(c, x, yy, bw, 20 * mm, fill=fill, stroke=fill if fill in (BROWN,) else LINE, radius=4, top_bar=accent)
        label(c, h, x + 5 * mm, yy + 15 * mm, bw - 10 * mm, color=accent if fill != BROWN else CORAL, size=7.2)
        body(c, text, x + 5 * mm, yy + 10 * mm, bw - 10 * mm, 11 * mm, color=WHITE if fill == BROWN else INK, size=8.2, leading=10.4)
    footer(c, 5, section="BLUEBOOK / ORIGINAL CAPSULE")


def draw_roam_overview(c: canvas.Canvas):
    rect(c, 0, 0, W, H, OLIVE)
    rect(c, 0, H - 5 * mm, W, 5 * mm, BLUE)
    label(c, "THE ROAM EDIT / PILL EDITION", M, H - 19 * mm, CONTENT_W, color=colors.HexColor("#D7E2B5"), size=8.8)
    title(c, "Beautiful places.\nBetter routes.\nNo wasted days.", M, H - 38 * mm, CONTENT_W, 46 * mm, color=WHITE, size=30, leading=32)
    body(c, "A practical editorial system for turning travel taste into useful content, a loyal audience and a real business.", M, H - 93 * mm, 112 * mm, 22 * mm, color=colors.HexColor("#E4EAD7"), size=12, leading=15.5)
    # Pill motif.
    circle(c, W - 43 * mm, H - 73 * mm, 17 * mm, fill=colors.HexColor("#46552A"), stroke=OLIVE_2, width=1)
    line(c, W - 53 * mm, H - 73 * mm, W - 31 * mm, H - 73 * mm, BLUE, 2.4)
    circle(c, W - 53 * mm, H - 73 * mm, 5 * mm, fill=BLUE, stroke=WHITE, width=0.8)
    circle(c, W - 31 * mm, H - 73 * mm, 5 * mm, fill=WHITE, stroke=BLUE, width=0.8)
    body(c, "17 pills / 5 templates / 30-day launch / 90-day rhythm", M, H - 115 * mm, CONTENT_W, 8 * mm, color=colors.HexColor("#D7E2B5"), size=8.3, leading=10, align=TA_CENTER)

    y = H - 136 * mm
    rect(c, M, y - 66 * mm, CONTENT_W, 62 * mm, fill=PAPER, stroke=None, radius=6)
    label(c, "THE EDITORIAL PROMISE", M + 8 * mm, y - 12 * mm, CONTENT_W - 16 * mm, color=BLUE)
    body(c, "People do not need another beautiful feed. They need a point of view that reduces uncertainty: where to stay, what to skip, what to book and why it is worth the time.", M + 8 * mm, y - 21 * mm, CONTENT_W - 16 * mm, 17 * mm, color=INK, size=11, leading=14.3)
    gap = 5 * mm
    cw = (CONTENT_W - 2 * gap - 16 * mm) / 3
    for i, (h, t) in enumerate([
        ("INSPIRATION", "I want to go there."),
        ("UTILITY", "I know what to do."),
        ("COMMERCE", "I will pay for more help."),
    ]):
        x = M + 8 * mm + i * (cw + gap)
        card(c, x, y - 58 * mm, cw, 24 * mm, fill=OLIVE_LIGHT if i != 1 else SKY, stroke=LINE, radius=4, top_bar=OLIVE_2 if i != 1 else BLUE)
        body(c, f"<b>{h}</b><br/><font color='#68757D'>{t}</font>", x + 4 * mm, y - 44 * mm, cw - 8 * mm, 13 * mm, color=INK, size=8.5, leading=10.5, align=TA_CENTER)

    body(c, "The book's job is not to make you post more. It is to make every post feel more like a decision.", M, 42 * mm, CONTENT_W, 10 * mm, color=colors.HexColor("#E4EAD7"), size=10.2, leading=13, align=TA_CENTER)
    footer(c, 6, dark=True, section="ROAM / EDITORIAL OVERVIEW")


def draw_roam_framework(c: canvas.Canvas):
    rect(c, 0, 0, W, H, PAPER)
    y = section_head(c, "ROAM VISUAL FRAMEWORK", "Make the point of view visible", color=INK, accent=BLUE)
    body(c, "The Roam Edit turns taste into a repeatable editorial machine: choose who you help, promise how you help, then guide one decision at a time.", M, y, CONTENT_W, 17 * mm, color=MUTED, size=10.8, leading=14.2)

    y -= 23 * mm
    left_w = 78 * mm
    right_x = M + 91 * mm
    right_w = W - M - right_x
    label(c, "THE NICHE TRIANGLE", M, y, left_w, color=BLUE)
    card(c, M, y - 61 * mm, left_w, 55 * mm, fill=WHITE, stroke=LINE, radius=5)
    cx = M + left_w / 2
    cy = y - 34 * mm
    # Triangle and three labelled nodes.
    pts = [(cx, cy + 17 * mm), (M + 14 * mm, cy - 13 * mm), (M + left_w - 14 * mm, cy - 13 * mm)]
    line(c, pts[0][0], pts[0][1], pts[1][0], pts[1][1], BLUE, 1.2)
    line(c, pts[1][0], pts[1][1], pts[2][0], pts[2][1], BLUE, 1.2)
    line(c, pts[2][0], pts[2][1], pts[0][0], pts[0][1], BLUE, 1.2)
    for px, py in pts:
        circle(c, px, py, 5.5 * mm, fill=OLIVE, stroke=BLUE, width=1)
    body(c, "TRAVELLER", cx - 19 * mm, cy + 31 * mm, 38 * mm, 5 * mm, color=BLUE_DARK, size=6.3, leading=7.2, align=TA_CENTER)
    body(c, "busy couples", cx - 19 * mm, cy + 26 * mm, 38 * mm, 5 * mm, color=MUTED, size=6.4, leading=7.2, align=TA_CENTER)
    body(c, "PROBLEM", M + 4 * mm, cy - 20 * mm, 33 * mm, 5 * mm, color=BLUE_DARK, size=7.1, leading=8, align=TA_CENTER)
    body(c, "too many tabs", M + 4 * mm, cy - 25 * mm, 33 * mm, 5 * mm, color=MUTED, size=6.8, leading=7.5, align=TA_CENTER)
    body(c, "EDITORIAL LENS", M + left_w - 37 * mm, cy - 20 * mm, 33 * mm, 5 * mm, color=BLUE_DARK, size=7.1, leading=8, align=TA_CENTER)
    body(c, "beautiful efficiency", M + left_w - 37 * mm, cy - 25 * mm, 33 * mm, 5 * mm, color=MUTED, size=6.8, leading=7.5, align=TA_CENTER)
    body(c, "A niche is where all three corners meet.", M + 7 * mm, y - 56 * mm, left_w - 14 * mm, 6 * mm, color=MUTED, size=7.5, leading=9, align=TA_CENTER)

    label(c, "THE CONTENT LADDER", right_x, y, right_w, color=CORAL)
    ladder = [
        ("04", "Commerce", "I will pay for more help.", OLIVE),
        ("03", "Utility", "This tells me exactly what to do.", OLIVE_2),
        ("02", "Trust", "This account gets my taste.", BLUE_DARK),
        ("01", "Inspiration", "I want to go there.", BLUE),
    ]
    for i, (n, h, t, fill) in enumerate(ladder):
        yy = y - 16 * mm - i * 13 * mm
        ww = right_w - (i * 8 * mm)
        xx = right_x + (i * 4 * mm)
        card(c, xx, yy - 10 * mm, ww, 10 * mm, fill=fill, stroke=fill, radius=3)
        body(c, f"<b>{n}  {h}</b>  <font color='#F3F8FA'>{t}</font>", xx + 4 * mm, yy - 3.2 * mm, ww - 8 * mm, 5.5 * mm, color=WHITE, size=7.6, leading=8.8)
    body(c, "Build upward: beauty earns attention; decisions earn saves; trust makes selling possible.", right_x, y - 69 * mm, right_w, 10 * mm, color=MUTED, size=8.3, leading=10.5)

    bottom_y = 46 * mm
    label(c, "THE NINE-SWIPE CAROUSEL PATH", M, bottom_y + 38 * mm, CONTENT_W, color=BLUE)
    path = ["Promise", "Problem", "Principle", "Plan", "Plan", "Plan", "Caveat", "Summary", "CTA"]
    gap = 2.2 * mm
    pw = (CONTENT_W - 8 * gap) / 9
    for i, t in enumerate(path):
        x = M + i * (pw + gap)
        fill = BLUE if i == 0 else (OLIVE if i == 8 else WHITE)
        stroke = BLUE if i < 3 else (OLIVE_2 if i == 8 else LINE)
        card(c, x, bottom_y, pw, 25 * mm, fill=fill, stroke=stroke, radius=3, top_bar=stroke)
        body(c, f"<b>{i+1}</b><br/><font color='{ '#F3F8FA' if i in (0,8) else '#2B211A'}'>{t}</font>", x + 1.5 * mm, bottom_y + 18 * mm, pw - 3 * mm, 13 * mm, color=WHITE if i in (0, 8) else INK, size=7.2, leading=8.8, align=TA_CENTER)
    body(c, "STOP -> GUIDE -> HAND OVER THE PLAN", M, 38 * mm, CONTENT_W, 6 * mm, color=BLUE_DARK, size=7.6, leading=9, align=TA_CENTER)
    footer(c, 7, section="ROAM / NICHE + LADDER + CAROUSEL")


def draw_roam_lesson(c: canvas.Canvas):
    rect(c, 0, 0, W, H, PAPER)
    y = section_head(c, "ROAM / ORIGINAL LESSON", "Make the carousel do one job", color=INK, accent=BLUE)
    label(c, "PILL 05 / BUILD THE CONTENT MACHINE", M, y, CONTENT_W, color=BLUE_DARK, size=7.8)
    y -= 10 * mm
    card(c, M, y - 25 * mm, CONTENT_W, 22 * mm, fill=OLIVE, stroke=OLIVE, radius=5, top_bar=BLUE)
    label(c, "THE 10-SECOND DOSE", M + 7 * mm, y - 8 * mm, 48 * mm, color=colors.HexColor("#D7E2B5"), size=7.8)
    body(c, "A carousel is not a slideshow. It walks one traveller from a problem to a plan in nine swipes.", M + 7 * mm, y - 14 * mm, CONTENT_W - 14 * mm, 10 * mm, color=WHITE, size=13.2, leading=16)

    y -= 35 * mm
    left_w = 85 * mm
    right_x = M + 95 * mm
    right_w = W - M - right_x
    label(c, "THE COVER FORMULA", M, y, left_w, color=BLUE)
    card(c, M, y - 37 * mm, left_w, 31 * mm, fill=WHITE, stroke=LINE, radius=4, top_bar=BLUE)
    body(c, "<b>PERSON</b><br/>who is this for?<br/><br/><b>PAIN</b><br/>what friction are they feeling?<br/><br/><b>PROMISE</b><br/>what will feel easier after the swipe?", M + 6 * mm, y - 11 * mm, left_w - 12 * mm, 24 * mm, color=INK, size=8.6, leading=10.2)
    label(c, "THE TWO-SECOND TEST", right_x, y, right_w, color=CORAL)
    card(c, right_x, y - 37 * mm, right_w, 31 * mm, fill=WARM, stroke=CORAL, radius=4, top_bar=CORAL)
    body(c, "Show only the cover. Ask: can a stranger name the traveller, the problem and the promised decision? If not, rewrite the cover before you design slide two.", right_x + 6 * mm, y - 11 * mm, right_w - 12 * mm, 22 * mm, color=INK, size=9.1, leading=11.5)

    y -= 47 * mm
    label(c, "THE NINE-SWIPE DRAFT", M, y, CONTENT_W, color=BLUE)
    line(c, M, y - 5 * mm, W - M, y - 5 * mm, LINE)
    gap = 2.2 * mm
    items = [
        ("1", "Promise", "A calm Lisbon weekend"),
        ("2", "Problem", "Too many bases, too little time"),
        ("3", "Principle", "One base, then walk outward"),
        ("4-6", "Plan", "Route, timing, trade-off"),
        ("7", "Caveat", "Not for travellers who want nightlife"),
        ("8", "Summary", "Saveable three-line route"),
        ("9", "CTA", "Save or send to your partner"),
    ]
    row_y = y - 15 * mm
    col_w = (CONTENT_W - 4 * gap) / 5
    for i, (n, h, t) in enumerate(items):
        row, col = divmod(i, 5)
        x = M + col * (col_w + gap)
        yy = row_y - row * 22 * mm
        card(c, x, yy - 16 * mm, col_w, 16 * mm, fill=OLIVE if i == 0 else (OLIVE_LIGHT if i in (5, 6) else WHITE), stroke=OLIVE_2 if i in (5, 6) else LINE, radius=3, top_bar=BLUE if i == 0 else OLIVE_2)
        body(c, f"<b>{n}</b>  {h}<br/><font color='{ '#E4EAD7' if i == 0 else '#68757D'}'>{t}</font>", x + 3 * mm, yy - 5 * mm, col_w - 6 * mm, 10 * mm, color=WHITE if i == 0 else INK, size=7.5, leading=9.2, align=TA_CENTER)

    by = 49 * mm
    rect(c, M, by, CONTENT_W, 36 * mm, fill=SKY, stroke=LINE, radius=5)
    label(c, "DO IT TODAY / 15 MINUTES", M + 7 * mm, by + 29 * mm, 65 * mm, color=BLUE_DARK, size=7.5)
    numbered(c, 1, "Choose one traveller and one decision.", M + 7 * mm, by + 20 * mm, 78 * mm, color=BLUE_DARK, size=8.8)
    numbered(c, 2, "Write the cover in one sentence.", M + 87 * mm, by + 20 * mm, 78 * mm, color=BLUE_DARK, size=8.8)
    numbered(c, 3, "Cut every slide that does not move the decision forward.", M + 7 * mm, by + 12 * mm, 150 * mm, color=BLUE_DARK, size=8.8)
    footer(c, 8, section="ROAM / ORIGINAL PILL")


def draw_comparison(c: canvas.Canvas):
    rect(c, 0, 0, W, H, PAPER)
    y = section_head(c, "PRACTICAL COMPARISON", "Two books. Two starting points. One operating system.", color=INK, accent=CORAL)
    body(c, "Choose the book that matches the work in front of you. The shared principle is the same: make a promise, create evidence, and build a habit that can survive contact with real people.", M, y, CONTENT_W, 18 * mm, color=MUTED, size=10.8, leading=14.2)

    y -= 25 * mm
    gap = 7 * mm
    cw = (CONTENT_W - gap) / 2
    columns = [
        (M, "THE APP BUILDER'S BLUEBOOK", "For the person turning a recurring problem into a useful product.", BLUE, BROWN, [
            "You have a workflow, not yet a product.",
            "You want to use AI without losing control.",
            "You need evidence before features.",
            "You want one owner-led path from build to launch.",
        ]),
        (M + cw + gap, "THE ROAM EDIT", "For the person turning taste, research or travel knowledge into a trusted media brand.", OLIVE_2, OLIVE, [
            "You have a point of view, not yet a machine.",
            "You want content that helps people decide.",
            "You need a niche people can feel.",
            "You want a clean path from content to product.",
        ]),
    ]
    for x, h, intro, accent, fill, bullets in columns:
        card(c, x, y - 88 * mm, cw, 84 * mm, fill=fill, stroke=accent, radius=6, top_bar=accent)
        label(c, "START HERE", x + 8 * mm, y - 12 * mm, cw - 16 * mm, color=colors.HexColor("#D7E2B5") if fill == OLIVE else colors.HexColor("#B9E2F4"), size=7.5)
        title(c, h, x + 8 * mm, y - 22 * mm, cw - 16 * mm, 20 * mm, color=WHITE, size=16, leading=18)
        body(c, intro, x + 8 * mm, y - 44 * mm, cw - 16 * mm, 13 * mm, color=colors.HexColor("#E4EAD7") if fill == OLIVE else colors.HexColor("#D9EDF5"), size=9.2, leading=11.8)
        yy = y - 58 * mm
        for bullet in bullets:
            circle(c, x + 10 * mm, yy - 2.1 * mm, 1.6 * mm, fill=accent)
            body(c, bullet, x + 15 * mm, yy, cw - 23 * mm, 8 * mm, color=WHITE, size=7.8, leading=9.2)
            yy -= 7.0 * mm

    y2 = y - 103 * mm
    label(c, "WHAT THEY SHARE", M, y2, CONTENT_W, color=BLUE)
    shared = [
        ("1", "A clear promise", "What useful result will this make easier?"),
        ("2", "A visible framework", "Can a reader see the choices and the order?"),
        ("3", "A small action", "What can be done today without a committee?"),
        ("4", "A learning loop", "What will you measure, repeat or stop?"),
    ]
    gap2 = 4 * mm
    sw = (CONTENT_W - 3 * gap2) / 4
    for i, (n, h, t) in enumerate(shared):
        x = M + i * (sw + gap2)
        card(c, x, 42 * mm, sw, 27 * mm, fill=WHITE, stroke=LINE, radius=4, top_bar=CORAL if i == 0 else BLUE)
        body(c, f"<b>{n}</b><br/><b>{h}</b><br/><font color='#68757D'>{t}</font>", x + 4 * mm, 62 * mm, sw - 8 * mm, 17 * mm, color=INK, size=8.1, leading=9.8, align=TA_CENTER)
    footer(c, 9, section="COMPARISON / PICK YOUR STARTING POINT")


def draw_cta(c: canvas.Canvas):
    rect(c, 0, 0, W, H, NAVY)
    rect(c, 0, H - 5 * mm, W, 5 * mm, CORAL)
    label(c, "END NOTE / CONTINUE THE EDIT", M, H - 20 * mm, CONTENT_W, color=CORAL, size=8.8)
    title(c, "Keep the useful parts.", M, H - 40 * mm, CONTENT_W, 24 * mm, color=WHITE, size=30, leading=32)
    body(c, "The full books go further: more capsules, more pills, more checklists, and more chances to turn judgement into a repeatable practice.", M, H - 70 * mm, 125 * mm, 22 * mm, color=colors.HexColor("#DDE9EF"), size=12, leading=15.5)

    y = 89 * mm
    gap = 7 * mm
    cw = (CONTENT_W - gap) / 2
    card(c, M, y, cw, 58 * mm, fill=colors.HexColor("#1E4260"), stroke=BLUE, radius=6, top_bar=BLUE)
    card(c, M + cw + gap, y, cw, 58 * mm, fill=colors.HexColor("#3C4928"), stroke=OLIVE_2, radius=6, top_bar=OLIVE_2)
    label(c, "BUILD", M + 7 * mm, y + 48 * mm, cw - 14 * mm, color=colors.HexColor("#B9E2F4"), size=7.6)
    title(c, "The App Builder's Bluebook", M + 7 * mm, y + 39 * mm, cw - 14 * mm, 19 * mm, color=WHITE, size=15.2, leading=16.5)
    body(c, "55 capsules. Six levels. One owner-led path from problem to operating product.", M + 7 * mm, y + 21 * mm, cw - 14 * mm, 15 * mm, color=colors.HexColor("#D9EDF5"), size=8.8, leading=11.2)
    label(c, "ROAM", M + cw + gap + 7 * mm, y + 48 * mm, cw - 14 * mm, color=colors.HexColor("#D7E2B5"), size=7.6)
    title(c, "The Roam Edit", M + cw + gap + 7 * mm, y + 39 * mm, cw - 14 * mm, 19 * mm, color=WHITE, size=17.2, leading=18.5)
    body(c, "17 pills. Five templates. A 30-day launch and a 90-day rhythm for useful travel media.", M + cw + gap + 7 * mm, y + 21 * mm, cw - 14 * mm, 15 * mm, color=colors.HexColor("#E4EAD7"), size=8.8, leading=11.2)

    label(c, "THE COMPLETE EDITIONS", M, 74 * mm, CONTENT_W, color=CORAL, size=7.8)
    rect(c, M, 54 * mm, 93 * mm, 15 * mm, fill=CORAL, stroke=None, radius=5)
    body(c, "<b>askakshay.com/store</b>", M + 6 * mm, 64 * mm, 81 * mm, 8 * mm, color=WHITE, size=15, leading=17, align=TA_CENTER)
    body(c, "Read the next page. Build the next useful thing. Choose a better route.", M, 41 * mm, CONTENT_W, 9 * mm, color=colors.HexColor("#B9C9D2"), size=9.7, leading=12, align=TA_CENTER)
    body(c, "askakshay.com/store", M, 26 * mm, CONTENT_W, 7 * mm, color=CORAL, size=8.5, leading=10, align=TA_CENTER)
    footer(c, 10, dark=True, section="ASK AKSHAY / COMPLETE EDITIONS")


def validate_sources() -> None:
    if not BLUEBOOK.exists() or not ROAM.exists():
        raise FileNotFoundError("Source PDFs are missing")
    blue = PdfReader(str(BLUEBOOK))
    roam = PdfReader(str(ROAM))
    if len(blue.pages) < 70 or len(roam.pages) < 85:
        raise ValueError("Unexpected source PDF page count")
    blue_text = "\n".join((blue.pages[i].extract_text() or "") for i in (0, 2, 6, 15, 29))
    roam_text = "\n".join((roam.pages[i].extract_text() or "") for i in (1, 12, 24, 58, 62))
    required_blue = ("The Five Jobs", "Evidence Ladder", "Inspect", "Plan")
    required_roam = ("niche", "carousel", "30-day", "90-day")
    if not all(term.lower() in blue_text.lower() for term in required_blue):
        raise ValueError("Bluebook source text check failed")
    if not all(term.lower() in roam_text.lower() for term in required_roam):
        raise ValueError("Roam source text check failed")


def build() -> None:
    validate_sources()
    BUILD.mkdir(exist_ok=True)
    c = canvas.Canvas(str(OUT), pagesize=A4)
    c.setTitle("Ask Akshay — Free Editorial Sampler")
    c.setAuthor("Ask Akshay")
    draw_cover(c); c.showPage()
    draw_how_to_read(c); c.showPage()
    draw_bluebook_overview(c); c.showPage()
    draw_bluebook_framework(c); c.showPage()
    draw_bluebook_lesson(c); c.showPage()
    draw_roam_overview(c); c.showPage()
    draw_roam_framework(c); c.showPage()
    draw_roam_lesson(c); c.showPage()
    draw_comparison(c); c.showPage()
    draw_cta(c); c.showPage()
    c.save()
    pages = len(PdfReader(str(OUT)).pages)
    if pages != 10:
        raise ValueError(f"Expected 10 sampler pages, got {pages}")
    shutil.rmtree(BUILD, ignore_errors=True)


if __name__ == "__main__":
    build()
