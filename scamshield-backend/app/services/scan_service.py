"""History queries and dashboard statistics. EVERY query is scoped to the current user."""
from __future__ import annotations

from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import contains_eager, selectinload

from ..errors.exceptions import NotFoundError
from ..extensions import db
from ..models.scan import AnalysisResult, Scan
from ..models.user import User
from ..utils.timeutil import utcnow
from .serializers import serialize_scan


def get_user_scan(user: User, scan_id: str) -> Scan:
    """404 (not 403) for other users' scans so IDs cannot be probed."""
    if not scan_id or len(scan_id) > 64:
        raise NotFoundError("Scan not found.")
    scan = db.session.execute(
        select(Scan).where(Scan.id == scan_id, Scan.user_id == user.id)
        .options(selectinload(Scan.indicators), selectinload(Scan.result))
    ).scalar_one_or_none()
    if scan is None:
        raise NotFoundError("Scan not found.")
    return scan


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def list_scans(user: User, q) -> tuple[list[dict], dict]:
    filters = [Scan.user_id == user.id]
    if q.classification:
        filters.append(AnalysisResult.classification == q.classification)
    if q.scan_type:
        filters.append(Scan.scan_type == q.scan_type)
    if q.q:
        filters.append(Scan.input_summary.ilike(f"%{_escape_like(q.q)}%", escape="\\"))

    total = db.session.scalar(
        select(func.count()).select_from(Scan).join(Scan.result).where(*filters)) or 0

    sort_col = AnalysisResult.risk_score if q.sort == "risk_score" else Scan.created_at
    sort_col = sort_col.asc() if q.order == "asc" else sort_col.desc()
    tiebreak = Scan.id.asc() if q.order == "asc" else Scan.id.desc()
    rows = db.session.execute(
        select(Scan).join(Scan.result).where(*filters)
        .options(contains_eager(Scan.result), selectinload(Scan.indicators))
        .order_by(sort_col, tiebreak).limit(q.per_page).offset((q.page - 1) * q.per_page)
    ).scalars().unique().all()

    pages = (total + q.per_page - 1) // q.per_page
    pagination = {"page": q.page, "per_page": q.per_page, "total": total, "pages": pages,
                  "has_next": q.page < pages, "has_prev": q.page > 1}
    return [serialize_scan(s, detail=False) for s in rows], pagination


def dashboard_stats(user: User, recent: int = 5, trend_days: int = 14) -> dict:
    owned = (Scan.user_id == user.id)
    by_class = dict(db.session.execute(
        select(AnalysisResult.classification, func.count()).select_from(AnalysisResult)
        .join(Scan, Scan.id == AnalysisResult.scan_id).where(owned)
        .group_by(AnalysisResult.classification)).all())
    total = sum(by_class.values())
    avg = db.session.scalar(
        select(func.avg(AnalysisResult.risk_score)).select_from(AnalysisResult)
        .join(Scan, Scan.id == AnalysisResult.scan_id).where(owned))
    by_type = dict(db.session.execute(
        select(Scan.scan_type, func.count()).where(owned).group_by(Scan.scan_type)).all())
    by_severity = dict(db.session.execute(
        select(AnalysisResult.severity, func.count()).select_from(AnalysisResult)
        .join(Scan, Scan.id == AnalysisResult.scan_id).where(owned)
        .group_by(AnalysisResult.severity)).all())

    since = (utcnow() - timedelta(days=trend_days - 1)).replace(hour=0, minute=0, second=0, microsecond=0)
    day = func.date(Scan.created_at)
    trend = [{"date": str(d), "count": c, "average_risk": round(float(a or 0), 1)}
             for d, c, a in db.session.execute(
                 select(day, func.count(), func.avg(AnalysisResult.risk_score))
                 .select_from(Scan).join(AnalysisResult, Scan.id == AnalysisResult.scan_id)
                 .where(owned, Scan.created_at >= since).group_by(day).order_by(day)).all()]

    recent_rows = db.session.execute(
        select(Scan).join(Scan.result).where(owned)
        .options(contains_eager(Scan.result), selectinload(Scan.indicators))
        .order_by(Scan.created_at.desc(), Scan.id.desc()).limit(recent)
    ).scalars().unique().all()

    return {
        "total_scans": total,
        "safe": by_class.get("safe", 0),
        "spam": by_class.get("spam", 0),
        "phishing": by_class.get("phishing", 0),
        "malicious": by_class.get("malicious", 0),
        "average_risk": round(float(avg), 1) if avg is not None else 0.0,
        "by_scan_type": {t: by_type.get(t, 0) for t in ("email", "text", "url", "qr")},
        "by_severity": {s: by_severity.get(s, 0) for s in ("LOW", "MEDIUM", "HIGH", "CRITICAL")},
        "trend": trend,
        "recent_scans": [serialize_scan(s, detail=False) for s in recent_rows],
    }
