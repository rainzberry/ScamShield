from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict
from urllib.parse import parse_qs, parse_qsl, urlsplit

from ..configs.lists import DANGEROUS_URI_SCHEMES
from ..configs.settings import MAX_QR_PAYLOAD_CHARS
from ..schemas import InvalidInputError

_DOMAIN = re.compile(r"^(?:[a-z0-9](?:[a-z0-9\-]{0,61}[a-z0-9])?\.)+[a-z]{2,24}(?::\d{1,5})?(?:[/?#]\S*)?$", re.I)
_EMAIL = re.compile(r"^[\w.+\-]+@[\w\-]+(?:\.[\w\-]+)+$")
_PHONE = re.compile(r"^\+?[\d\s\-().]{7,25}$")
_SCHEME = re.compile(r"^([a-z][a-z0-9+.\-]*):", re.I)
_UPI_PUBLIC = ("pa", "pn", "am", "cu", "tn", "tr", "tid", "mc", "mode", "orgid", "url", "purpose", "ver")


@dataclass
class ParsedPayload:
    type: str
    raw: str
    fields: Dict[str, Any] = field(default_factory=dict)
    truncated: bool = False

    def public(self) -> Dict[str, Any]:
        return {"type": self.type, "fields": self.fields, "truncated": self.truncated}


def parse_upi(raw: str) -> Dict[str, Any]:
    parts = urlsplit(raw.strip())
    action = (parts.netloc or parts.path.strip("/")).lower()
    fields: Dict[str, str] = {}
    dupes = set()
    for k, v in parse_qsl(parts.query, keep_blank_values=True):
        k = k.lower()
        if k in fields:
            dupes.add(k)
        else:
            fields[k] = v
    return {"action": action, "fields": fields, "duplicate_params": sorted(dupes)}


def parse_wifi(raw: str) -> Dict[str, Any]:
    body, items, buf, i = raw[5:], [], "", 0
    while i < len(body):
        ch = body[i]
        if ch == "\\" and i + 1 < len(body):
            buf += body[i + 1]
            i += 2
            continue
        if ch == ";":
            items.append(buf)
            buf = ""
        else:
            buf += ch
        i += 1
    if buf:
        items.append(buf)
    f = {}
    for it in items:
        if ":" in it:
            k, v = it.split(":", 1)
            f[k.upper()] = v
    sec = f.get("T", "").upper()
    return {"ssid": f.get("S", ""), "security": sec or "NOPASS", "hidden": f.get("H", "").lower() == "true",
            "has_password": bool(f.get("P"))}   # the password itself is never returned


def parse_vcard(raw: str) -> Dict[str, Any]:
    text = re.sub(r"\r?\n[ \t]", "", raw)
    out: Dict[str, Any] = {"name": "", "org": "", "phones": [], "emails": [], "urls": []}
    for line in re.split(r"\r?\n", text):
        name, _, val = line.partition(":")
        key = name.split(";")[0].strip().upper()
        val = val.strip()
        if key == "FN":
            out["name"] = val
        elif key == "ORG":
            out["org"] = val
        elif key == "TEL":
            out["phones"].append(val)
        elif key == "EMAIL":
            out["emails"].append(val)
        elif key == "URL":
            out["urls"].append(val)
    return out


def parse_payload(raw: str) -> ParsedPayload:
    if not isinstance(raw, str):
        raise InvalidInputError("QR payload must be a string")
    text = raw.replace("\ufeff", "").strip()
    if not text:
        raise InvalidInputError("QR payload is empty")
    trunc = len(text) > MAX_QR_PAYLOAD_CHARS
    text = text[:MAX_QR_PAYLOAD_CHARS]
    low = text.lower()
    m = _SCHEME.match(text)
    scheme = m.group(1).lower() if m else ""

    if scheme in DANGEROUS_URI_SCHEMES:
        return ParsedPayload("unknown", text, {"scheme": scheme}, trunc)
    if low.startswith("upi:"):
        u = parse_upi(text)
        fields = {k: v for k, v in u["fields"].items() if k in _UPI_PUBLIC}
        return ParsedPayload("upi", text, {"action": u["action"], **fields,
                                           "duplicate_params": u["duplicate_params"],
                                           "has_signature": "sign" in u["fields"]}, trunc)
    if low.startswith(("http://", "https://")):
        return ParsedPayload("url", text, {"url": text}, trunc)
    if low.startswith("mailto:"):
        parts = urlsplit(text)
        q = parse_qs(parts.query)
        return ParsedPayload("email", text, {"address": parts.path, "subject": q.get("subject", [""])[0],
                                             "body": q.get("body", [""])[0]}, trunc)
    if low.startswith("tel:"):
        return ParsedPayload("phone", text, {"number": text[4:].strip()}, trunc)
    if low.startswith(("sms:", "smsto:", "mms:", "mmsto:")):
        rest = text.split(":", 1)[1]
        if "?" in rest:
            num, q = rest.split("?", 1)
            body = parse_qs(q).get("body", [""])[0]
        elif ":" in rest and low.startswith(("smsto", "mmsto")):
            num, body = rest.split(":", 1)
        else:
            num, body = rest, ""
        return ParsedPayload("sms", text, {"number": num, "body": body}, trunc)
    if low.startswith("wifi:"):
        return ParsedPayload("wifi", text, parse_wifi(text), trunc)
    if low.startswith("begin:vcard"):
        return ParsedPayload("vcard", text, parse_vcard(text), trunc)
    if _EMAIL.match(text):
        return ParsedPayload("email", text, {"address": text, "subject": "", "body": ""}, trunc)
    if _PHONE.match(text) and sum(c.isdigit() for c in text) >= 7:
        return ParsedPayload("phone", text, {"number": re.sub(r"[^\d+]", "", text)}, trunc)
    if _DOMAIN.match(text):
        return ParsedPayload("url", text, {"url": text}, trunc)
    if scheme and not re.search(r"\s", text):
        return ParsedPayload("unknown", text, {"scheme": scheme}, trunc)
    return ParsedPayload("text", text, {"text": text}, trunc)