"""URL validation. Validation is syntactic only: nothing is ever fetched or opened."""
from __future__ import annotations

import re
from urllib.parse import urlsplit

_OTHER_SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.\-]*:(?!\d)")


def normalize_url(raw: str) -> str:
    """Return a syntactically valid http(s) URL or raise ValueError."""
    value = (raw or "").strip()
    if not value:
        raise ValueError("URL must not be empty.")
    if len(value) > 2048:
        raise ValueError("URL is too long (max 2048 characters).")
    if any(ch.isspace() or ord(ch) < 32 or ord(ch) == 127 for ch in value):
        raise ValueError("URL must not contain spaces or control characters.")
    if "://" not in value:
        if _OTHER_SCHEME.match(value):
            raise ValueError("Only http and https URLs are supported.")
        value = "http://" + value
    try:
        parts = urlsplit(value)
        _ = parts.port  # raises ValueError for an invalid port
    except ValueError:
        raise ValueError("URL is not valid.") from None
    if parts.scheme.lower() not in ("http", "https"):
        raise ValueError("Only http and https URLs are supported.")
    if not parts.hostname or len(parts.hostname) > 253:
        raise ValueError("URL must contain a valid host name.")
    return value
