from __future__ import annotations

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from ..extensions import db
from ..models.user import DEFAULT_SETTINGS
from ..schemas.settings import SettingsUpdateSchema
from ..security.auth import get_current_user
from ..utils.validation import parse_body

bp = Blueprint("settings", __name__, url_prefix="/api/settings")


def _view(user) -> dict:
    return {"display_name": user.display_name, **DEFAULT_SETTINGS, **(user.settings or {})}


@bp.get("")
@jwt_required()
def get_settings():
    return jsonify({"success": True, "settings": _view(get_current_user())})


@bp.put("")
@jwt_required()
def update_settings():
    user = get_current_user()
    data = parse_body(SettingsUpdateSchema)
    merged = {**DEFAULT_SETTINGS, **(user.settings or {})}
    if data.theme is not None:
        merged["theme"] = data.theme
    if data.email_notifications is not None:
        merged["email_notifications"] = data.email_notifications
    user.settings = merged                     # assign a new dict so SQLAlchemy sees the change
    if data.display_name is not None:
        user.display_name = data.display_name.strip() or None
    db.session.commit()
    return jsonify({"success": True, "settings": _view(user)})
