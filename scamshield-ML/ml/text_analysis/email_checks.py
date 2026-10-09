from __future__ import annotations

import re
from email.utils import parseaddr
from typing import List, Optional

from ..configs.lists import (BRAND_SAFE_REGISTERED_DOMAINS, DANGEROUS_ATTACHMENT_EXT,
                             FREEMAIL_DOMAINS, RISKY_ATTACHMENT_EXT, SENDER_ROLE_WORDS,
                             SUSPICIOUS_TLDS)
from ..features.common import split_hostname
from ..risk.weights import make_indicator
from ..schemas import Indicator
from ..url_analysis.brands import brand_signals, find_brand, tokenize

_DECOY = re.compile(r"\.(?:pdf|docx?|xlsx?|pptx?|jpe?g|png|gif|txt|rtf)\s*\.(?:exe|scr|bat|cmd|com|js|jse|vbs|vbe|lnk|jar|hta|ps1)$", re.I)


def _domain(addr: str) -> str:
    return addr.rsplit("@", 1)[1].lower().strip() if "@" in addr else ""


def sender_indicators(sender: Optional[str], reply_to: Optional[str]) -> List[Indicator]:
    out: List[Indicator] = []
    if not sender or not isinstance(sender, str):
        return out
    display, addr = parseaddr(sender)
    dom = _domain(addr)
    if dom:
        sp = split_hostname(dom)
        reg = sp["registered"]
        reasons = []
        brand = find_brand(tokenize(display))
        if brand and brand not in sp["label"] and (reg not in BRAND_SAFE_REGISTERED_DOMAINS or reg in FREEMAIL_DOMAINS):
            reasons.append(f"Display name mentions '{brand}' but the sender domain is '{reg}'.")
        bs = brand_signals(sp, "")
        if bs["brand_lookalike"]:
            reasons.append(f"Sender domain '{dom}' resembles brand '{bs['lookalike_of']}'.")
        elif bs["brand_in_registered_extra"] or bs["brand_in_subdomain"]:
            reasons.append(f"Sender domain '{dom}' embeds brand name '{bs['matched_brand']}' but is not that brand's known domain.")
        if sp["suffix"].split(".")[-1] in SUSPICIOUS_TLDS:
            reasons.append(f"Sender TLD '.{sp['suffix']}' is on the heuristic suspicious-TLD list.")
        dl = display.lower()
        if reg in FREEMAIL_DOMAINS and any(w in dl for w in SENDER_ROLE_WORDS):
            reasons.append(f"Official-sounding display name '{display}' is sent from free-mail domain '{reg}'.")
        if reasons:
            out.append(make_indicator("SUSPICIOUS_SENDER", " ".join(reasons)))
        if reply_to and isinstance(reply_to, str):
            rdom = _domain(parseaddr(reply_to)[1])
            if rdom and split_hostname(rdom)["registered"] != reg:
                out.append(make_indicator("REPLY_TO_MISMATCH", f"Reply-To domain '{rdom}' differs from sender domain '{dom}'."))
    return out


def attachment_indicators(names) -> List[Indicator]:
    exe, decoy, risky = [], [], []
    for n in list(names or [])[:50]:
        if not isinstance(n, str) or not n.strip():
            continue
        low = n.strip().lower()
        ext = low.rsplit(".", 1)[-1] if "." in low else ""
        if _DECOY.search(low):
            decoy.append(n)
        elif ext in DANGEROUS_ATTACHMENT_EXT:
            exe.append(n)
        elif ext in RISKY_ATTACHMENT_EXT:
            risky.append(n)
    out: List[Indicator] = []
    if decoy:
        out.append(make_indicator("DOUBLE_EXTENSION_ATTACHMENT", "Attachment(s) disguise an executable as a document: " + ", ".join(decoy)))
    if exe:
        out.append(make_indicator("EXECUTABLE_ATTACHMENT", "Executable/script attachment type: " + ", ".join(exe)))
    if risky:
        out.append(make_indicator("RISKY_ATTACHMENT", "Attachment type often used to deliver malware (macro/archive/HTML): " + ", ".join(risky)))
    return out