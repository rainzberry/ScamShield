from __future__ import annotations

import re

_WS = re.compile(r"\s+")
_URL_RE = re.compile(r"https?://[^\s<>\"'\)\]]{1,2048}", re.IGNORECASE)
_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def one_line(value: str, limit: int) -> str:
    value = _WS.sub(" ", value or "").strip()
    return value if len(value) <= limit else value[: limit - 1] + "…"


def strip_control_chars(value: str) -> str:
    return _CONTROL.sub("", value or "")


def extract_urls(text: str, limit: int = 20) -> list[str]:
    seen: list[str] = []
    for match in _URL_RE.findall(text or ""):
        url = match.rstrip(".,;:!?")
        if url not in seen:
            seen.append(url)
        if len(seen) >= limit:
            break
    return seen
