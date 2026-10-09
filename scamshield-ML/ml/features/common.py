from __future__ import annotations

import ipaddress
import math
import re
from collections import Counter
from typing import Dict, List

from ..configs.lists import MULTI_PART_SUFFIXES

_OBF_IP = re.compile(r"^(?:0x[0-9a-f]+|\d+)(?:\.(?:0x[0-9a-f]+|\d+)){3}$", re.I)
_HEX_IP = re.compile(r"^0x[0-9a-f]{1,8}$", re.I)
_DEC_IP = re.compile(r"^\d{8,10}$")
_GLYPH = str.maketrans({"0": "o", "3": "e", "4": "a", "5": "s", "7": "t", "$": "s", "@": "a"})


def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in Counter(s).values())


def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def homoglyph_variants(s: str) -> List[str]:
    s = s.lower()
    out = {s}
    t = s.translate(_GLYPH)
    for one in ("l", "i"):
        v = t.replace("1", one)
        out.update({v, v.replace("rn", "m"), v.replace("vv", "w")})
    return sorted(out)


def is_ip_host(host: str) -> bool:
    h = host.strip("[]").lower()
    if not h:
        return False
    try:
        ipaddress.ip_address(h)
        return True
    except ValueError:
        pass
    return bool(_OBF_IP.match(h) or _HEX_IP.match(h) or _DEC_IP.match(h))


def split_hostname(host: str) -> Dict[str, str]:
    h = host.lower().rstrip(".")
    if not h or is_ip_host(h):
        return {"subdomain": "", "label": h, "suffix": "", "registered": h}
    labels = [x for x in h.split(".") if x]
    if len(labels) == 1:
        return {"subdomain": "", "label": labels[0], "suffix": "", "registered": labels[0]}
    two = ".".join(labels[-2:])
    if two in MULTI_PART_SUFFIXES and len(labels) >= 3:
        suffix, label, sub = two, labels[-3], labels[:-3]
    else:
        suffix, label, sub = labels[-1], labels[-2], labels[:-2]
    return {
        "subdomain": ".".join(sub),
        "label": label,
        "suffix": suffix,
        "registered": f"{label}.{suffix}",
    }