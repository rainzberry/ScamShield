from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional

from ..configs.lists import KNOWN_UPI_HANDLES, UPI_PAYEE_KEYWORDS, DANGEROUS_URI_SCHEMES
from ..configs.settings import MAX_EMBEDDED_URLS, TEXT_THRESHOLD, URL_THRESHOLD
from ..preprocessing.text_cleaning import extract_urls
from ..result import assemble_result, bubble_indicators, make_versions
from ..risk.engine import compute_risk
from ..risk.weights import make_indicator
from ..schemas import Indicator
from ..text_analysis.analyzer import analyze_message
from ..url_analysis.analyzer import analyze_url
from ..url_analysis.brands import find_brand, tokenize
from .payload import ParsedPayload, parse_payload

_VPA = re.compile(r"^[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z][a-zA-Z0-9.\-]{1,63}$")
_NOTE = re.compile(r"\b(?:refund|cash ?back|reward|prize|lottery|receive money|claim)\b", re.I)
HIGH_AMOUNT = Decimal("10000")


def _rules_only(parsed: ParsedPayload, inds: List[Indicator], url_model=None, warnings=None, extras=None):
    risk = compute_risk(inds, None)
    cls = "suspicious" if risk["score"] >= 25 else "unverified"
    ex = {"payload": parsed.public()}
    ex.update(extras or {})
    return assemble_result(scan_type="qr", classification=cls, risk=risk, indicators=inds,
                           versions=make_versions(None, url_model), extras=ex, warnings=warnings)


def _wrap(child: Dict[str, Any], parsed: ParsedPayload) -> Dict[str, Any]:
    out = dict(child)
    out["scan_type"] = "qr"
    out["payload"] = parsed.public()
    if child["risk_score"] >= 50:
        ind = make_indicator("SUSPICIOUS_QR_PAYLOAD",
                             f"The QR payload ({parsed.type}) was flagged by analysis: risk {child['risk_score']}, classification '{child['classification']}'.").to_dict()
        out["indicators"] = [ind] + list(child["indicators"])
    return out


def _upi(parsed: ParsedPayload, url_model) -> Dict[str, Any]:
    f = parsed.fields
    inds: List[Indicator] = [
        make_indicator("UPI_PAYMENT_REQUEST", f"UPI URI action '{f.get('action') or 'unknown'}' starts a payment flow when scanned in a payment app. No payment was initiated by this analysis."),
        make_indicator("UPI_MERCHANT_UNVERIFIED", "Merchant identity could not be independently verified. UPI payees can only be verified inside your payment app; this analysis runs offline."),
    ]
    pa = (f.get("pa") or "").strip()
    if not pa or not _VPA.match(pa):
        inds.append(make_indicator("UPI_INVALID_VPA", "No payee UPI ID (pa) present." if not pa else f"Payee UPI ID '{pa}' does not match the VPA format name@handle."))
    else:
        handle = pa.split("@", 1)[1].lower()
        if handle not in KNOWN_UPI_HANDLES:
            inds.append(make_indicator("UPI_UNKNOWN_HANDLE", f"UPI handle '@{handle}' is not in the built-in known-handle list (the list is non-exhaustive)."))
    if not (f.get("pn") or "").strip():
        inds.append(make_indicator("UPI_MISSING_PAYEE_NAME", "No payee name (pn) is provided."))
    if f.get("am") not in (None, ""):
        try:
            amt = Decimal(str(f["am"]))
            if not amt.is_finite() or amt <= 0:
                raise InvalidOperation
            inds.append(make_indicator("UPI_PREFILLED_AMOUNT", f"Amount is pre-filled: {amt} {f.get('cu') or 'INR'}."))
            if amt >= HIGH_AMOUNT:
                inds.append(make_indicator("UPI_HIGH_AMOUNT", f"Pre-filled amount {amt} is at or above {HIGH_AMOUNT}."))
        except InvalidOperation:
            inds.append(make_indicator("UPI_INVALID_AMOUNT", f"Amount value '{f['am']}' is not a positive number."))
    payee_text = (pa.split("@")[0] + " " + (f.get("pn") or "")).lower()
    kw = [k for k in UPI_PAYEE_KEYWORDS if k in payee_text]
    brand = find_brand(tokenize(payee_text))
    if kw or brand:
        inds.append(make_indicator("UPI_PAYEE_KEYWORDS", "Payee identifier contains words commonly used in impersonation: " + ", ".join(kw + ([brand] if brand else [])) + " (a signal, not proof)."))
    note_hits = sorted({m.lower() for m in _NOTE.findall(f.get("tn") or "")})
    if note_hits:
        inds.append(make_indicator("UPI_NOTE_REWARD_LANGUAGE", "Payment note mentions: " + ", ".join(note_hits) + ". Scanning a UPI QR sends money; it never receives money."))
    if f.get("duplicate_params"):
        inds.append(make_indicator("UPI_DUPLICATE_PARAMS", "Repeated parameter(s) in UPI URI: " + ", ".join(f["duplicate_params"])))
    extras: Dict[str, Any] = {}
    if f.get("url"):
        try:
            child = analyze_url(f["url"], url_model=url_model)
            inds.append(make_indicator("UPI_EMBEDDED_URL", f"UPI payload contains a URL parameter (not opened). URL risk {child['risk_score']}."))
            inds.extend(bubble_indicators(child, "In UPI url parameter"))
            extras["embedded_urls"] = [{"url": f["url"], "risk_score": child["risk_score"], "classification": child["classification"]}]
        except ValueError:
            pass
    return _rules_only(parsed, inds, url_model, extras=extras)


