"""Detailed per-scan reports: JSON (default) and PDF (ReportLab)."""
from __future__ import annotations

import io
import re
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models.report import Report
from ..models.scan import Scan
from ..utils.timeutil import iso, utcnow
from .serializers import serialize_indicator

DISCLAIMER = ("Automated analysis. Risk scores estimate likelihood and are not proof of "
              "malicious intent. Verify through official channels when in doubt.")
_CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def record_generation(scan: Scan, fmt: str) -> Report:
    def _fetch():
        return db.session.execute(select(Report).where(
            Report.scan_id == scan.id, Report.report_format == fmt)).scalar_one_or_none()

    report = _fetch()
    if report is None:
        report = Report(scan_id=scan.id, user_id=scan.user_id, report_format=fmt, download_count=0)
        db.session.add(report)
    report.download_count = (report.download_count or 0) + 1
    report.generated_at = utcnow()
    try:
        db.session.commit()
    except IntegrityError:           # concurrent first-time generation
        db.session.rollback()
        report = _fetch()
    return report


def build_report(scan: Scan, report: Report) -> dict:
    r = scan.result
    indicators = [serialize_indicator(i) for i in scan.indicators]
    return {
        "report_id": report.id,
        "generated_at": iso(report.generated_at),
        "metadata": {"scan_id": scan.id, "scan_type": scan.scan_type,
                     "created_at": iso(scan.created_at), "input_summary": scan.input_summary,
                     "details": scan.details},
        "classification": r.classification,
        "risk_score": r.risk_score,
        "confidence": r.confidence,
        "severity": r.severity,
        "indicators": indicators,
        "evidence": [{"indicator": i["type"], "evidence": i["evidence"]}
                     for i in indicators if i["evidence"]],
        "explanation": r.explanation,
        "recommendation": r.recommendation,
        "model_version": r.model_version,
        "timestamp": iso(scan.created_at),
        "disclaimer": DISCLAIMER,
    }


def _p(text, style, limit: int = 1200) -> Paragraph:
    clean = _CTRL.sub("", str(text if text is not None else ""))[:limit]   # truncate BEFORE escaping
    return Paragraph(escape(clean).replace("\n", "<br/>"), style)


def build_pdf(report: dict) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=16 * mm, bottomMargin=16 * mm,
                            title="ScamShield AI Report", author="ScamShield AI")
    styles = getSampleStyleSheet()
    body = ParagraphStyle("body", parent=styles["BodyText"], fontSize=9.5, leading=13)
    small = ParagraphStyle("small", parent=body, fontSize=8, leading=10, textColor=colors.grey)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], spaceBefore=10, spaceAfter=4)
    meta = report["metadata"]

    story = [Paragraph("ScamShield AI - Threat Analysis Report", styles["Title"]),
             _p(f"Report {report['report_id']} - generated {report['generated_at']}", small),
             Spacer(1, 6)]

    summary_rows = [
        ["Scan ID", meta["scan_id"]], ["Scan type", meta["scan_type"]],
        ["Classification", report["classification"].upper()],
        ["Risk score", f"{report['risk_score']} / 100"],
        ["Severity", report["severity"]],
        ["Confidence", f"{report['confidence']:.2%}"],
        ["Model version", report["model_version"]], ["Scanned at", report["timestamp"]],
    ]
    table = Table([[_p(k, body), _p(v, body)] for k, v in summary_rows], colWidths=[40 * mm, 130 * mm])
    table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                               ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
                               ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story += [table, Paragraph("Input", h2), _p(meta["input_summary"], body)]

    story.append(Paragraph("Indicators", h2))
    if report["indicators"]:
        rows = [[_p("Severity", body), _p("Indicator", body), _p("Evidence", body)]]
        for ind in report["indicators"][:50]:
            rows.append([_p(ind["severity"], body, 20),
                         _p(f"{ind['type']}: {ind['description']}", body, 500),
                         _p(ind["evidence"] or "-", body, 400)])
        ind_table = Table(rows, colWidths=[22 * mm, 90 * mm, 58 * mm], repeatRows=1)
        ind_table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                                       ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                                       ("VALIGN", (0, 0), (-1, -1), "TOP")]))
        story.append(ind_table)
    else:
        story.append(_p("No indicators were recorded.", body))

    story.append(Paragraph("Explanation", h2))
    explanation = report["explanation"] or {}
    summary_text = explanation.get("summary") if isinstance(explanation, dict) else None
    story.append(_p(summary_text or "See indicators above.", body, 3000))
    story += [Paragraph("Recommendation", h2), _p(report["recommendation"], body, 3000),
              Spacer(1, 10), _p(DISCLAIMER, small)]
    doc.build(story)
    return buf.getvalue()
