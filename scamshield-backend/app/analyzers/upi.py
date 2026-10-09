"""UPI QR payload parser (upi://pay?pa=...&pn=...&am=...).

This module only PARSES. It never contacts a bank/PSP and never initiates a payment.
It does not claim fraud: identity simply cannot be verified offline.
"""
from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from urllib.parse import parse_qs, urlsplit

VERIFICATION_NOTE = "Merchant identity could not be independently verified."

_VPA_RE = re.compile(r"^[a-zA-Z0-9._\-]{2,256}@[a-zA-Z][a-zA-Z0-9]{2,64}$")
_MAX_FIELD = 200


def _field(params: dict, key: str) -> str | None:
    value = params.get(key)
    if value is None:
        return None
    value = value.strip()
    return value[:_MAX_FIELD] if value else None


def parse_upi(payload: str) -> dict:
    warnings: list[str] = []
    result = {
        "action": None, "upi_id": None, "upi_id_valid": False, "payee_name": None,
        "amount": None, "amount_valid": None, "currency": None,
        "transaction_reference": None, "transaction_note": None, "merchant_code": None,
        "verification_note": VERIFICATION_NOTE, "warnings": warnings,
    }
    try:
        parts = urlsplit(payload.strip())
        params = {k.lower(): v[0] for k, v in parse_qs(parts.query).items() if v}
    except ValueError:
        warnings.append("The UPI link is malformed and could not be fully parsed.")
        return result

    result["action"] = (parts.netloc or parts.path.strip("/")).lower() or None
    upi_id = _field(params, "pa")
    result["upi_id"] = upi_id
    if upi_id is None:
        warnings.append("No payee UPI ID (pa) is present in this QR code.")
    else:
        result["upi_id_valid"] = bool(_VPA_RE.match(upi_id))
        if not result["upi_id_valid"]:
            warnings.append("The UPI ID format looks unusual.")

    result["payee_name"] = _field(params, "pn")

    amount = _field(params, "am")
    if amount is not None:
        try:
            value = Decimal(amount)
            if not value.is_finite() or value <= 0 or value > Decimal("1000000000"):
                raise InvalidOperation
            result["amount"] = format(value.quantize(Decimal("0.01")), "f")
            result["amount_valid"] = True
        except InvalidOperation:
            result["amount"] = amount
            result["amount_valid"] = False
            warnings.append("The amount field is not a valid positive number.")

    currency = _field(params, "cu")
    result["currency"] = currency.upper() if currency else None
    result["transaction_reference"] = _field(params, "tr")
    result["transaction_note"] = _field(params, "tn")
    result["merchant_code"] = _field(params, "mc")
    return result