def _wifi(parsed: ParsedPayload, url_model) -> Dict[str, Any]:
    f, inds = parsed.fields, []
    sec = f.get("security", "")
    if sec in ("NOPASS", "", "NONE"):
        inds.append(make_indicator("WIFI_OPEN_NETWORK", f"Network '{f.get('ssid')}' is configured without encryption."))
    elif sec == "WEP":
        inds.append(make_indicator("WIFI_WEP", f"Network '{f.get('ssid')}' uses WEP, which is cryptographically broken."))
    return _rules_only(parsed, inds, url_model)


def _vcard(parsed: ParsedPayload, url_model) -> Dict[str, Any]:
    inds, children = [], []
    for u in parsed.fields.get("urls", [])[:MAX_EMBEDDED_URLS]:
        try:
            c = analyze_url(u, url_model=url_model)
        except ValueError:
            continue
        children.append({"url": u, "risk_score": c["risk_score"], "classification": c["classification"]})
        inds.extend(bubble_indicators(c, f"In vCard URL {u[:50]}"))
    return _rules_only(parsed, inds, url_model, extras={"embedded_urls": children})


def analyze_qr_payload(payload: str, text_model=None, url_model=None,
                       url_threshold: float = URL_THRESHOLD, text_threshold: float = TEXT_THRESHOLD) -> Dict[str, Any]:
    """Analyse an already-decoded QR payload. Nothing is opened, fetched or paid."""
    parsed = parse_payload(payload)
    t = parsed.type
    if t == "url":
        return _wrap(analyze_url(parsed.fields["url"], url_model=url_model, threshold=url_threshold, scan_type="qr"), parsed)
    if t == "upi":
        return _upi(parsed, url_model)
    if t == "wifi":
        return _wifi(parsed, url_model)
    if t == "vcard":
        return _vcard(parsed, url_model)
    if t in ("text", "email", "sms"):
        subject = parsed.fields.get("subject", "")
        body = parsed.fields.get("text") or parsed.fields.get("body", "")
        if not (subject or body).strip():
            return _rules_only(parsed, [], url_model, warnings=["Payload has no message text to analyse."])
        child = analyze_message(subject=subject, body=body, text_model=text_model, url_model=url_model,
                                scan_type="qr", threshold=text_threshold)
        return _wrap(child, parsed)
    inds = []
    if t == "unknown" and parsed.fields.get("scheme") in DANGEROUS_URI_SCHEMES:
        inds.append(make_indicator("DANGEROUS_URI_SCHEME", f"URI scheme '{parsed.fields['scheme']}:' can run script or expose local content."))
        risk = compute_risk(inds, None)
        return assemble_result(scan_type="qr", classification="malicious", risk=risk, indicators=inds,
                               versions=make_versions(None, url_model), extras={"payload": parsed.public()})
    return _rules_only(parsed, inds, url_model)