from __future__ import annotations

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import text

from .. import __version__
from ..extensions import db
from ..services.ml_adapter import get_ml_engine

bp = Blueprint("system", __name__, url_prefix="/api")


@bp.get("/health")
def health():
    try:
        db.session.execute(text("SELECT 1"))
        database = "ok"
    except Exception:
        database = "error"
    ml = get_ml_engine().model_info()
    status = "ok" if database == "ok" and ml["available"] else "degraded"
    return jsonify({"success": True, "status": status, "version": __version__,
                    "database": database, "ml": {"available": ml["available"]}})


@bp.get("/model/info")
@jwt_required()
def model_info():
    return jsonify({"success": True, "model": get_ml_engine().model_info()})
