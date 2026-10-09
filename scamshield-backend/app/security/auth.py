from __future__ import annotations

from datetime import datetime, timezone

from flask import current_app
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity
from sqlalchemy import delete

from ..errors.exceptions import AuthenticationError
from ..extensions import db
from ..models.token_blocklist import TokenBlocklist
from ..models.user import User
from ..utils.timeutil import utcnow


def issue_token(user: User) -> tuple[str, int]:
    token = create_access_token(identity=user.id)
    expires = current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]
    return token, int(expires.total_seconds())


def get_current_user() -> User:
    """Return the authenticated user (call only inside a @jwt_required view)."""
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id) if user_id else None
    if user is None or not user.is_active:
        raise AuthenticationError("Authentication required.")
    return user


def revoke_current_token() -> None:
    claims = get_jwt()
    expires_at = datetime.fromtimestamp(claims["exp"], tz=timezone.utc).replace(tzinfo=None)
    db.session.add(TokenBlocklist(
        jti=claims["jti"], token_type=claims.get("type", "access"),
        user_id=get_jwt_identity(), expires_at=expires_at))
    # opportunistic cleanup of rows whose tokens have expired anyway
    db.session.execute(delete(TokenBlocklist).where(TokenBlocklist.expires_at < utcnow()))
    db.session.commit()
