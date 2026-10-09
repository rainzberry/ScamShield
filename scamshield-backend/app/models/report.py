from __future__ import annotations

from ..extensions import db
from ..utils.ids import new_id
from ..utils.timeutil import utcnow


class Report(db.Model):
    """Audit record of a generated report (one row per scan + format)."""
    __tablename__ = "reports"
    __table_args__ = (db.UniqueConstraint("scan_id", "report_format", name="uq_report_scan_fmt"),)

    id = db.Column(db.String(36), primary_key=True, default=new_id)
    scan_id = db.Column(db.String(36), db.ForeignKey("scans.id", ondelete="CASCADE"),
                        nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"),
                        nullable=False, index=True)
    report_format = db.Column(db.String(8), nullable=False, default="json")
    download_count = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    generated_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    scan = db.relationship("Scan", back_populates="reports")
