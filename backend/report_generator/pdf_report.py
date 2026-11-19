"""PDF report generation for a completed scan."""

import io
import json
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

SEVERITY_COLORS = {
    "critical": colors.HexColor("#dc2626"),
    "high": colors.HexColor("#ea580c"),
    "medium": colors.HexColor("#d97706"),
    "low": colors.HexColor("#2563eb"),
    "informational": colors.HexColor("#64748b"),
}


def _p(text, style):
    clean = escape(str(text or "")).replace("\n", "<br/>")
    return Paragraph(clean[:1400], style)


def build_pdf(scan, vulnerabilities):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=16 * mm,
        title=f"SecureAI Report - {scan.target_host}",
        author="SecureAI",
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleCustom", parent=styles["Title"], fontSize=22, textColor=colors.HexColor("#0f172a"), spaceAfter=6)
    subtitle = ParagraphStyle("Subtitle", parent=styles["Normal"], fontSize=10, textColor=colors.HexColor("#475569"), alignment=TA_CENTER, spaceAfter=14)
    heading = ParagraphStyle("HeadingCustom", parent=styles["Heading2"], fontSize=14, textColor=colors.HexColor("#1d4ed8"), spaceBefore=10, spaceAfter=5)
    body = ParagraphStyle("BodyCustom", parent=styles["BodyText"], fontSize=9.2, leading=13, textColor=colors.HexColor("#1e293b"))
    small = ParagraphStyle("Small", parent=body, fontSize=8.2, leading=11, textColor=colors.HexColor("#475569"))

    story = []
    story.append(Paragraph("SecureAI Security Assessment", title_style))
    story.append(Paragraph("AI-Based Web Vulnerability Detection and Risk Assessment", subtitle))

    summary_rows = [
        ["Scan ID", scan.id],
        ["Target URL", scan.target_url],
        ["Scan date", scan.created_at.strftime("%Y-%m-%d %H:%M UTC") if scan.created_at else "-"],
        ["Scan mode", scan.scan_mode],
        ["Pages scanned", str(scan.pages_scanned)],
        ["Security score", f"{scan.security_score}/100"],
        ["Total findings", str(scan.total_findings)],
    ]
    summary_table = Table(summary_rows, colWidths=[42 * mm, 130 * mm])
    summary_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eff6ff")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(summary_table)
    story.append(Spacer(1, 10))

    dist_rows = [["Severity", "Count"]] + [
        ["Critical", str(scan.critical_count)],
        ["High", str(scan.high_count)],
        ["Medium", str(scan.medium_count)],
        ["Low", str(scan.low_count)],
        ["Informational", str(scan.info_count)],
    ]
    dist_table = Table(dist_rows, colWidths=[45 * mm, 25 * mm])
    dist_style = [
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
    ]
    for index, key in enumerate(["critical", "high", "medium", "low", "informational"], start=1):
        dist_style.append(("TEXTCOLOR", (0, index), (0, index), SEVERITY_COLORS[key]))
    dist_table.setStyle(TableStyle(dist_style))
    story.append(Paragraph("Severity Distribution", heading))
    story.append(dist_table)
    story.append(Spacer(1, 10))
    story.append(
        _p(
            "This report contains passive, non-destructive observations. Potential indicators are clearly separated from "
            "confirmed configuration findings and should be manually verified before remediation claims are made.",
            small,
        )
    )

    story.append(PageBreak())
    story.append(Paragraph("Detailed Findings", heading))
    if not vulnerabilities:
        story.append(_p("No findings were recorded for this scan.", body))

    for index, vuln in enumerate(vulnerabilities, start=1):
        try:
            references = json.loads(vuln.references or "[]")
        except (TypeError, ValueError):
            references = []
        try:
            reasoning = json.loads(vuln.reasoning or "[]")
        except (TypeError, ValueError):
            reasoning = []
        color = SEVERITY_COLORS.get(vuln.severity, colors.HexColor("#64748b"))
        header_table = Table(
            [[f"{index}. {vuln.name}", f"{vuln.severity.upper()} | Score {vuln.risk_score:.1f}"]],
            colWidths=[125 * mm, 47 * mm],
        )
        header_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), color),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.append(header_table)
        story.append(Spacer(1, 4))
        details = [
            ("Category", vuln.category),
            ("Affected URL", vuln.affected_url),
            ("Confidence", f"{vuln.confidence} ({'verified' if vuln.verified else 'potential indicator'})"),
            ("Description", vuln.description),
            ("Potential impact", vuln.impact),
            ("Evidence", vuln.evidence),
            ("In simple terms", vuln.simple_explanation),
            ("Why it is dangerous", vuln.why_dangerous),
            ("Recommended fix", vuln.recommendation),
            ("Secure coding", vuln.secure_coding),
            ("Prevention", vuln.prevention),
            ("References", ", ".join(references) if references else "-"),
            ("Risk reasoning", " ".join(reasoning[:4]) if reasoning else "-"),
        ]
        for label, value in details:
            story.append(_p(f"{label}: {value or '-'}", body))
        story.append(Spacer(1, 12))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
