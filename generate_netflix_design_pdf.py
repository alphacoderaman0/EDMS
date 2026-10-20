"""
Generate a comprehensive Netflix India visual design system PDF
for AI coding agents to restyle existing websites.
"""

from __future__ import annotations

import os
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    Flowable,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUT_PATH = Path(__file__).parent / "Netflix_India_Design_System_Reference.pdf"
PAGE_W, PAGE_H = A4
MARGIN = 0.7 * inch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class ColorSwatchRow(Flowable):
    """Row of labeled color swatches."""

    def __init__(self, items, width=PAGE_W - 2 * MARGIN, swatch_h=36):
        super().__init__()
        self.items = items  # list of (name, hex, role)
        self.width = width
        self.swatch_h = swatch_h
        self.height = swatch_h + 42

    def draw(self):
        n = len(self.items)
        gap = 8
        w = (self.width - gap * (n - 1)) / n
        c = self.canv
        for i, (name, hex_code, role) in enumerate(self.items):
            x = i * (w + gap)
            fill = colors.HexColor(hex_code)
            c.setFillColor(fill)
            c.setStrokeColor(colors.HexColor("#444444"))
            c.setLineWidth(0.5)
            c.roundRect(x, 42, w, self.swatch_h, 4, fill=1, stroke=1)
            c.setFillColor(colors.HexColor("#FFFFFF"))
            c.setFont("Helvetica-Bold", 8)
            c.drawString(x + 4, 30, name[:22])
            c.setFont("Helvetica", 7.5)
            c.setFillColor(colors.HexColor("#B3B3B3"))
            c.drawString(x + 4, 18, hex_code.upper())
            c.setFillColor(colors.HexColor("#808080"))
            c.setFont("Helvetica", 6.5)
            # wrap role lightly
            c.drawString(x + 4, 6, role[:28])


class ButtonPreview(Flowable):
    """Visual mock of a Netflix-style button."""

    def __init__(self, label, bg, fg="#FFFFFF", radius=8, pad_x=22, pad_y=10, font_size=12):
        super().__init__()
        self.label = label
        self.bg = bg
        self.fg = fg
        self.radius = radius
        self.pad_x = pad_x
        self.pad_y = pad_y
        self.font_size = font_size
        self.width = 200
        self.height = pad_y * 2 + font_size + 8

    def wrap(self, availWidth, availHeight):
        # measure text
        return (min(self.width, availWidth), self.height)

    def draw(self):
        c = self.canv
        text_w = c.stringWidth(self.label, "Helvetica-Bold", self.font_size)
        bw = text_w + self.pad_x * 2
        bh = self.height - 2
        c.setFillColor(colors.HexColor(self.bg))
        c.roundRect(0, 1, bw, bh, self.radius, fill=1, stroke=0)
        c.setFillColor(colors.HexColor(self.fg))
        c.setFont("Helvetica-Bold", self.font_size)
        c.drawString(self.pad_x, self.pad_y + 2, self.label)


class InputPreview(Flowable):
    def __init__(self):
        super().__init__()
        self.width = 280
        self.height = 56

    def wrap(self, availWidth, availHeight):
        return (min(self.width, availWidth), self.height)

    def draw(self):
        c = self.canv
        c.setFillColor(colors.HexColor("#2D2D2D"))
        c.roundRect(0, 0, 280, 56, 8, fill=1, stroke=0)
        c.setFillColor(colors.HexColor("#808080"))
        c.setFont("Helvetica", 9)
        c.drawString(16, 36, "Email address")
        c.setFillColor(colors.HexColor("#FFFFFF"))
        c.setFont("Helvetica", 12)
        c.drawString(16, 14, "name@example.com")


class GradientBar(Flowable):
    def __init__(self, stops, label="", width=PAGE_W - 2 * MARGIN, height=28):
        super().__init__()
        self.stops = stops  # list of hex
        self.label = label
        self.width = width
        self.height = height + (16 if label else 0)

    def draw(self):
        c = self.canv
        y = 16 if self.label else 0
        bar_h = 28
        steps = 80
        for i in range(steps):
            t = i / (steps - 1)
            pos = t * (len(self.stops) - 1)
            i0 = int(pos)
            i1 = min(i0 + 1, len(self.stops) - 1)
            local = pos - i0
            c0 = colors.HexColor(self.stops[i0])
            c1 = colors.HexColor(self.stops[i1])
            r = c0.red + (c1.red - c0.red) * local
            g = c0.green + (c1.green - c0.green) * local
            b = c0.blue + (c1.blue - c0.blue) * local
            c.setFillColor(colors.Color(r, g, b))
            x = (i / steps) * self.width
            c.rect(x, y, self.width / steps + 1, bar_h, fill=1, stroke=0)
        if self.label:
            c.setFillColor(colors.HexColor("#B3B3B3"))
            c.setFont("Helvetica", 8)
            c.drawString(0, 2, self.label)


class CodeBlock(Flowable):
    """Dark code/snippet block."""

    def __init__(self, text, width=PAGE_W - 2 * MARGIN):
        super().__init__()
        self.text = text.rstrip("\n")
        self.width = width
        lines = self.text.split("\n")
        self.lines = lines
        self.height = 14 + len(lines) * 11 + 10

    def wrap(self, availWidth, availHeight):
        self.width = min(self.width, availWidth)
        return (self.width, self.height)

    def draw(self):
        c = self.canv
        c.setFillColor(colors.HexColor("#161616"))
        c.setStrokeColor(colors.HexColor("#333333"))
        c.setLineWidth(0.6)
        c.roundRect(0, 0, self.width, self.height, 6, fill=1, stroke=1)
        c.setFillColor(colors.HexColor("#E6E6E6"))
        c.setFont("Courier", 7.5)
        y = self.height - 16
        for line in self.lines:
            # truncate long lines
            max_chars = int(self.width / 4.4)
            c.drawString(10, y, line[:max_chars])
            y -= 11


