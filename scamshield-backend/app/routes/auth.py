from __future__ import annotations

from flask import Blueprint, current_app, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from ..errors.exceptions import AuthenticationError, ConflictError
from ..extensions import db, limiter
from ..models.user import DEFAULT_SETTINGS, User
from ..schemas.auth import LoginSchema, RegisterSchema
from ..security.auth import get_current_user, issue_token, revoke_current_token
from ..security.passwords import hash_password, verify_dummy, verify_password
from ..utils.timeutil import utcnow
from ..utils.validation import parse_body

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _auth_limit() -> str:
    return current_app.config["RATELIMIT_AUTH"]


def _token_response(user: User, status: int):
    token, expires_in = issue_token(user)
    return jsonify({"success": True, "access_token": token, "token_type": "Bearer",
                    "expires_in": expires_in, "user": user.to_public()}), status


@bp.post("/register")
@limiter.limit(_auth_limit)
def register():
    data = parse_body(RegisterSchema)
    email = data.email.lower()
    if db.session.execute(select(User.id).where(User.email == email)).first():
        raise ConflictError("An account with this email already exists.", code="EMAIL_IN_USE")
    user = User(email=email, password_hash=hash_password(data.password),
                display_name=data.display_name, settings=dict(DEFAULT_SETTINGS))
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ConflictError("An account with this email already exists.",
                            code="EMAIL_IN_USE") from None
    return _token_response(user, 201)


@bp.post("/login")
@limiter.limit(_auth_limit)
def login():
    data = parse_body(LoginSchema)
    email = data.email.lower()
    user = db.session.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if user is None:
        verify_dummy(data.password)
        raise AuthenticationError("Invalid email or password.", code="INVALID_CREDENTIALS")
    if not verify_password(user.password_hash, data.password) or not user.is_active:
        raise AuthenticationError("Invalid email or password.", code="INVALID_CREDENTIALS")
    user.last_login_at = utcnow()
    db.session.commit()
    return _token_response(user, 200)


@bp.post("/logout")
@jwt_required()
def logout():
    revoke_current_token()
    return jsonify({"success": True, "message": "Logged out."})


@bp.get("/me")
@jwt_required()
def me():
    return jsonify({"success": True, "user": get_current_user().to_public()})
