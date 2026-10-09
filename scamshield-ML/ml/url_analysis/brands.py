from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from ..configs.lists import BRAND_SAFE_REGISTERED_DOMAINS, BRANDS
from ..features.common import homoglyph_variants, levenshtein

BRANDS_BY_LEN = tuple(sorted(set(BRANDS), key=lambda b: (-len(b), b)))
FUZZY_BRANDS = tuple(b for b in BRANDS_BY_LEN if len(b) >= 6)


def tokenize(text: str) -> List[str]:
    return [t for t in re.split(r"[^a-z0-9]+", text.lower()) if t]


def brand_matches_tokens(tokens: List[str], brand: str) -> bool:
    if brand in tokens:
        return True
    if len(brand) >= 6:
        return any(t.startswith(brand) or t.endswith(brand) for t in tokens)
    return False


def find_brand(tokens: List[str]) -> Optional[str]:
    for b in BRANDS_BY_LEN:
        if brand_matches_tokens(tokens, b):
            return b
    return None


def brand_signals(sp: Dict[str, str], path_query: str = "") -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "brand_in_registered_extra": 0, "brand_in_subdomain": 0, "brand_in_path": 0,
        "brand_lookalike": 0, "matched_brand": None, "lookalike_of": None,
        "lookalike_token": None, "lookalike_distance": None,
    }
    if sp["registered"] in BRAND_SAFE_REGISTERED_DOMAINS:
        return out
    label = sp["label"]
    ltoks = tokenize(label)
    if label not in BRANDS:
        for b in BRANDS_BY_LEN:
            if brand_matches_tokens(ltoks, b):
                out["brand_in_registered_extra"], out["matched_brand"] = 1, b
                break
    b = find_brand(tokenize(sp["subdomain"]))
    if b:
        out["brand_in_subdomain"] = 1
        out["matched_brand"] = out["matched_brand"] or b
    b = find_brand(tokenize(path_query))
    if b:
        out["brand_in_path"] = 1
        out["matched_brand"] = out["matched_brand"] or b
    best = None
    for cand in {label} | {t for t in ltoks if len(t) >= 6}:
        if cand in BRANDS:
            continue
        for variant in homoglyph_variants(cand):
            for br in FUZZY_BRANDS:
                if abs(len(variant) - len(br)) > 2:
                    continue
                d = levenshtein(variant, br)
                if d <= (1 if len(br) < 9 else 2) and (best is None or d < best[0]):
                    best = (d, br, cand)
    if best:
        out.update(brand_lookalike=1, lookalike_of=best[1], lookalike_token=best[2],
                   lookalike_distance=best[0])
        out["matched_brand"] = out["matched_brand"] or best[1]
    return out