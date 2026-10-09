"""Gmail integration.

ONLY the clearly-labelled DEMO mode is implemented. Real Gmail OAuth is NOT implemented:
no Google credentials are read or stored and no Gmail API response is ever fabricated.
"""
from __future__ import annotations

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from ..data.demo_gmail import DEMO_ADDRESS, DEMO_LABEL, DEMO_MESSAGES
from ..errors.exceptions import NotImplementedFeatureError, ValidationAppError
from ..extensions import db
from ..models.gmail import GmailConnection
from ..security.auth import get_current_user
from ..utils.timeutil import iso

bp = Blueprint("gmail", __name__, url_prefix="/api/gmail")


def _status(conn) -> dict:
    return {"connected": bool(conn and conn.status == "connected"),
            "mode": conn.mode if conn else None,
            "is_demo": bool(conn and conn.mode == "demo"),
            "email_address": conn.email_address if conn else None,
            "connected_at": iso(conn.created_at) if conn else None,
            "oauth_supported": False,
            "label": DEMO_LABEL if conn and conn.mode == "demo" else None}


@bp.get("/status")
@jwt_required()
def status():
    return jsonify({"success": True, "gmail": _status(get_current_user().gmail_connection)})


@bp.post("/demo/connect")
@jwt_required()
def connect_demo():
    user = get_current_user()
    conn = user.gmail_connection
    if conn is None:
        conn = GmailConnection(user_id=user.id)
        db.session.add(conn)
    conn.mode, conn.status, conn.email_address = "demo", "connected", DEMO_ADDRESS
    db.session.commit()
    return jsonify({"success": True, "gmail": _status(conn)})


@bp.post("/disconnect")
@jwt_required()
def disconnect():
    user = get_current_user()
    if user.gmail_connection is not None:
        db.session.delete(user.gmail_connection)
        db.session.commit()
    return jsonify({"success": True, "gmail": _status(None)})


@bp.get("/messages")
@jwt_required()
def messages():
    conn = get_current_user().gmail_connection
    if conn is None or conn.mode != "demo":
        raise ValidationAppError("Connect Demo Gmail Mode first (POST /api/gmail/demo/connect).",
                                 code="GMAIL_NOT_CONNECTED")
    return jsonify({"success": True, "mode": "demo", "is_demo": True, "label": DEMO_LABEL,
                    "messages": [{**m, "is_demo": True} for m in DEMO_MESSAGES]})


@bp.get("/oauth/start")
@jwt_required()
def oauth_start():
    raise NotImplementedFeatureError(
        "Real Gmail OAuth is not implemented in this build. Use Demo Gmail Mode.")
