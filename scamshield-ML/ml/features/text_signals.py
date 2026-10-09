"""Regex signals for message text. Every hit returns the matched phrase as evidence."""
from __future__ import annotations

import re
from typing import Dict, List


def _c(patterns):
    return [re.compile(p, re.I) for p in patterns]


URGENCY_STRONG = _c([
    r"\baccount (?:will be |has been |is )?(?:suspended|locked|closed|disabled|limited|terminated)\b",
    r"\bfinal (?:notice|warning|reminder)\b",
    r"\bact now\b",
    r"\bwithin (?:the next )?\d{1,3} (?:hours?|hrs?|days?)\b",
    r"\bimmediate (?:action|attention|response) (?:is )?required\b",
    r"\byour (?:account|access) (?:will|may) be (?:suspended|closed|locked|terminated)\b",
])
URGENCY_WEAK = _c([
    r"\burgent(?:ly)?\b", r"\bimmediately\b", r"\bexpires? (?:today|soon|in \d+)\b",
    r"\blast chance\b", r"\btime[- ]sensitive\b", r"\bverify now\b",
])
CREDENTIAL = _c([
    r"\b(?:verify|confirm|update|validate|re-?enter|provide|enter|submit)\b[^.\n]{0,40}?\b(?:password|passcode|pin|otp|one[- ]time (?:password|passcode|code)|cvv|card (?:number|details)|credentials?|login (?:details|information)|account (?:details|information|number)|bank (?:details|account)|ssn|social security|aadhaar|pan (?:card|number))\b",
    r"\b(?:click|tap|follow)\b[^.\n]{0,25}?\b(?:link|button|here)\b[^.\n]{0,40}?\b(?:verify|confirm|log ?in|sign ?in|update|unlock|restore)\b",
    r"\b(?:log ?in|sign ?in)\b[^.\n]{0,20}?\bto (?:verify|confirm|restore|unlock|secure|keep)\b",
])
PAYMENT = _c([
    r"\bgift ?cards?\b",
    r"\b(?:wire transfer|western union|moneygram)\b",
    r"\b(?:pay|send|transfer|deposit)\b[^.\n]{0,30}?\b(?:bitcoin|btc|crypto(?:currency)?|usdt)\b",
    r"\b(?:processing|clearance|transfer|handling|release|registration|activation) fee\b",
    r"\bsend (?:me )?(?:the )?money\b",
])
ADV_G1 = _c([r"\b(?:next of kin|beneficiary|inheritance|unclaimed (?:funds?|fortune)|deceased|dormant account|late husband|foreign partner)\b"])
ADV_G2 = _c([r"(?:[$£€]|\busd\b|\bus\$)\s?\d{1,3}(?:,\d{3})+|\b\d+(?:\.\d+)?\s?million\b"])
ADV_G3 = _c([r"\b(?:transfer(?:red)? (?:of )?(?:the )?funds?|release (?:of )?(?:the )?funds?|business proposal|mutual benefit|strictly confidential)\b"])
OFFER = _c([
    r"\byou(?:'ve| have)? (?:won|been selected)\b",
    r"\byou are (?:a |the )?(?:lucky )?winner\b",
    r"\bcongratulations\b[^.\n]{0,60}?\b(?:won|winner|selected|prize|reward)\b",
    r"\b(?:lottery|jackpot)\b",
    r"\bclaim your (?:reward|prize|gift|bonus|winnings|refund)\b",
    r"\bfree (?:gift|iphone|money|prize)\b",
])
PROMO = _c([
    r"\b(?:buy|order) now\b", r"\blimited[- ]time\b", r"\b(?:special|exclusive) (?:offer|promotion|deal)\b",
    r"\b(?:lowest|cheapest) price\b", r"\b100% (?:free|guaranteed)\b", r"\bno prescription\b",
    r"\b(?:viagra|cialis)\b", r"\bweight loss\b", r"\bwork from home\b",
    r"\bmake money (?:fast|online)\b", r"\bclick here\b", r"\bdiscount\b",
])
_NEG = re.compile(r"\b(?:never|not|don't|won't|no)\b", re.I)


def _find(patterns, text: str, limit: int = 6, check_negation: bool = False) -> List[str]:
    hits: List[str] = []
    for p in patterns:
        for m in p.finditer(text):
            if check_negation and _NEG.search(text[max(0, m.start() - 30):m.start()]):
                continue
            s = re.sub(r"\s+", " ", m.group(0)).strip()[:80]
            if s.lower() not in {h.lower() for h in hits}:
                hits.append(s)
            break
        if len(hits) >= limit:
            break
    return hits


def extract_text_signals(text: str) -> Dict[str, List[str]]:
    """Return {signal_name: [matched phrases]} for signals that meet their trigger rule."""
    t = text[:100000] if isinstance(text, str) else ""
    out: Dict[str, List[str]] = {}
    strong, weak = _find(URGENCY_STRONG, t), _find(URGENCY_WEAK, t)
    if strong or len(weak) >= 2:
        out["urgent"] = strong + weak
    cred = _find(CREDENTIAL, t, check_negation=True)
    if cred:
        out["credential"] = cred
    pay = _find(PAYMENT, t)
    if pay:
        out["payment"] = pay
    groups = [_find(g, t, 2) for g in (ADV_G1, ADV_G2, ADV_G3)]
    if sum(1 for g in groups if g) >= 2:
        out["advance_fee"] = [h for g in groups for h in g]
    offer = _find(OFFER, t)
    if offer:
        out["offer"] = offer
    promo = _find(PROMO, t)
    if len(promo) >= 2:
        out["promo"] = promo
    return out