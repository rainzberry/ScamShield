from __future__ import annotations

from ..extensions import db
from ..utils.ids import new_id
from ..utils.timeutil import iso, utcnow

DEFAULT_SETTINGS = {"theme": "system", "email_notifications": False}


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=new_id)
    email = db.Column(db.String(320), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)  # never plaintext
    display_name = db.Column(db.String(80))
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    settings = db.Column(db.JSON, nullable=False, default=lambda: dict(DEFAULT_SETTINGS))
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    last_login_at = db.Column(db.DateTime)

    scans = db.relationship("Scan", back_populates="user", cascade="all, delete-orphan")
    gmail_connection = db.relationship(
        "GmailConnection", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def to_public(self) -> dict:
        """Safe representation: never includes the password hash."""
        return {
            "id": self.id,
            "email": self.email,
            "display_name": self.display_name,
            "settings": {**DEFAULT_SETTINGS, **(self.settings or {})},
            "created_at": iso(self.created_at),
        }
