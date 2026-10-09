from __future__ import annotations

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from ..schemas.scans import ScanListQuery
from ..security.auth import get_current_user
from ..services import scan_service
from ..services.serializers import serialize_scan
from ..utils.validation import parse_query

bp = Blueprint("scans", __name__, url_prefix="/api/scans")


@bp.get("")
@jwt_required()
def list_scans():
    user = get_current_user()
    items, pagination = scan_service.list_scans(user, parse_query(ScanListQuery))
    return jsonify({"success": True, "scans": items, "pagination": pagination})


@bp.get("/<scan_id>")
@jwt_required()
def get_scan(scan_id: str):
    user = get_current_user()
    scan = scan_service.get_user_scan(user, scan_id)
    return jsonify({"success": True, "scan": serialize_scan(scan, detail=True)})
