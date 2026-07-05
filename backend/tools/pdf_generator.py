import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable
)
from reportlab.lib.enums import TA_CENTER
import re

def markdown_to_pdf(topic: str, markdown_text: str, citations: list[dict]) -> bytes:
    """Convert a markdown report + citations into a PDF and return bytes."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=22,
        textColor=colors.HexColor("#6C63FF"),
        spaceAfter=12,
        alignment=TA_CENTER,
    )
    h1_style = ParagraphStyle(
        "CustomH1",
        parent=styles["Heading1"],
        fontSize=16,
        textColor=colors.HexColor("#6C63FF"),
        spaceBefore=16,
        spaceAfter=6,
    )
    h2_style = ParagraphStyle(
        "CustomH2",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=colors.HexColor("#4A47A3"),
        spaceBefore=12,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["Normal"],
        fontSize=10,
        leading=16,
        spaceAfter=6,
    )
    citation_style = ParagraphStyle(
        "Citation",
        parent=styles["Normal"],
        fontSize=9,
        leading=14,
        textColor=colors.HexColor("#555555"),
        spaceAfter=4,
    )

    story = []

    # Title
    story.append(Paragraph(f"ResearchLab AI Report", title_style))
    story.append(Paragraph(f"<b>Topic:</b> {topic}", body_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#6C63FF")))
    story.append(Spacer(1, 12))

    # Parse markdown lines
    for line in markdown_text.split("\n"):
        line = line.strip()
        if not line:
            story.append(Spacer(1, 6))
        elif line.startswith("## "):
            story.append(Paragraph(line[3:], h1_style))
        elif line.startswith("### "):
            story.append(Paragraph(line[4:], h2_style))
        elif line.startswith("- ") or line.startswith("* "):
            story.append(Paragraph(f"• {line[2:]}", body_style))
        elif line.startswith("**") and line.endswith("**"):
            story.append(Paragraph(f"<b>{line[2:-2]}</b>", body_style))
        else:
            # Inline bold
            line = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", line)
            story.append(Paragraph(line, body_style))

    # Citations section
    if citations:
        story.append(Spacer(1, 16))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
        story.append(Paragraph("References", h1_style))
        for i, c in enumerate(citations, 1):
            story.append(Paragraph(
                f"[{i}] <b>{c.get('title','')}</b><br/>"
                f"<i>{c.get('url','')}</i><br/>"
                f"{c.get('snippet','')}",
                citation_style
            ))
            story.append(Spacer(1, 4))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
