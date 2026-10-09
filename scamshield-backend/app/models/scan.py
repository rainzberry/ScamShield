from __future__ import annotations

from ..extensions import db
from ..utils.ids import new_id
from ..utils.timeutil import utcnow


class Scan(db.Model):
    """One submitted item (email / text / url / qr). Always owned by exactly one user."""
    __tablename__ = "scans"
    __table_args__ = (db.Index("ix_scans_user_created", "user_id", "created_at"),)

    id = db.Column(db.String(36), primary_key=True, default=new_id)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"),
                        nullable=False, index=True)
    scan_type = db.Column(db.String(16), nullable=False, index=True)
    input_summary = db.Column(db.String(300), nullable=False, default="")
    input_data = db.Column(db.JSON, nullable=False, default=dict)   # what the user submitted
    details = db.Column(db.JSON, nullable=False, default=dict)      # e.g. decoded QR info
    status = db.Column(db.String(16), nullable=False, default="completed")
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow, index=True)

    user = db.relationship("User", back_populates="scans")
    result = db.relationship("AnalysisResult", back_populates="scan", uselist=False,
                             cascade="all, delete-orphan")
    indicators = db.relationship("ThreatIndicator", back_populates="scan",
                                 cascade="all, delete-orphan",
                                 order_by="ThreatIndicator.position")
    reports = db.relationship("Report", back_populates="scan", cascade="all, delete-orphan")


class AnalysisResult(db.Model):
    __tablename__ = "analysis_results"
    __table_args__ = (
        db.CheckConstraint("risk_score >= 0 AND risk_score <= 100", name="ck_risk_range"),
        db.CheckConstraint("confidence >= 0 AND confidence <= 1", name="ck_confidence_range"),
    )

    id = db.Column(db.String(36), primary_key=True, default=new_id)
    scan_id = db.Column(db.String(36), db.ForeignKey("scans.id", ondelete="CASCADE"),
                        nullable=False, unique=True)
    classification = db.Column(db.String(16), nullable=False, index=True)
    risk_score = db.Column(db.Integer, nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    severity = db.Column(db.String(10), nullable=False, index=True)
    explanation = db.Column(db.JSON, nullable=False, default=dict)
    recommendation = db.Column(db.Text, nullable=False, default="")
    model_version = db.Column(db.String(64), nullable=False, default="unknown")
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    scan = db.relationship("Scan", back_populates="result")


class ThreatIndicator(db.Model):
    __tablename__ = "threat_indicators"

    id = db.Column(db.String(36), primary_key=True, default=new_id)
    scan_id = db.Column(db.String(36), db.ForeignKey("scans.id", ondelete="CASCADE"),
                        nullable=False, index=True)
    position = db.Column(db.Integer, nullable=False, default=0)
    indicator_type = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(500), nullable=False, default="")
    severity = db.Column(db.String(10), nullable=False, default="INFO")
    weight = db.Column(db.Float)
    evidence = db.Column(db.Text)
    source = db.Column(db.String(16), nullable=False, default="ml")  # "ml" | "backend"

    scan = db.relationship("Scan", back_populates="indicators")
