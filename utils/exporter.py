import io
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle


def generate_markdown_report(result: dict) -> str:
    """Generate a clean GitHub-flavored Markdown report from meeting results."""
    title = result.get("title", "AI Meeting Assistant Report")
    timestamp = result.get("timestamp", "N/A")
    source = result.get("source", "N/A")
    language = result.get("language", "English")
    summary = result.get("summary", "No summary available.")
    action_items = result.get("action_items", "None")
    key_decisions = result.get("key_decisions", "None")
    open_questions = result.get("open_questions", "None")
    topics = result.get("timestamped_topics", "")
    transcript = result.get("transcript", "")

    md = f"""# 🎬 {title}

**Generated on**: {timestamp}  
**Source**: `{source}` | **Language**: `{language}`  

---

## 📋 Executive Summary
{summary}

---

## 📌 Timestamped Agenda & Key Moments
{topics if topics else "Not specified."}

---

## ✅ Action Items
{action_items}

---

## 🔑 Key Decisions
{key_decisions}

---

## ❓ Open Questions & Follow-ups
{open_questions}

---

## 📝 Full Transcript
```text
{transcript}
```
"""
    return md


def generate_pdf_report(result: dict) -> bytes:
    """Generate a beautifully formatted PDF report byte buffer using ReportLab."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    # Custom Color Palette
    PRIMARY = colors.HexColor("#7c3aed")
    SECONDARY = colors.HexColor("#06b6d4")
    TEXT_DARK = colors.HexColor("#1e1e2e")
    BG_LIGHT = colors.HexColor("#f8f9fa")

    # Custom Paragraph Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=PRIMARY,
        alignment=0,
        spaceAfter=6
    )

    meta_style = ParagraphStyle(
        'MetaStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=15
    )

    h2_style = ParagraphStyle(
        'H2Style',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=PRIMARY,
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=TEXT_DARK,
        spaceAfter=8
    )

    story = []

    # Title
    doc_title = result.get("title", "AI Meeting Assistant Report")
    story.append(Paragraph(doc_title, title_style))

    # Metadata Banner
    ts = result.get("timestamp", "N/A")
    src = result.get("source", "N/A")
    lang = result.get("language", "English")
    story.append(Paragraph(f"<b>Date:</b> {ts} &nbsp;|&nbsp; <b>Source:</b> {src} &nbsp;|&nbsp; <b>Language:</b> {lang}", meta_style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=0, spaceAfter=15))

    # Executive Summary
    story.append(Paragraph("📋 Executive Summary", h2_style))
    summary_text = result.get("summary", "No summary available.").replace("\n", "<br/>")
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 10))

    # Key Moments
    topics = result.get("timestamped_topics")
    if topics:
        story.append(Paragraph("📌 Timestamped Agenda & Key Moments", h2_style))
        story.append(Paragraph(topics.replace("\n", "<br/>"), body_style))
        story.append(Spacer(1, 10))

    # Action Items & Key Decisions Table
    story.append(Paragraph("✅ Action Items & Key Decisions", h2_style))
    
    actions = result.get("action_items", "None").replace("\n", "<br/>")
    decisions = result.get("key_decisions", "None").replace("\n", "<br/>")

    data = [
        [Paragraph("<b>Action Items</b>", body_style), Paragraph("<b>Key Decisions</b>", body_style)],
        [Paragraph(actions, body_style), Paragraph(decisions, body_style)]
    ]

    t = Table(data, colWidths=[260, 260])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BG_LIGHT),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))

    # Open Questions
    story.append(Paragraph("❓ Open Questions", h2_style))
    questions = result.get("open_questions", "None").replace("\n", "<br/>")
    story.append(Paragraph(questions, body_style))
    story.append(Spacer(1, 15))

    # Transcript Preview
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceBefore=10, spaceAfter=10))
    story.append(Paragraph("📝 Full Transcript", h2_style))
    transcript = result.get("transcript", "")
    if len(transcript) > 2000:
        transcript = transcript[:2000] + "\n\n...[Truncated for PDF export]..."
    story.append(Paragraph(transcript.replace("\n", "<br/>"), body_style))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
