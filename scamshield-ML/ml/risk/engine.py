"""Deterministic risk engine (risk-v1).

With a trained model:  score = round_half_up( 55 * P_model + min(evidence_points, 45) )
Rules only:            score = round_half_up( min(evidence_points, 100) )
evidence_points = sum(indicator.points) + points of matched combinations.
floor: some indicators enforce a minimum score (e.g. executable attachment >= 60).
P_model is rounded to 4 decimals first. Same input + same model version -> same score.
Risk is NOT confidence: confidence is the model's certainty in its own label.
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

from ..configs.settings import RISK_FORMULA_VERSION
from ..schemas import Indicator, severity_from_score

MODEL_WEIGHT = 55.0
EVIDENCE_CAP_WITH_MODEL = 45
EVIDENCE_CAP_RULES_ONLY = 100

COMBOS = [
    (frozenset({"CREDENTIAL_REQUEST", "URGENT_LANGUAGE"}), 5),
    (frozenset({"CREDENTIAL_REQUEST", "SUSPICIOUS_URL_IN_TEXT"}), 6),
    (frozenset({"CREDENTIAL_REQUEST", "SUSPICIOUS_SENDER"}), 5),
    (frozenset({"ADVANCE_FEE_PATTERN", "PAYMENT_REQUEST"}), 5),
    (frozenset({"IP_BASED_URL", "SUSPICIOUS_URL_KEYWORDS"}), 4),
    (frozenset({"LOOKALIKE_DOMAIN", "SUSPICIOUS_TLD"}), 4),
]


def _round_half_up(x: float) -> int:
    return int(math.floor(x + 0.5))


def compute_risk(indicators: List[Indicator], model_probability: Optional[float] = None) -> Dict[str, Any]:
    p = None
    if model_probability is not None:
        p = round(min(1.0, max(0.0, float(model_probability))), 4)
    model_pts = MODEL_WEIGHT * p if p is not None else 0.0
    codes = {i.code for i in indicators}
    items = sorted(({"code": i.code, "points": i.points} for i in indicators if i.points),
                   key=lambda d: d["code"])
    combos = [{"codes": sorted(c), "points": pts} for c, pts in COMBOS if c <= codes]
    raw = sum(d["points"] for d in items) + sum(c["points"] for c in combos)
    cap = EVIDENCE_CAP_WITH_MODEL if p is not None else EVIDENCE_CAP_RULES_ONLY
    evidence = min(raw, cap)
    before = max(0, min(100, _round_half_up(model_pts + evidence)))
    floor_ind = max(indicators, key=lambda i: (i.floor, i.code), default=None)
    floor = floor_ind.floor if floor_ind else 0
    score = max(before, floor) if floor else before
    score = max(0, min(100, score))
    return {
        "score": score,
        "severity": severity_from_score(score),
        "breakdown": {
            "formula_version": RISK_FORMULA_VERSION,
            "formula": ("round(55*P_model + min(evidence, 45))" if p is not None
                        else "round(min(evidence, 100))  [no model available]"),
            "model_probability": p,
            "model_points": round(model_pts, 2),
            "evidence_items": items,
            "combo_items": combos,
            "evidence_raw": raw,
            "evidence_cap": cap,
            "evidence_points": evidence,
            "score_before_floor": before,
            "floor_applied": ({"code": floor_ind.code, "floor": floor}
                              if floor and before < floor else None),
        },
    }


_REC = {
    "safe": "No significant threat indicators were found. Still be careful with unexpected requests for money or credentials.",
    "unverified": "No threat was detected by the available checks, but the content could not be verified. Confirm the source independently before acting.",
    "suspicious": "Treat this as suspicious. Do not click links, open attachments or share information until you verify the sender through a separate, trusted channel.",
    "spam": "Likely unsolicited promotional content. Do not respond or click links; mark as spam and delete.",
    "phishing": "Likely phishing. Do not click links, scan further QR codes, or enter credentials. Report it to your IT/security team or the impersonated organisation and delete it.",
    "scam": "Likely a scam. Do not send money, gift cards or personal details. Block the sender and report it.",
    "malicious": "Potentially malicious content. Do not open the attachment or link. Delete it and report it to your security team.",
}


def recommendation_for(classification: str, severity: str) -> str:
    base = _REC.get(classification, _REC["unverified"])
    if classification in ("safe", "unverified") and severity in ("MEDIUM", "HIGH", "CRITICAL"):
        base += " Some risk indicators were present - review them before proceeding."
    return base


def build_summary(classification, risk, model_block, top_terms, indicators) -> str:
    b = risk["breakdown"]
    parts = [f"Classified as {classification.upper()} with a risk score of {risk['score']}/100 ({risk['severity']})."]
    if model_block:
        parts.append(f"The {model_block['name']} estimated P(suspicious)={model_block['probability_suspicious']:.3f} "
                     f"(decision threshold {model_block['threshold']}), model confidence {model_block['confidence']:.3f}.")
    else:
        parts.append("No trained model contributed to this result; it is based on deterministic rules only.")
    if top_terms:
        parts.append("Top model features pushing toward suspicious: " + ", ".join(top_terms) + ".")
    rules = sorted(i.code for i in indicators if i.source == "rule" and i.severity != "INFO")
    if rules:
        parts.append("Rule indicators: " + ", ".join(rules) + ".")
    s = f"Score = model {b['model_points']} + evidence {b['evidence_points']}"
    if b["floor_applied"]:
        s += f", raised to floor {b['floor_applied']['floor']} by {b['floor_applied']['code']}"
    parts.append(s + ".")
    return " ".join(parts)