from __future__ import annotations

from flask import Blueprint, Response, jsonify
from flask_jwt_extended import jwt_required

from ..schemas.scans import ReportQuery
from ..security.auth import get_current_user
from ..services import report_service, scan_service
from ..utils.validation import parse_query

bp = Blueprint("reports", __name__, url_prefix="/api/reports")


@bp.get("/<scan_id>")
@jwt_required()
def get_report(scan_id: str):
    user = get_current_user()
    fmt = parse_query(ReportQuery).format
    scan = scan_service.get_user_scan(user, scan_id)   # 404 for other users' scans
    record = report_service.record_generation(scan, fmt)
    report = report_service.build_report(scan, record)
    if fmt == "pdf":
        pdf = report_service.build_pdf(report)
        return Response(pdf, mimetype="application/pdf", headers={
            "Content-Disposition": f'attachment; filename="scamshield-report-{scan.id}.pdf"'})
    return jsonify({"success": True, "report": report})
