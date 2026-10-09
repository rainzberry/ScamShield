"""Centralised error handling. No stack traces are ever returned to clients."""
from __future__ import annotations

import logging

from flask import g, jsonify
from werkzeug.exceptions import HTTPException

from ..extensions import db, jwt
from .exceptions import AppError

log = logging.getLogger(__name__)

_HTTP_ERRORS = {
    400: ("BAD_REQUEST", "The request could not be processed."),
    401: ("AUTHENTICATION_ERROR", "Authentication required."),
    403: ("FORBIDDEN", "You do not have permission to perform this action."),
    404: ("NOT_FOUND", "Resource not found."),
    405: ("METHOD_NOT_ALLOWED", "Method not allowed for this endpoint."),
    413: ("FILE_TOO_LARGE", "The request body is too large."),
    415: ("UNSUPPORTED_MEDIA_TYPE", "Unsupported media type."),
    429: ("RATE_LIMITED", "Too many requests. Please slow down."),
}


def error_response(code: str, message: str, status: int, details=None):
    body = {"success": False, "error": {"code": code, "message": message}}
    if details:
        body["error"]["details"] = details
    return jsonify(body), status


def register_error_handlers(app) -> None:
    @app.errorhandler(AppError)
    def _app_error(exc: AppError):
        if exc.status_code >= 500:
            log.error("AppError %s (%s) [request=%s]", exc.code, exc.message,
                      getattr(g, "request_id", "-"))
        return error_response(exc.code, exc.message, exc.status_code, exc.details)

    @app.errorhandler(HTTPException)
    def _http_error(exc: HTTPException):
        status = exc.code or 500
        code, message = _HTTP_ERRORS.get(status, ("HTTP_ERROR", "The request failed."))
        return error_response(code, message, status)

    from flask_limiter import RateLimitExceeded

    @app.errorhandler(RateLimitExceeded)
    def _rate_limited(_exc):
        # explicit handler so the JSON envelope is used even if Flask-Limiter installs its own
        code, message = _HTTP_ERRORS[429]
        return error_response(code, message, 429)

    @app.errorhandler(Exception)
    def _unhandled(exc: Exception):
        try:
            db.session.rollback()
        except Exception:  # pragma: no cover - defensive
            pass
        log.exception("Unhandled exception [request=%s]", getattr(g, "request_id", "-"))
        return error_response("INTERNAL_ERROR", "An internal error occurred.", 500)

    _register_jwt_callbacks()


def _register_jwt_callbacks() -> None:
    from ..models.token_blocklist import TokenBlocklist

    @jwt.unauthorized_loader
    def _missing(_reason):
        return error_response("AUTHENTICATION_ERROR", "Authentication required.", 401)

    @jwt.invalid_token_loader
    def _invalid(_reason):
        return error_response("INVALID_TOKEN", "The access token is invalid.", 401)

    @jwt.expired_token_loader
    def _expired(_header, _payload):
        return error_response("TOKEN_EXPIRED", "The access token has expired.", 401)

    @jwt.revoked_token_loader
    def _revoked(_header, _payload):
        return error_response("TOKEN_REVOKED", "The access token has been revoked.", 401)

    @jwt.token_in_blocklist_loader
    def _is_revoked(_header, payload) -> bool:
        jti = payload.get("jti")
        return db.session.query(TokenBlocklist.id).filter_by(jti=jti).first() is not None