def make_styles():
    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="CoverTitle",
            fontName="Helvetica-Bold",
            fontSize=28,
            leading=34,
            textColor=colors.HexColor("#FFFFFF"),
            alignment=TA_CENTER,
            spaceAfter=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CoverSub",
            fontName="Helvetica",
            fontSize=12,
            leading=18,
            textColor=colors.HexColor("#B3B3B3"),
            alignment=TA_CENTER,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="H1",
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#FFFFFF"),
            spaceBefore=6,
            spaceAfter=10,
            borderPadding=3,
        )
    )
    styles.add(
        ParagraphStyle(
            name="H2",
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=17,
            textColor=colors.HexColor("#E50914"),
            spaceBefore=12,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="H3",
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#FFFFFF"),
            spaceBefore=8,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Body",
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#E6E6E6"),
            alignment=TA_JUSTIFY,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodyLeft",
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#E6E6E6"),
            alignment=TA_LEFT,
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Muted",
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#808080"),
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BulletText",
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#E6E6E6"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="TableCell",
            fontName="Helvetica",
            fontSize=7.5,
            leading=10,
            textColor=colors.HexColor("#E6E6E6"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="TableHeader",
            fontName="Helvetica-Bold",
            fontSize=7.5,
            leading=10,
            textColor=colors.HexColor("#FFFFFF"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="Callout",
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#FFFFFF"),
            backColor=colors.HexColor("#232323"),
            borderPadding=8,
            spaceBefore=6,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="FooterNote",
            fontName="Helvetica",
            fontSize=7.5,
            leading=10,
            textColor=colors.HexColor("#808080"),
            alignment=TA_CENTER,
        )
    )
    return styles


def dark_table(data, col_widths):
    style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#232323")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#FFFFFF")),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#161616")),
            ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#E6E6E6")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ("LEADING", (0, 0), (-1, -1), 10),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#333333")),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#161616"), colors.HexColor("#1A1A1A")]),
        ]
    )
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(style)
    return t


def bullets(items, styles):
    flow = []
    for item in items:
        flow.append(
            Paragraph(f"•  {item}", styles["BulletText"])
        )
    return flow


