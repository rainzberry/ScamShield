from __future__ import annotations

from ..extensions import db
from ..utils.ids import new_id
from ..utils.timeutil import utcnow


class GmailConnection(db.Model):
    """Per-user Gmail link state.

    Only mode="demo" is implemented. A real OAuth mode would add encrypted token
    columns here; no Google secrets or tokens are ever stored in this build.
    """
    __tablename__ = "gmail_connections"

    id = db.Column(db.String(36), primary_key=True, default=new_id)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"),
                        nullable=False, unique=True)
    mode = db.Column(db.String(16), nullable=False, default="demo")
    email_address = db.Column(db.String(320))
    status = db.Column(db.String(16), nullable=False, default="connected")
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=utcnow, onupdate=utcnow)

    user = db.relationship("User", back_populates="gmail_connection")
