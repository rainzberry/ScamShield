from __future__ import annotations

from email import message_from_bytes, policy
from typing import Any, Dict, List


def _fallback_body(msg) -> str:
    chunks = []
    for part in msg.walk():
        if part.get_content_maintype() == "text" and not part.get_filename():
            try:
                payload = part.get_payload(decode=True) or b""
                chunks.append(payload.decode(part.get_content_charset() or "utf-8", errors="replace"))
            except Exception:
                continue
    return "\n".join(chunks)


def parse_eml_bytes(raw: bytes) -> Dict[str, Any]:
    """Parse a raw RFC-822 message into subject/sender/reply_to/body/attachments."""
    msg = message_from_bytes(raw, policy=policy.default)

    def hdr(name: str) -> str:
        try:
            return str(msg.get(name) or "")
        except Exception:
            return ""

    body = ""
    try:
        part = msg.get_body(preferencelist=("plain", "html"))
        body = part.get_content() if part is not None else ""
    except Exception:
        body = ""
    if not body:
        body = _fallback_body(msg)
    attachments: List[str] = []
    try:
        attachments = [p.get_filename() for p in msg.walk() if p.get_filename()]
    except Exception:
        pass
    return {
        "subject": hdr("subject"),
        "sender": hdr("from"),
        "reply_to": hdr("reply-to") or None,
        "body": body,
        "attachments": attachments,
    }