def add_page_decorations(c: canvas.Canvas, doc):
    c.saveState()
    # page background
    c.setFillColor(colors.HexColor("#000000"))
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    # top red accent line
    c.setFillColor(colors.HexColor("#E50914"))
    c.rect(0, PAGE_H - 3, PAGE_W, 3, fill=1, stroke=0)
    # footer
    c.setFillColor(colors.HexColor("#414141"))
    c.rect(MARGIN, 28, PAGE_W - 2 * MARGIN, 0.5, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#808080"))
    c.setFont("Helvetica", 7)
    c.drawString(MARGIN, 16, "Netflix India Design System Reference  |  For AI restyling agents  |  Aesthetic only — do not copy trademarks")
    c.drawRightString(PAGE_W - MARGIN, 16, f"Page {doc.page}")
    c.restoreState()


def build():
    styles = make_styles()
    story = []
    content_w = PAGE_W - 2 * MARGIN

    # ===================== COVER =====================
    story.append(Spacer(1, 1.4 * inch))
    story.append(Paragraph("NETFLIX INDIA", styles["CoverTitle"]))
    story.append(Paragraph("Visual Design System Reference", styles["CoverTitle"]))
    story.append(Spacer(1, 8))
    story.append(
        Paragraph(
            "Implementation-focused guide for AI coding agents<br/>"
            "to restyle an existing website with a Netflix-like cinematic aesthetic<br/>"
            "without changing functionality, business logic, or application behavior.",
            styles["CoverSub"],
        )
    )
    story.append(Spacer(1, 18))
    bar = Table([[""]], colWidths=[120], rowHeights=[4])
    bar.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#E50914"))]))
    wrap = Table([[bar]], colWidths=[content_w])
    wrap.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    story.append(wrap)
    story.append(Spacer(1, 20))
    story.append(
        Paragraph(
            "Source analyzed: https://www.netflix.com/in/ (marketing / signup homepage)<br/>"
            "Document purpose: design tokens, component recipes, CSS variables, agent rules<br/>"
            "Scope: visual styling only — not a trademark or brand-asset license",
            styles["CoverSub"],
        )
    )
    story.append(Spacer(1, 40))
    meta = [
        ["Document type", "Design system / token reference"],
        ["Primary brand red", "#E50914"],
        ["Canvas", "#000000"],
        ["Typeface", "Netflix Sans → Helvetica Neue / Segoe UI / Roboto / Ubuntu / sans-serif"],
        ["Shape language", "8px radius family (cards, CTA, inputs, FAQ)"],
        ["Depth model", "Tone ladder (no box-shadows on marketing chrome)"],
        ["Audience", "AI coding agent performing CSS/theme restyle"],
    ]
    story.append(dark_table(
        [[Paragraph(f"<b>{a}</b>", styles["TableCell"]), Paragraph(b, styles["TableCell"])] for a, b in meta],
        [140, content_w - 140],
    ))
    story.append(PageBreak())

    # ===================== TOC =====================
    story.append(Paragraph("1. Contents", styles["H1"]))
    toc = [
        "2. How an AI agent should use this document",
        "3. Visual theme & atmosphere",
        "4. Color system (tokens, roles, swatches)",
        "5. Typography (family, scale, weights, rules)",
        "6. Spacing, layout & grid",
        "7. Depth, elevation, borders & shadows",
        "8. Gradients & overlays",
        "9. Component catalog (buttons, forms, cards, FAQ, nav, footer)",
        "10. Motion & interaction states",
        "11. Responsive behavior",
        "12. CSS custom properties (copy-paste token sheet)",
        "13. Agent implementation checklist & guardrails",
        "14. Do's and don'ts",
        "15. Mapping Netflix aesthetics onto an existing site (EDMS-safe)",
        "Appendix A — Quick token cheat sheet",
    ]
    for t in toc:
        story.append(Paragraph(t, styles["BodyLeft"]))
    story.append(PageBreak())

    # ===================== AGENT USE =====================
    story.append(Paragraph("2. How an AI agent should use this document", styles["H1"]))
    story.append(
        Paragraph(
            "This PDF is a <b>styling contract</b>. Treat it as the source of visual truth when "
            "restyling an existing application. Apply tokens and patterns to presentation layers "
            "(CSS, templates, component class names). Do <b>not</b> alter routes, forms' server "
            "handlers, authentication, database models, validation rules, or business workflows.",
            styles["Body"],
        )
    )
    story.append(Paragraph("Priority order when conflicting guidance appears", styles["H2"]))
    for i, item in enumerate(
        [
            "Preserve existing functionality and DOM structure needed by JS/backend.",
            "Apply color, typography, spacing, radius, and surface tokens from this doc.",
            "Match component <i>visual recipes</i> (button fill, input height) without renaming server fields.",
            "Prefer CSS variables / theme files over hardcoded one-off colors.",
            "When unsure, choose the darker surface and higher contrast — Netflix is cinema-dark.",
        ],
        1,
    ):
        story.append(Paragraph(f"<b>{i}.</b>  {item}", styles["BodyLeft"]))

    story.append(Paragraph("Safe change surface (allowed)", styles["H2"]))
    for item in [
        "Global CSS / SCSS / Tailwind theme tokens",
        "Template class names and presentational markup wrappers",
        "Button, input, card, navbar, footer, accordion visual styles",
        "Backgrounds, overlays, gradients, borders, focus rings",
        "Font stacks and type scale mappings",
    ]:
        story.append(Paragraph(f"•  {item}", styles["BulletText"]))

    story.append(Paragraph("Forbidden change surface (never touch for “Netflix look”)", styles["H2"]))
    for item in [
        "View logic, serializers, models, migrations, URL routing",
        "Form field names, CSRF handling, auth middleware, permissions",
        "API contracts, query parameters, session behavior",
        "Copying Netflix trademarks, wordmark SVG, or proprietary Netflix Sans font files into production without license",
    ]:
        story.append(Paragraph(f"•  {item}", styles["BulletText"]))

    story.append(Spacer(1, 8))
    story.append(
        Paragraph(
            "<b>Font licensing note:</b> Netflix Sans is proprietary. For a third-party site, "
            "use the documented fallback stack (Helvetica Neue, Segoe UI, Roboto, Ubuntu, "
            "sans-serif) or a licensed open alternative (e.g. Inter Black for hero + Inter Regular "
            "for body) while preserving the weight silhouette described in §5.",
            styles["Callout"],
        )
    )
    story.append(PageBreak())

    # ===================== THEME =====================
    story.append(Paragraph("3. Visual theme & atmosphere", styles["H1"]))
    story.append(
        Paragraph(
            "Netflix India’s public homepage feels like a <b>streaming theater before the lights "
            "come up</b>: a pure black canvas, movie-poster artwork carrying almost all color, "
            "and a single red “ticket” CTA. The UI is conversion-first (email capture + Get Started) "
            "and content-first (trending posters, feature tiles, FAQ).",
            styles["Body"],
        )
    )
    story.append(Paragraph("Mood keywords", styles["H2"]))
    story.append(
        Paragraph(
            "Cinematic · High-contrast · Dark · Direct · Promotional-but-not-playful · "
            "Media-first · Conversion-oriented · Disciplined red accent",
            styles["BodyLeft"],
        )
    )
    story.append(Paragraph("Design density", styles["H2"]))
    story.append(
        Paragraph(
            "Medium–high information density in carousels and FAQ, but low visual chrome. "
            "Dark backgrounds and strong section separation keep modules readable. Whitespace "
            "is purposeful and vertical (large section gutters), not airy “startup landing page” "
            "whitespace.",
            styles["Body"],
        )
    )
    story.append(Paragraph("Page architecture (marketing funnel)", styles["H2"]))
    arch = [
        ["#", "Section", "Role"],
        ["1", "Top nav", "Logo left · language picker · red Sign In"],
        ["2", "Hero", "Display headline · price line · email + CTA"],
        ["3", "Trending rail", "Horizontal posters + outline rank numerals"],
        ["4", "Reasons to join", "2×2 / 4-col feature cards with illustration space"],
        ["5", "FAQ accordion", "Stacked charcoal rows with + / × chevron"],
        ["6", "Secondary email CTA", "Repeat of email + Get Started"],
        ["7", "Footer", "Muted link columns + legal caption"],
    ]
    story.append(dark_table(
        [[Paragraph(a, styles["TableHeader"] if i == 0 else styles["TableCell"]) for a in row]
         for i, row in enumerate(arch)],
        [28, 110, content_w - 138],
    ))
    story.append(PageBreak())

    # ===================== COLORS =====================
    story.append(Paragraph("4. Color system", styles["H1"]))
    story.append(
        Paragraph(
            "Palette discipline is the brand. Red is a <b>single-voltage accent</b> used sparingly "
            "for actions and logo emphasis. Almost everything else is black, charcoal, white, or "
            "muted gray. Gradients appear mainly behind the trending rail — not as page washes.",
            styles["Body"],
        )
    )

    story.append(Paragraph("4.1 Core surfaces", styles["H2"]))
    story.append(ColorSwatchRow([
        ("Canvas", "#000000", "Page base"),
        ("Surface Deep", "#161616", "Rail backdrop"),
        ("Surface Card", "#232323", "FAQ / feature"),
        ("Surface Input", "#2D2D2D", "Email field"),
    ]))
    story.append(Spacer(1, 6))
    story.append(ColorSwatchRow([
        ("Panel alt", "#181818", "Alt tile surface"),
        ("Charcoal", "#141414", "Legacy card bg"),
        ("Hairline", "#414141", "Borders / rules"),
        ("Border soft", "#333333", "Tile strokes"),
    ]))

    story.append(Paragraph("4.2 Brand & accent", styles["H2"]))
    story.append(ColorSwatchRow([
        ("Netflix Red", "#E50914", "CTA / Sign In"),
        ("Red Hover", "#C11119", "Primary hover"),
        ("Dark Red", "#B20710", "N symbol depth"),
        ("Focus Ring", "#A9A9A9", "Focus default"),
    ]))

    story.append(Paragraph("4.3 Text & ink", styles["H2"]))
    story.append(ColorSwatchRow([
        ("Ink Base", "#FFFFFF", "Headings / body"),
        ("Ink Soft", "#B3B3B3", "Secondary copy"),
        ("Ink Muted", "#808080", "Footer / legal"),
        ("Ink Dim", "#A9A9A9", "Focus / helpers"),
    ]))

    story.append(Paragraph("4.4 Gradient stops (trending rail wash)", styles["H2"]))
    story.append(ColorSwatchRow([
        ("Navy", "#192247", "Rail left"),
        ("Wine", "#210E17", "Rail mid"),
        ("Burgundy", "#461518", "Rail right"),
        ("Oxblood", "#6F181D", "Far accent"),
    ]))
    story.append(Spacer(1, 4))
    story.append(GradientBar(
        ["#192247", "#210E17", "#461518", "#6F181D"],
        label="Trending-rail linear gradient (navy → wine → burgundy → oxblood)",
    ))

    story.append(Paragraph("4.5 Token roles (implementation map)", styles["H2"]))
    color_rows = [
        ["Token", "Hex", "Role / usage rules"],
        ["--nf-canvas", "#000000", "html/body background; nav; footer"],
        ["--nf-surface-deep", "#161616", "Carousel / rail container"],
        ["--nf-surface-card", "#232323", "Cards, FAQ rows, secondary buttons"],
        ["--nf-surface-input", "#2D2D2D", "Text inputs on dark chrome"],
        ["--nf-red", "#E50914", "Primary CTA + Sign In ONLY"],
        ["--nf-red-hover", "#C11119", "Hover / active for primary CTA"],
        ["--nf-ink", "#FFFFFF", "Primary text on dark"],
        ["--nf-ink-soft", "#B3B3B3", "Supporting body / placeholders"],
        ["--nf-ink-muted", "#808080", "Footer links, legal, captions"],
        ["--nf-hairline", "#414141", "1px borders, dividers"],
        ["--nf-border", "#333333", "Optional tile outline"],
        ["--nf-overlay", "rgba(0,0,0,.64)", "Hero image darkening"],
        ["--nf-focus", "rgba(255,255,255,.9)", "Visible focus ring on dark"],
    ]
    story.append(dark_table(
        [[Paragraph(c, styles["TableHeader"] if r == 0 else styles["TableCell"]) for c in row]
         for r, row in enumerate(color_rows)],
        [110, 90, content_w - 200],
    ))

    story.append(Paragraph("4.6 Color frequency discipline", styles["H2"]))
    for item in [
        "Use Netflix Red on CTAs and critical auth entry points — not on body links, badges everywhere, or panel backgrounds.",
        "Never use burgundy/oxblood as button fills; they are gradient stops only.",
        "Body text is white (#FFFFFF), not gray. Gray is for secondary/footer only.",
        "Do not invent a light-mode Netflix marketing skin for this aesthetic; the system assumes dark canvas + bright posters.",
    ]:
        story.append(Paragraph(f"•  {item}", styles["BulletText"]))
    story.append(PageBreak())

    # ===================== TYPOGRAPHY =====================
    story.append(Paragraph("5. Typography", styles["H1"]))
    story.append(
        Paragraph(
            "One family everywhere. Hierarchy comes from <b>size + weight</b>, not from mixing "
            "serif/sans. The signature silhouette is a very heavy hero against light body weight.",
            styles["Body"],
        )
    )
    story.append(Paragraph("5.1 Font stack", styles["H2"]))
    story.append(CodeBlock(
        'font-family: "Netflix Sans", "Helvetica Neue", "Segoe UI",\n'
        "             Roboto, Ubuntu, sans-serif;"
    ))
    story.append(Spacer(1, 6))
    story.append(
        Paragraph(
            "Observed weights on the live site / extracts: <b>400</b> (body), <b>500</b> "
            "(section titles, CTA labels), <b>700</b> or <b>900</b> (hero display depending on "
            "measurement source). For agent implementation, prefer: hero <b>800–900</b>, "
            "emphasis <b>500</b>, body <b>400</b>. Avoid filling the middle with 600/700 body headings.",
            styles["Body"],
        )
    )

    story.append(Paragraph("5.2 Type scale", styles["H2"]))
    type_rows = [
        ["Token", "Size", "Weight", "Line-height", "Color", "Use"],
        ["hero-display", "56px → 32px", "900 / 700", "1.25 (≈70px)", "#FFFFFF", "Main hero H1"],
        ["section-title", "24px", "500", "1.2–normal", "#FFFFFF", "Trending / Reasons"],
        ["accordion-title", "24px", "400", "normal", "#FFFFFF", "FAQ question row"],
        ["button-label", "16–24px", "500", "1.0", "#FFFFFF", "Get Started CTA"],
        ["body-emphasis", "20px", "500", "normal", "#FFFFFF", "Ready to watch?"],
        ["body-base", "16px", "400", "1.5 (24px)", "#FFFFFF", "Descriptions, labels"],
        ["body-sm", "14px", "400–500", "1.5 (21px)", "#FFFFFF / #808080", "Nav, footer links"],
        ["legal-caption", "13px", "400", "normal", "#808080", "Copyright / reCAPTCHA"],
        ["price-line", "16–20px", "400", "1.4", "#FFFFFF", "Starts at ₹149…"],
    ]
    story.append(dark_table(
        [[Paragraph(c, styles["TableHeader"] if r == 0 else styles["TableCell"]) for c in row]
         for r, row in enumerate(type_rows)],
        [78, 70, 55, 70, 70, content_w - 343],
    ))

    story.append(Paragraph("5.3 Typography principles for agents", styles["H2"]))
    for item in [
        "Keep headlines short, forceful, and white on black.",
        "Tighten letter-spacing slightly on large display (-0.01em to -0.02em) if the fallback font feels loose.",
        "Do not use decorative serifs, monospace UI, or multi-font “editorial” mixes for this aesthetic.",
        "CTA label weight should feel medium (500), not ultra-bold — the red fill carries the emphasis.",
        "Outline-stroked giant numerals behind posters are a signature for ranked lists — optional on non-media sites; if used, stroke-only white/light glyphs, not filled.",
    ]:
        story.append(Paragraph(f"•  {item}", styles["BulletText"]))
    story.append(PageBreak())

    # ===================== SPACING =====================
    story.append(Paragraph("6. Spacing, layout & grid", styles["H1"]))
    story.append(
        Paragraph(
            "Base unit is effectively <b>8px</b>, with micro 2–3px steps and large 24 / 64px "
            "section rhythm. Horizontal gutters on desktop are unusually generous.",
            styles["Body"],
        )
    )
    story.append(Paragraph("6.1 Spacing scale", styles["H2"]))
    space_rows = [
        ["Token", "Value", "Typical use"],
        ["--space-xxs", "2px", "Hairline offsets, micro gaps"],
        ["--space-xs", "3–4px", "Icon nudge, tight stacks"],
        ["--space-sm", "8px", "Compact control padding, card gaps"],
        ["--space-md", "12px", "Internal tile rhythm"],
        ["--space-base", "16px", "Nav padding, form gaps"],
        ["--space-lg", "24px", "Card / FAQ internal padding"],
        ["--space-xl", "32px", "Module separation"],
        ["--space-2xl", "48px", "Section padding (compact)"],
        ["--space-3xl", "64px", "Major section gutters"],
        ["--page-gutter-desktop", "≈80–148px", "Left/right page margin at ≥1280px"],
        ["--page-gutter-mobile", "16px", "Collapsed gutters"],
        ["--btn-pad", "8px 22px", "Primary CTA padding"],
        ["--input-height", "56px", "Email field height"],
    ]
    story.append(dark_table(
        [[Paragraph(c, styles["TableHeader"] if r == 0 else styles["TableCell"]) for c in row]
         for r, row in enumerate(space_rows)],
        [130, 90, content_w - 220],
    ))

    story.append(Paragraph("6.2 Layout principles", styles["H2"]))
    for item in [
        "Linear single-column funnel on marketing pages — no sidebars, no dashboard chrome.",
        "Primary conversion control (email + CTA) appears above the fold and again after FAQ.",
        "Content rails scroll horizontally; sections stack vertically.",
        "Feature grids: 4 columns desktop → 2×2 tablet → 1 column mobile.",
        "Max content width feels centered with large side gutters; avoid edge-to-edge text blocks.",
        "Cards may use heavy bottom padding when an illustration sits under copy (e.g. 24px 16px 128px).",
    ]:
        story.append(Paragraph(f"•  {item}", styles["BulletText"]))

    story.append(Paragraph("6.3 Border radius scale", styles["H2"]))
    radius_rows = [
        ["Token", "Value", "Use"],
        ["--radius-xs", "2–4px", "Language picker, small chrome, Sign In (tighter)"],
        ["--radius-md", "8px", "DEFAULT: CTA, inputs, FAQ, feature cards, posters"],
        ["--radius-lg", "16px", "Rare — logo glyph container / soft tiles"],
        ["--radius-pill", "999px", "AVOID for primary CTA (breaks one-radius family)"],
    ]
    story.append(dark_table(
        [[Paragraph(c, styles["TableHeader"] if r == 0 else styles["TableCell"]) for c in row]
         for r, row in enumerate(radius_rows)],
        [100, 70, content_w - 170],
    ))
    story.append(PageBreak())

    # ===================== DEPTH =====================
    story.append(Paragraph("7. Depth, elevation, borders & shadows", styles["H1"]))
    story.append(
        Paragraph(
            "Netflix marketing chrome uses <b>almost no box-shadows</b>. Depth = stacked charcoal "
            "tones on black. Shadows, if any, belong to modal/product overlays — not FAQ cards.",
            styles["Body"],
        )
    )
    elev = [
        ["Level", "Surface", "Treatment"],
        ["0 Base", "#000000", "Page, nav, footer — flat"],
        ["1 Deep", "#161616", "Rails — flat"],
        ["2 Card", "#232323", "FAQ / features — flat, 8px radius"],
        ["3 Input", "#2D2D2D", "Interactive fields — flat"],
        ["Overlay", "rgba(0,0,0,.5–.8)", "Hero/poster readability wash"],
        ["Optional product shadow", "0 8px 24px rgba(0,0,0,.45)", "Only if you need floating dialogs"],
    ]
    story.append(dark_table(
        [[Paragraph(c, styles["TableHeader"] if r == 0 else styles["TableCell"]) for c in row]
         for r, row in enumerate(elev)],
        [110, 130, content_w - 240],
    ))
    story.append(Paragraph("Borders", styles["H2"]))
    for item in [
        "Default hairline: 1px solid #414141 (or #333333 on tiles).",
        "Inputs often rely on fill contrast more than heavy borders; focus may brighten border to white.",
        "Avoid thick colored borders and glow outlines (no neon red rings).",
        "Dividers in footers: 1px #414141.",
    ]:
        story.append(Paragraph(f"•  {item}", styles["BulletText"]))

    story.append(Paragraph("Focus rings (a11y — keep when restyling)", styles["H2"]))
    story.append(CodeBlock(
        "/* Netflix-like focus on dark UI */\n"
        ":focus-visible {\n"
        "  outline: 2px solid #FFFFFF;\n"
        "  outline-offset: 2px;\n"
        "}\n"
        "/* Fallback observed token */\n"
        "--focus-ring-color: #a9a9a9;"
    ))
    story.append(PageBreak())

    # ===================== GRADIENTS =====================
    story.append(Paragraph("8. Gradients & overlays", styles["H1"]))
    story.append(Paragraph("8.1 Hero image overlay", styles["H2"]))
    story.append(
        Paragraph(
            "Hero media sits under a dark overlay so white type stays readable. Typical recipe:",
            styles["Body"],
        )
    )
    story.append(CodeBlock(
        ".hero {\n"
        "  background-color: #000;\n"
        "  background-image:\n"
        "    linear-gradient(to top, rgba(0,0,0,.9) 0%, rgba(0,0,0,.55) 40%,\n"
        "                    rgba(0,0,0,.35) 70%, rgba(0,0,0,.55) 100%),\n"
        "    url(/your-hero.jpg);\n"
        "  background-size: cover;\n"
        "  background-position: center top;\n"
        "}"
    ))
    story.append(Spacer(1, 8))
    story.append(Paragraph("8.2 Trending rail wash", styles["H2"]))
    story.append(GradientBar(
        ["#192247", "#210E17", "#461518", "#6F181D"],
        label="linear-gradient(90deg, #192247, #210E17, #461518, #6F181D)",
    ))
    story.append(Spacer(1, 8))
    story.append(CodeBlock(
        ".trending-rail {\n"
        "  background:\n"
        "    linear-gradient(90deg, #192247 0%, #210E17 40%, #461518 75%, #6F181D 100%),\n"
        "    #161616;\n"
        "}"
    ))
    story.append(Paragraph("8.3 Rules", styles["H2"]))
    for item in [
        "Do not purple-wash the entire site; keep gradients sectional.",
        "Prefer darkening overlays over frosted glass blur for Netflix-like marketing chrome.",
        "Poster art should be the brightest chroma on the page.",
    ]:
        story.append(Paragraph(f"•  {item}", styles["BulletText"]))
    story.append(PageBreak())

    # ===================== COMPONENTS =====================
    story.append(Paragraph("9. Component catalog", styles["H1"]))

    story.append(Paragraph("9.1 Primary CTA button (Get Started)", styles["H2"]))
    story.append(ButtonPreview("Get Started  ›", "#E50914", radius=8, pad_x=22, pad_y=10, font_size=14))
    story.append(Spacer(1, 6))
    story.append(CodeBlock(
        ".btn-primary {\n"
        "  background: #E50914;\n"
        "  color: #FFFFFF;\n"
        "  border: none;\n"
        "  border-radius: 8px;\n"
        "  padding: 8px 22px;          /* or min-height: 48px */\n"
        "  font-size: 18px;            /* 16–24px acceptable */\n"
        "  font-weight: 500;\n"
        "  line-height: 1;\n"
        "  cursor: pointer;\n"
        "  display: inline-flex;\n"
        "  align-items: center;\n"
        "  gap: 8px;\n"
        "}\n"
        ".btn-primary:hover { background: #C11119; }\n"
        ".btn-primary:active { background: #B20710; }"
    ))

    story.append(Paragraph("9.2 Sign In (nav compact)", styles["H2"]))
    story.append(ButtonPreview("Sign In", "#E50914", radius=4, pad_x=16, pad_y=6, font_size=11))
    story.append(Spacer(1, 6))
    story.append(
        Paragraph(
            "Same red, tighter radius (4px), smaller padding (≈4–8px × 16px), body-sm/base type. "
            "Quieter than the hero CTA but still unmistakable.",
            styles["Body"],
        )
    )

    story.append(Paragraph("9.3 Secondary button", styles["H2"]))
    story.append(ButtonPreview("Secondary", "#232323", radius=8, pad_x=22, pad_y=10, font_size=12))
    story.append(Spacer(1, 4))
    story.append(
        Paragraph(
            "Fill #232323 (or rgba(109,109,110,.7) for translucent media overlays), white text, "
            "8px radius, no border. Used for non-primary actions on dark UI.",
            styles["Body"],
        )
    )

    story.append(Paragraph("9.4 Email / text input", styles["H2"]))
    story.append(InputPreview())
    story.append(Spacer(1, 6))
    story.append(CodeBlock(
        ".input {\n"
        "  background: #2D2D2D;                 /* or rgba(22,22,22,.75) */\n"
        "  color: #FFFFFF;\n"
        "  border: 1px solid #666666;           /* optional; many builds borderless */\n"
        "  border-radius: 8px;\n"
        "  min-height: 56px;\n"
        "  padding: 24px 16px 8px;              /* room for floating label */\n"
        "  font-size: 16px;\n"
        "  font-weight: 400;\n"
        "  width: 100%;\n"
        "}\n"
        ".input::placeholder { color: #808080; }\n"
        ".input:focus {\n"
        "  outline: none;\n"
        "  border-color: #FFFFFF;\n"
        "}"
    ))

    story.append(Paragraph("9.5 Email capture composite", styles["H2"]))
    story.append(
        Paragraph(
            "Desktop: horizontal flex — input grows, CTA fixed on the right, gap ≈ 8px. "
            "Mobile: stack vertically — full-width input, full-width CTA beneath. "
            "Repeat this pattern near the bottom of long pages.",
            styles["Body"],
        )
    )
    story.append(PageBreak())

    story.append(Paragraph("9.6 Feature card", styles["H2"]))
    story.append(CodeBlock(
        ".feature-card {\n"
        "  background: #232323;\n"
        "  color: #FFFFFF;\n"
        "  border-radius: 8px;\n"
        "  padding: 24px 16px 48px;   /* add more bottom if illustration */\n"
        "  border: none;             /* tone step provides separation */\n"
        "}\n"
        ".feature-card h3 { font-size: 24px; font-weight: 500; margin: 0 0 8px; }\n"
        ".feature-card p  { font-size: 16px; font-weight: 400; color: #FFFFFF; }\n"
        ".feature-card:hover { background: #2A2A2A; }  /* subtle lift via tone */"
    ))

    story.append(Paragraph("9.7 FAQ accordion row", styles["H2"]))
    story.append(CodeBlock(
        ".faq-row {\n"
        "  background: #232323;\n"
        "  color: #FFFFFF;\n"
        "  border-radius: 8px;\n"
        "  padding: 24px;\n"
        "  margin-bottom: 8px;\n"
        "  display: flex;\n"
        "  justify-content: space-between;\n"
        "  align-items: center;\n"
        "  min-height: 72px;\n"
        "  cursor: pointer;\n"
        "}\n"
        ".faq-row .title { font-size: 24px; font-weight: 400; }\n"
        ".faq-row .icon  { font-size: 28px; font-weight: 300; } /* + / × */\n"
        ".faq-panel {\n"
        "  background: #232323;\n"
        "  padding: 0 24px 24px;\n"
        "  font-size: 16px;\n"
        "  line-height: 1.5;\n"
        "}"
    ))

    story.append(Paragraph("9.8 Poster / media tile", styles["H2"]))
    for item in [
        "8px clipped corner radius on artwork.",
        "No heavy card chrome — the image is the component.",
        "Optional rank numeral: large outline stroke behind/beside the poster.",
        "Horizontal scroll container with snap optional; keep posters large enough to read titles.",
    ]:
        story.append(Paragraph(f"•  {item}", styles["BulletText"]))

    story.append(Paragraph("9.9 Top navigation", styles["H2"]))
    for item in [
        "Background transparent or #000; no drop shadow; no bottom border required.",
        "Logo left; utilities right (language + Sign In).",
        "Padding ≈ 16px vertical; horizontal aligned to page gutters.",
        "On scroll over hero imagery, keep high-contrast red Sign In.",
    ]:
        story.append(Paragraph(f"•  {item}", styles["BulletText"]))

    story.append(Paragraph("9.10 Footer", styles["H2"]))
    for item in [
        "Canvas #000 background.",
        "Link text #808080 at 14px; hover to #FFFFFF underline optional.",
        "Multi-column link lists on desktop; stacked on mobile.",
        "Legal caption 13px muted.",
    ]:
        story.append(Paragraph(f"•  {item}", styles["BulletText"]))
    story.append(PageBreak())

    # ===================== MOTION =====================
    story.append(Paragraph("10. Motion & interaction states", styles["H1"]))
    story.append(
        Paragraph(
            "Motion is restrained. Prefer short opacity/height transitions over bounce or parallax.",
            styles["Body"],
        )
    )
    motion_rows = [
        ["Interaction", "Behavior", "Suggested CSS"],
        ["Button hover", "Darken red ~10–15%", "background #C11119; transition 150ms ease"],
        ["Card hover", "Slightly lighter charcoal", "background #2A2A2A; 150–200ms"],
        ["FAQ expand", "Inline height reveal", "grid-template-rows / max-height 200–300ms ease"],
        ["FAQ chevron", "+ rotates to ×", "transform rotate; 200ms"],
        ["Input focus", "Border → white", "border-color #fff; 100ms"],
        ["Rail scroll", "Horizontal drag/wheel", "overflow-x:auto; scroll-snap optional"],
    ]
    story.append(dark_table(
        [[Paragraph(c, styles["TableHeader"] if r == 0 else styles["TableCell"]) for c in row]
         for r, row in enumerate(motion_rows)],
        [90, 120, content_w - 210],
    ))
    story.append(Spacer(1, 8))
    story.append(
        Paragraph(
            "Respect <b>prefers-reduced-motion: reduce</b> — disable non-essential transitions.",
            styles["Body"],
        )
    )
    story.append(PageBreak())

    # ===================== RESPONSIVE =====================
    story.append(Paragraph("11. Responsive behavior", styles["H1"]))
    bp = [
        ["Breakpoint", "Width", "Key behavior"],
        ["Mobile S", "<425px", "16px gutters; 1-col cards; hero ~32px; CTA stacks"],
        ["Mobile", "425–576px", "Hero 32–40px; email+CTA vertical stack"],
        ["Tablet", "576–768px", "Feature cards 2×2; rail still horizontal"],
        ["Tablet L", "768–1024px", "Full-width FAQ; gutters ~16–40px"],
        ["Desktop S", "1024–1280px", "4-col features; gutters ~80px"],
        ["Desktop", "1280–1440px", "Standard; gutters up to ~148px; 5-tile rail"],
        ["Large", ">1440px", "Cap content width; grow side gutters"],
    ]
    story.append(dark_table(
        [[Paragraph(c, styles["TableHeader"] if r == 0 else styles["TableCell"]) for c in row]
         for r, row in enumerate(bp)],
        [70, 80, content_w - 150],
    ))
    story.append(Paragraph("Touch targets", styles["H2"]))
    for item in [
        "Primary CTA ≥ 44px tall.",
        "FAQ rows ≥ 72px tall tap area.",
        "Email input 56px tall.",
        "Avoid shrinking Sign In below ~28px height without increasing hit padding.",
    ]:
        story.append(Paragraph(f"•  {item}", styles["BulletText"]))

    story.append(Paragraph("Collapsing rules agents must preserve", styles["H2"]))
    for item in [
        "Hero weight stays heavy at every size; only size scales down.",
        "Horizontal rails stay scrollable — do not squash posters into unreadably small grids.",
        "Email + CTA: inline on desktop, stacked on mobile.",
        "FAQ remains a vertical stack at all breakpoints.",
    ]:
        story.append(Paragraph(f"•  {item}", styles["BulletText"]))
    story.append(PageBreak())

    # ===================== CSS VARS =====================
    story.append(Paragraph("12. CSS custom properties (copy-paste token sheet)", styles["H1"]))
    story.append(
        Paragraph(
            "Paste into a root stylesheet / theme file. Map your existing class names to these "
            "variables instead of scattering hex values.",
            styles["Body"],
        )
    )
    story.append(CodeBlock(
        ":root {\n"
        "  /* Color */\n"
        "  --nf-canvas: #000000;\n"
        "  --nf-surface-deep: #161616;\n"
        "  --nf-surface-card: #232323;\n"
        "  --nf-surface-input: #2D2D2D;\n"
        "  --nf-red: #E50914;\n"
        "  --nf-red-hover: #C11119;\n"
        "  --nf-red-active: #B20710;\n"
        "  --nf-ink: #FFFFFF;\n"
        "  --nf-ink-soft: #B3B3B3;\n"
        "  --nf-ink-muted: #808080;\n"
        "  --nf-hairline: #414141;\n"
        "  --nf-border: #333333;\n"
        "  --nf-overlay: rgba(0, 0, 0, 0.64);\n"
        "  --nf-grad-navy: #192247;\n"
        "  --nf-grad-wine: #210E17;\n"
        "  --nf-grad-burgundy: #461518;\n"
        "  --nf-grad-oxblood: #6F181D;\n"
        "\n"
        "  /* Type */\n"
        "  --nf-font: \"Helvetica Neue\", \"Segoe UI\", Roboto, Ubuntu, sans-serif;\n"
        "  --nf-fs-hero: clamp(2rem, 4vw, 3.5rem); /* 32–56px */\n"
        "  --nf-fs-section: 1.5rem;  /* 24px */\n"
        "  --nf-fs-body: 1rem;       /* 16px */\n"
        "  --nf-fs-sm: 0.875rem;     /* 14px */\n"
        "  --nf-fs-legal: 0.8125rem; /* 13px */\n"
        "  --nf-fw-hero: 800;\n"
        "  --nf-fw-em: 500;\n"
        "  --nf-fw-body: 400;\n"
        "\n"
        "  /* Shape & space */\n"
        "  --nf-radius: 8px;\n"
        "  --nf-radius-sm: 4px;\n"
        "  --nf-space-sm: 8px;\n"
        "  --nf-space-md: 16px;\n"
        "  --nf-space-lg: 24px;\n"
        "  --nf-space-xl: 64px;\n"
        "  --nf-input-h: 56px;\n"
        "  --nf-gutter: clamp(16px, 8vw, 148px);\n"
        "\n"
        "  /* Motion */\n"
        "  --nf-ease: 150ms ease;\n"
        "}\n"
        "\n"
        "html, body {\n"
        "  background: var(--nf-canvas);\n"
        "  color: var(--nf-ink);\n"
        "  font-family: var(--nf-font);\n"
        "  font-weight: var(--nf-fw-body);\n"
        "  line-height: 1.5;\n"
        "}"
    ))
    story.append(PageBreak())

    # ===================== CHECKLIST =====================
    story.append(Paragraph("13. Agent implementation checklist & guardrails", styles["H1"]))
    story.append(Paragraph("Before editing", styles["H2"]))
    for item in [
        "Identify theme entry points (base CSS, Bootstrap overrides, template blocks).",
        "List interactive forms/buttons that must keep the same name/id/action attributes.",
        "Screenshot current key pages for visual regression comparison.",
    ]:
        story.append(Paragraph(f"•  {item}", styles["BulletText"]))

    story.append(Paragraph("While editing", styles["H2"]))
    for item in [
        "Introduce CSS variables first; then remap components to variables.",
        "Restyle buttons/inputs via classes — do not replace <form> actions or method.",
        "Keep existing heading hierarchy (h1–h6) for accessibility; only change visual CSS.",
        "Ensure focus states remain visible on dark backgrounds.",
        "Maintain color contrast: white text on #232323/#000 passes; muted gray on black may fail for small text — use #B3B3B3+ for readable secondary copy.",
    ]:
        story.append(Paragraph(f"•  {item}", styles["BulletText"]))

    story.append(Paragraph("After editing", styles["H2"]))
    for item in [
        "Click through login, create, edit, delete, search — confirm behavior unchanged.",
        "Check mobile widths 375 / 768 / 1280.",
        "Verify no broken icons/images from background changes (e.g. dark logos on dark bg).",
        "Remove any accidentally added Netflix wordmark assets.",
    ]:
        story.append(Paragraph(f"•  {item}", styles["BulletText"]))

    story.append(Paragraph("Definition of done (visual)", styles["H2"]))
    for item in [
        "Page background is near-black; cards are charcoal; primary actions are #E50914.",
        "Typography uses a single sans stack with heavy hero / regular body contrast.",
        "Corners consistently ~8px; no heavy drop shadows on static cards.",
        "Forms remain fully usable; validation messages readable (prefer soft red/white alerts, not low-contrast gray).",
    ]:
        story.append(Paragraph(f"•  {item}", styles["BulletText"]))
    story.append(PageBreak())

    # ===================== DOS DONTS =====================
    story.append(Paragraph("14. Do's and don'ts", styles["H1"]))
    story.append(Paragraph("Do", styles["H2"]))
    for item in [
        "Reserve #E50914 for primary actions and key brand moments.",
        "Let imagery (or bold content blocks) supply color variety.",
        "Use tone steps (#000 → #161616 → #232323 → #2D2D2D) for hierarchy.",
        "Keep layouts linear and conversion/content focused.",
        "Use 8px radius as the default shape language.",
        "Stack generous vertical section spacing (48–64px).",
    ]:
        story.append(Paragraph(f"•  {item}", styles["BulletText"]))

    story.append(Paragraph("Don't", styles["H2"]))
    for item in [
        "Don't introduce light cream/purple SaaS themes while claiming Netflix aesthetic.",
        "Don't paint large background areas red.",
        "Don't add colorful borders, neon glows, or multi-shadow card stacks.",
        "Don't pill-shape every button (radius 999px).",
        "Don't use gray for primary body text.",
        "Don't ship proprietary Netflix Sans or official logos in a third-party product.",
        "Don't refactor backend logic to “match Netflix” — styling only.",
        "Don't weaken overlays until text on images fails contrast.",
    ]:
        story.append(Paragraph(f"•  {item}", styles["BulletText"]))
    story.append(PageBreak())

    # ===================== MAPPING =====================
    story.append(Paragraph("15. Mapping Netflix aesthetics onto an existing site", styles["H1"]))
    story.append(
        Paragraph(
            "Your application (e.g. an eDiary / EDMS Django site) is not a streaming storefront. "
            "Translate the <b>aesthetic system</b>, not the product IA. Map as follows:",
            styles["Body"],
        )
    )
    map_rows = [
        ["Existing element", "Netflix analog", "Apply"],
        ["App shell / body", "Canvas", "bg #000; text #FFF"],
        ["Navbar", "Top nav", "dark bar; red primary auth/action btn"],
        ["Primary submit", "Get Started CTA", "btn-primary red 8px"],
        ["Secondary actions", "Secondary btn", "#232323 fill"],
        ["Cards / panels", "Feature / FAQ surfaces", "#232323; 8px; no shadow"],
        ["Tables", "Dense dark lists", "deep surface header; hairline #414141"],
        ["Forms", "Email input chrome", "#2D2D2D fields; white labels"],
        ["Alerts success", "—", "keep semantic green; don't force red"],
        ["Alerts error", "Brand red family", "use #E50914 / #C11119 sparingly"],
        ["Hero / landing", "Hero + overlay", "dark overlay + heavy headline"],
        ["Footer", "Footer band", "muted #808080 links"],
        ["Modals", "Elevated surface", "#181818–#232323; optional shadow"],
    ]
    story.append(dark_table(
        [[Paragraph(c, styles["TableHeader"] if r == 0 else styles["TableCell"]) for c in row]
         for r, row in enumerate(map_rows)],
        [110, 110, content_w - 220],
    ))
    story.append(Spacer(1, 10))
    story.append(
        Paragraph(
            "<b>Agent prompt snippet (paste when restyling):</b><br/><br/>"
            "Restyle this site to a Netflix-India-like cinematic dark aesthetic using the token "
            "sheet in Netflix_India_Design_System_Reference.pdf. Use black/charcoal surfaces, "
            "white text, #E50914 for primary CTAs only, 8px radii, no card box-shadows, single "
            "sans fallback stack, heavy display / regular body type. Change CSS and presentational "
            "classes only — do not modify business logic, form actions, models, or routes.",
            styles["Callout"],
        )
    )
    story.append(PageBreak())

    # ===================== APPENDIX =====================
    story.append(Paragraph("Appendix A — Quick token cheat sheet", styles["H1"]))
    cheat = [
        ["Need", "Use"],
        ["Page background", "#000000"],
        ["Card / FAQ / panel", "#232323"],
        ["Input fill", "#2D2D2D"],
        ["Primary button", "bg #E50914 · hover #C11119 · text #FFF · radius 8px"],
        ["Body text", "#FFFFFF · 16px · weight 400"],
        ["Secondary text", "#B3B3B3 or #808080"],
        ["Section title", "24px · weight 500 · #FFF"],
        ["Hero title", "clamp(32px, 4vw, 56px) · weight 800–900"],
        ["Default radius", "8px"],
        ["Section gap", "64px"],
        ["Page gutter", "clamp(16px, 8vw, 148px)"],
        ["Hairline", "1px solid #414141"],
        ["Shadow", "none (prefer tone steps)"],
        ["Font", "Helvetica Neue, Segoe UI, Roboto, Ubuntu, sans-serif"],
        ["Focus", "2px solid #FFF; offset 2px"],
    ]
    story.append(dark_table(
        [[Paragraph(c, styles["TableHeader"] if r == 0 else styles["TableCell"]) for c in row]
         for r, row in enumerate(cheat)],
        [130, content_w - 130],
    ))
    story.append(Spacer(1, 16))
    story.append(Paragraph("Appendix B — Sources & confidence", styles["H2"]))
    story.append(
        Paragraph(
            "Primary live source: Netflix India homepage HTML/CSS (assets.nflxext.com nmhp stylesheet; "
            "inline design tokens). Cross-checked against public design-token writeups derived from "
            "the same marketing surface (color frequency, type scale, radius statistics) and Netflix "
            "brand red guidance (#E50914 / #B20710). Measurements can drift as Netflix ships UI "
            "experiments; prefer tokens and principles over pixel-perfect cloning.",
            styles["Body"],
        )
    )
    story.append(Spacer(1, 12))
    story.append(
        Paragraph(
            "End of reference. Apply visually. Preserve behavior.",
            styles["CoverSub"],
        )
    )

    # Build with dark background via onPage
    doc = SimpleDocTemplate(
        str(OUT_PATH),
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=0.65 * inch,
        bottomMargin=0.55 * inch,
        title="Netflix India Visual Design System Reference",
        author="Design System Extract for AI Agents",
        subject="Implementation-focused UI styling reference for Netflix-like aesthetics",
    )

    def first_page(c, doc_):
        add_page_decorations(c, doc_)

    def later_pages(c, doc_):
        add_page_decorations(c, doc_)

    doc.build(story, onFirstPage=first_page, onLaterPages=later_pages)
    print(f"Wrote {OUT_PATH}")
    return OUT_PATH


if __name__ == "__main__":
    build()
