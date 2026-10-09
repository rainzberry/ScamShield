"""Helpers that turn request data into validated Pydantic models."""
from __future__ import annotations

from flask import request
from pydantic import ValidationError

from ..errors.exceptions import ValidationAppError


def _clean_errors(exc: ValidationError) -> list[dict]:
    # Only field + message: never echo submitted values (could be passwords).
    return [
        {"field": ".".join(str(p) for p in err.get("loc", ())) or "body",
         "message": str(err.get("msg", "Invalid value"))}
        for err in exc.errors()
    ]


def parse_body(schema_cls):
    data = request.get_json(silent=True)
    if data is None:
        raise ValidationAppError(
            "Request body must be valid JSON with 'Content-Type: application/json'.")
    if not isinstance(data, dict):
        raise ValidationAppError("JSON body must be an object.")
    try:
        return schema_cls.model_validate(data)
    except ValidationError as exc:
        raise ValidationAppError("Request validation failed.", details=_clean_errors(exc)) from None


def parse_query(schema_cls):
    raw = {k: v for k, v in request.args.to_dict().items() if v != ""}
    try:
        return schema_cls.model_validate(raw)
    except ValidationError as exc:
        raise ValidationAppError("Query validation failed.", details=_clean_errors(exc)) from None
