"""PDF export for Rulees documents.

Renders the markdown-like content produced by
``app.modules.documents.service.render_document_content`` /
``render_markdown_export`` (``# title``, ``## heading``, plain-text
paragraphs and ``- `` bullets) into a branded, paginated PDF using
reportlab's platypus layout engine.

Replaces a previous hand-rolled PDF 1.4 byte writer that silently truncated
content after 38 visible lines instead of paginating.
"""

from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate

# Official Rulees brand colors (see frontend/src/App.css: --brand-deep / --brand-soft).
BRAND_DEEP = colors.HexColor("#375d61")
BRAND_SOFT = colors.HexColor("#c8e3e6")
TEXT_COLOR = colors.HexColor("#1f2937")
MUTED_COLOR = colors.HexColor("#4b5563")

PAGE_SIZE = A4
MARGIN = 20 * mm
HEADER_HEIGHT = 22 * mm
FOOTER_HEIGHT = 14 * mm

_STYLE_H1 = ParagraphStyle(
    "RuleesH1",
    fontName="Helvetica-Bold",
    fontSize=16,
    leading=20,
    textColor=BRAND_DEEP,
    spaceBefore=2,
    spaceAfter=10,
)
_STYLE_H2 = ParagraphStyle(
    "RuleesH2",
    fontName="Helvetica-Bold",
    fontSize=13,
    leading=16,
    textColor=BRAND_DEEP,
    spaceBefore=10,
    spaceAfter=6,
)
_STYLE_BODY = ParagraphStyle(
    "RuleesBody",
    fontName="Helvetica",
    fontSize=10.5,
    leading=14,
    textColor=TEXT_COLOR,
    spaceAfter=6,
)
_STYLE_BULLET = ParagraphStyle(
    "RuleesBullet",
    parent=_STYLE_BODY,
    leftIndent=14,
    firstLineIndent=-14,
    spaceAfter=3,
)


def _parse_blocks(content: str) -> list[tuple[str, str]]:
    """Split rendered document markdown into ``(kind, text)`` blocks.

    ``kind`` is one of ``"h1"``, ``"h2"``, ``"bullet"``, ``"p"``. Consecutive
    non-empty plain-text lines are merged into a single paragraph block;
    blank lines close the current paragraph.
    """
    blocks: list[tuple[str, str]] = []
    paragraph_lines: list[str] = []

    def flush_paragraph() -> None:
        if paragraph_lines:
            blocks.append(("p", " ".join(paragraph_lines)))
            paragraph_lines.clear()

    for raw_line in content.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            flush_paragraph()
            continue
        if stripped.startswith("## "):
            flush_paragraph()
            blocks.append(("h2", stripped[3:].strip()))
        elif stripped.startswith("# "):
            flush_paragraph()
            blocks.append(("h1", stripped[2:].strip()))
        elif stripped.startswith("- "):
            flush_paragraph()
            blocks.append(("bullet", stripped[2:].strip()))
        else:
            paragraph_lines.append(stripped)
    flush_paragraph()
    return blocks


def _build_story(content: str) -> list:
    story: list = []
    for kind, text in _parse_blocks(content):
        safe_text = escape(text)
        if kind == "h1":
            story.append(Paragraph(safe_text, _STYLE_H1))
        elif kind == "h2":
            story.append(Paragraph(safe_text, _STYLE_H2))
        elif kind == "bullet":
            story.append(Paragraph(f"• {safe_text}", _STYLE_BULLET))
        else:
            story.append(Paragraph(safe_text, _STYLE_BODY))
    if not story:
        story.append(Paragraph("", _STYLE_BODY))
    return story


class _NumberedCanvas(Canvas):
    """Canvas that draws the branded header/footer on every page.

    Uses the standard two-pass technique: ``showPage`` buffers each page's
    drawing state instead of emitting it immediately, and ``save`` replays
    every buffered page once the final page count is known so the footer
    can render "Pagina X de Y".
    """

    def __init__(self, *args, doc_title: str = "", **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states: list[dict] = []
        self._doc_title = doc_title

    def showPage(self) -> None:
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self) -> None:
        total_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_header_footer(total_pages)
            super().showPage()
        super().save()

    def _draw_header_footer(self, total_pages: int) -> None:
        width, height = PAGE_SIZE

        # Header band: brand-deep banner with a brand-soft accent stripe.
        self.setFillColor(BRAND_DEEP)
        self.rect(0, height - HEADER_HEIGHT, width, HEADER_HEIGHT, fill=1, stroke=0)
        self.setFillColor(BRAND_SOFT)
        self.rect(0, height - HEADER_HEIGHT - 2, width, 2, fill=1, stroke=0)

        self.setFillColor(colors.white)
        self.setFont("Helvetica-Bold", 14)
        self.drawString(MARGIN, height - 13 * mm, "Rulees")

        self.setFont("Helvetica", 9)
        self.drawString(MARGIN, height - 19 * mm, self._doc_title[:96])

        # Footer: brand-soft divider, page count and generation timestamp.
        self.setStrokeColor(BRAND_SOFT)
        self.setLineWidth(0.75)
        self.line(MARGIN, FOOTER_HEIGHT, width - MARGIN, FOOTER_HEIGHT)

        self.setFillColor(MUTED_COLOR)
        self.setFont("Helvetica", 8)
        page_number = self.getPageNumber()
        self.drawString(MARGIN, FOOTER_HEIGHT - 10, f"Pagina {page_number} de {total_pages}")

        generated_at = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")
        self.drawRightString(width - MARGIN, FOOTER_HEIGHT - 10, f"Gerado em {generated_at}")


def build_simple_pdf(title: str, content: str) -> bytes:
    """Render ``content`` (Rulees document markdown) as a branded PDF.

    Uses ``reportlab.platypus.SimpleDocTemplate`` for real, automatic
    pagination -- long documents flow across as many pages as needed
    instead of being silently truncated.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=PAGE_SIZE,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=HEADER_HEIGHT + 8 * mm,
        bottomMargin=FOOTER_HEIGHT + 6 * mm,
        title=title,
    )
    story = _build_story(content)

    def _canvasmaker(*args, **kwargs):
        return _NumberedCanvas(*args, doc_title=title, **kwargs)

    doc.build(story, canvasmaker=_canvasmaker)
    return buffer.getvalue()
