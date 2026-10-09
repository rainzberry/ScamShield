from __future__ import annotations

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from ..security.auth import get_current_user
from ..services import scan_service

bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@bp.get("/stats")
@jwt_required()
def stats():
    user = get_current_user()
    return jsonify({"success": True, **scan_service.dashboard_stats(user)})
