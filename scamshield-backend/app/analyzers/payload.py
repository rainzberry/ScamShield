"""Payload-type detection for decoded QR content.

Nothing here executes, opens, dials, pays or connects. It only classifies text.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..utils.text import strip_control_chars
from ..utils.urls import normalize_url
from .upi import VERIFICATION_NOTE, parse_upi

_BARE_DOMAIN = re.compile(r"^(?:www\.)?[a-z0-9](?:[a-z0-9\-]*[a-z0-9])?(?:\.[a-z0-9\-]+)+(?::\d+)?(?:[/?#]\S*)?$",
                          re.IGNORECASE)
_SCHEME = re.compile(r"^([a-zA-Z][a-zA-Z0-9+.\-]*):(?!\d)")
_RISKY_SCHEMES = {"javascript", "data", "file", "intent", "vbscript", "blob", "market",
                  "content", "ftp", "sftp", "ssh", "whatsapp", "tg", "skype"}
_CRYPTO_SCHEMES = {"bitcoin", "ethereum", "litecoin", "monero", "dogecoin", "bitcoincash"}


@dataclass
class PayloadInfo:
    payload_type: str
    display_payload: str      # what the QR contained (secrets redacted)
    analysis_payload: str     # what is passed to the ML analyzer
    parsed: dict = field(default_factory=dict)


def _parse_wifi(payload: str) -> tuple[dict, str]:
    """Parse WIFI:T:WPA;S:name;P:secret;H:false;; and REDACT the password."""
    body = payload[5:]
    fields: dict[str, str] = {}
    for token in re.split(r"(?<!\\);", body):
        if len(token) > 2 and token[1] == ":":
            fields[token[0].upper()] = token[2:].replace("\\;", ";")
    parsed = {
        "ssid": fields.get("S"),
        "security": fields.get("T") or "nopass",
        "hidden": fields.get("H", "").lower() == "true",
        "password_present": bool(fields.get("P")),
    }
    redacted = f"WIFI:T:{parsed['security']};S:{parsed['ssid'] or ''};P:[redacted];;"
    return parsed, redacted


def classify_payload(raw: str) -> PayloadInfo:
    payload = strip_control_chars(raw).strip()
    lower = payload.lower()
    scheme_match = _SCHEME.match(payload)
    scheme = scheme_match.group(1).lower() if scheme_match else None

    if lower.startswith("upi://"):
        return PayloadInfo("upi", payload, payload, parse_upi(payload))

    if lower.startswith("wifi:"):
        parsed, redacted = _parse_wifi(payload)
        return PayloadInfo("wifi", redacted, redacted, parsed)

    if scheme in ("http", "https") or (scheme is None and _BARE_DOMAIN.match(payload)):
        try:
            normalized = normalize_url(payload)
            return PayloadInfo("url", payload, normalized, {"url": normalized})
        except ValueError:
            return PayloadInfo("text", payload, payload, {})

    if lower.startswith(("mailto:", "matmsg:")):
        return PayloadInfo("email", payload, payload, {"scheme": "mailto"})
    if lower.startswith("tel:"):
        return PayloadInfo("phone", payload, payload, {"scheme": "tel"})
    if lower.startswith(("sms:", "smsto:", "mms:", "mmsto:")):
        return PayloadInfo("sms", payload, payload, {"scheme": scheme})
    if lower.startswith("geo:"):
        return PayloadInfo("geo", payload, payload, {"scheme": "geo"})
    if lower.startswith(("begin:vcard", "mecard:")):
        return PayloadInfo("contact", payload, payload, {})
    if lower.startswith("begin:vevent") or lower.startswith("begin:vcalendar"):
        return PayloadInfo("calendar", payload, payload, {})
    if scheme in _CRYPTO_SCHEMES:
        return PayloadInfo("crypto", payload, payload, {"scheme": scheme})
    if scheme and "\n" not in payload and (
            payload[len(scheme) + 1:].startswith("//") or scheme in _RISKY_SCHEMES):
        return PayloadInfo("other_uri", payload, payload, {"scheme": scheme})
    return PayloadInfo("text", payload, payload, {})


def informational_indicators(info: PayloadInfo) -> list[dict]:
    """Neutral, factual notes added by the backend. severity=INFO, weight=None:
    they never influence the risk score (scoring lives in the ML risk engine)."""

    def note(kind: str, text: str) -> dict:
        return {"type": kind, "description": text, "severity": "INFO",
                "weight": None, "evidence": None, "source": "backend"}

    notes: list[dict] = []
    t, p = info.payload_type, info.parsed
    if t == "upi":
        notes.append(note("upi_identity_unverified", VERIFICATION_NOTE))
        if p.get("amount_valid"):
            cur = p.get("currency") or "the default currency"
            notes.append(note("upi_amount_prefilled",
                              f"This QR pre-fills a payment amount of {p['amount']} ({cur})."))
        for warning in p.get("warnings", []):
            notes.append(note("upi_format_note", warning))
        notes.append(note("no_payment_initiated",
                          "ScamShield only parsed this payload. No payment was initiated."))
    elif t == "wifi":
        notes.append(note("wifi_config", "This QR contains a Wi-Fi network configuration. "
                                         "ScamShield did not connect to it."))
    elif t == "other_uri":
        notes.append(note("non_web_scheme",
                          f"This QR contains a non-web link ('{p.get('scheme')}:'). It was not opened."))
    elif t in ("phone", "sms", "email"):
        notes.append(note("action_link", f"This QR would start a {t} action on a phone. "
                                         "ScamShield did not trigger it."))
    elif t == "crypto":
        notes.append(note("crypto_payment_link",
                          "This QR contains a cryptocurrency payment link. It was not opened."))
    return notes
