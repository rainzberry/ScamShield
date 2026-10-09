from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required

from ..errors.exceptions import ValidationAppError
from ..extensions import limiter
from ..schemas.analyze import EmailAnalyzeSchema, TextAnalyzeSchema, UrlAnalyzeSchema
from ..security.auth import get_current_user
from ..security.uploads import validate_image_upload
from ..services import analysis_service
from ..services.serializers import serialize_scan
from ..utils.validation import parse_body

bp = Blueprint("analyze", __name__, url_prefix="/api/analyze")


def _analyze_limit() -> str:
    return current_app.config["RATELIMIT_ANALYZE"]


def _scan_response(scan):
    return jsonify({"success": True, "scan": serialize_scan(scan, detail=True)}), 201


@bp.post("/email")
@limiter.limit(_analyze_limit)
@jwt_required()
def analyze_email():
    user = get_current_user()
    return _scan_response(analysis_service.analyze_email(user, parse_body(EmailAnalyzeSchema)))


@bp.post("/text")
@limiter.limit(_analyze_limit)
@jwt_required()
def analyze_text():
    user = get_current_user()
    return _scan_response(analysis_service.analyze_text(user, parse_body(TextAnalyzeSchema)))


@bp.post("/url")
@limiter.limit(_analyze_limit)
@jwt_required()
def analyze_url():
    user = get_current_user()
    return _scan_response(analysis_service.analyze_url(user, parse_body(UrlAnalyzeSchema)))


@bp.post("/qr")
@limiter.limit(_analyze_limit)
@jwt_required()
def analyze_qr():
    user = get_current_user()
    upload = request.files.get("file") or request.files.get("image")
    if upload is None:
        raise ValidationAppError(
            "No image uploaded. Send multipart/form-data with an image in the 'file' field.")
    cfg = current_app.config
    image = validate_image_upload(
        upload, max_bytes=cfg["QR_MAX_UPLOAD_BYTES"],
        allowed_extensions=cfg["QR_ALLOWED_EXTENSIONS"],
        allowed_mime_types=cfg["QR_ALLOWED_MIME_TYPES"], max_pixels=cfg["QR_MAX_PIXELS"])
    return _scan_response(analysis_service.analyze_qr(user, image))
