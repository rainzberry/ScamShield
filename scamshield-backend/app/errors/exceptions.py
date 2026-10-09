"""Application exceptions. Every AppError becomes the standard JSON error envelope."""
from __future__ import annotations


class AppError(Exception):
    status_code = 500
    code = "INTERNAL_ERROR"
    default_message = "An internal error occurred."

    def __init__(self, message: str | None = None, *, code: str | None = None,
                 status_code: int | None = None, details=None):
        self.message = message or self.default_message
        super().__init__(self.message)
        if code:
            self.code = code
        if status_code:
            self.status_code = status_code
        self.details = details


class ValidationAppError(AppError):
    status_code = 400
    code = "VALIDATION_ERROR"
    default_message = "The request is invalid."


class AuthenticationError(AppError):
    status_code = 401
    code = "AUTHENTICATION_ERROR"
    default_message = "Authentication required."


class ForbiddenError(AppError):
    status_code = 403
    code = "FORBIDDEN"
    default_message = "You do not have permission to perform this action."


class NotFoundError(AppError):
    status_code = 404
    code = "NOT_FOUND"
    default_message = "Resource not found."


class ConflictError(AppError):
    status_code = 409
    code = "CONFLICT"
    default_message = "The resource already exists."


class FileTooLargeError(AppError):
    status_code = 413
    code = "FILE_TOO_LARGE"
    default_message = "The uploaded file is too large."


class UnsupportedMediaError(AppError):
    status_code = 415
    code = "UNSUPPORTED_FILE_TYPE"
    default_message = "Unsupported file type."


class QRDecodeError(AppError):
    status_code = 422
    code = "QR_NOT_DECODABLE"
    default_message = "No readable QR code was found in the image."


class RateLimitedError(AppError):
    status_code = 429
    code = "RATE_LIMITED"
    default_message = "Too many requests. Please slow down."


class NotImplementedFeatureError(AppError):
    status_code = 501
    code = "NOT_IMPLEMENTED"
    default_message = "This feature is not implemented."


class MLContractError(AppError):
    """The ML engine answered, but not in the documented format."""
    status_code = 502
    code = "ML_INVALID_RESPONSE"
    default_message = "The analysis engine returned an invalid response."


class ModelUnavailableError(AppError):
    """The ML engine/model artifact is missing or cannot be loaded."""
    status_code = 503
    code = "MODEL_UNAVAILABLE"
    default_message = "The analysis model is currently unavailable."


class AnalysisFailedError(AppError):
    status_code = 500
    code = "ANALYSIS_FAILED"
    default_message = "The analysis could not be completed."
