"""Password policy + hashing (Werkzeug PBKDF2-SHA256, salted). Passwords are never logged."""
from __future__ import annotations

from flask import current_app
from werkzeug.security import check_password_hash, generate_password_hash

_COMMON = {"password", "password1", "password123", "12345678", "123456789",
           "qwerty123", "iloveyou1", "admin123", "letmein123", "welcome123"}
_dummy_cache: dict[str, str] = {}


def password_problems(password: str) -> list[str]:
    problems = []
    if len(password) < 8:
        problems.append("at least 8 characters")
    if not any(c.isalpha() for c in password):
        problems.append("at least one letter")
    if not any(c.isdigit() for c in password):
        problems.append("at least one digit")
    if password.lower() in _COMMON:
        problems.append("not be a commonly used password")
    return problems


def hash_password(password: str) -> str:
    return generate_password_hash(password, method=current_app.config["PASSWORD_HASH_METHOD"])


def verify_password(stored_hash: str, password: str) -> bool:
    return check_password_hash(stored_hash, password)


def verify_dummy(password: str) -> None:
    """Burn comparable CPU time when the email is unknown (limits user enumeration by timing)."""
    method = current_app.config["PASSWORD_HASH_METHOD"]
    if method not in _dummy_cache:
        _dummy_cache[method] = generate_password_hash("not-a-real-password", method=method)
    check_password_hash(_dummy_cache[method], password)
