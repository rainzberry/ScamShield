from __future__ import annotations

from ..extensions import db
from ..utils.timeutil import utcnow


class TokenBlocklist(db.Model):
    """Revoked JWTs (logout). Rows are purged after the token's natural expiry."""
    __tablename__ = "token_blocklist"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    jti = db.Column(db.String(64), unique=True, nullable=False, index=True)
    token_type = db.Column(db.String(16), nullable=False, default="access")
    user_id = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
