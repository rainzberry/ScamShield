from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..configs.settings import MAX_EMBEDDED_URLS, MAX_TEXT_CHARS, TEXT_THRESHOLD
from ..explainability.text_explainer import explain_text
from ..features.common import split_hostname
from ..features.text_signals import extract_text_signals
from ..preprocessing.text_cleaning import (clean_text, compose_email_text, extract_urls,
                                           html_to_text, looks_like_html)
from ..result import assemble_result, bubble_indicators, make_versions
from ..risk.engine import compute_risk
from ..risk.weights import make_indicator
from ..schemas import SEVERITY_RANK, InvalidInputError, Indicator
from ..url_analysis.analyzer import analyze_url
from ..url_analysis.brands import find_brand, tokenize
from .email_checks import attachment_indicators, sender_indicators

_PHISH = {"CREDENTIAL_REQUEST", "SUSPICIOUS_SENDER", "SUSPICIOUS_URL_IN_TEXT", "LOOKALIKE_DOMAIN",
          "BRAND_IN_SUBDOMAIN", "IMPERSONATION_INDICATOR"}
_SCAM = {"ADVANCE_FEE_PATTERN", "PAYMENT_REQUEST", "UNSOLICITED_OFFER"}
_MAL = {"EXECUTABLE_ATTACHMENT", "DOUBLE_EXTENSION_ATTACHMENT"}


def _short(u: str, n: int = 80) -> str:
    return u if len(u) <= n else u[: n - 3] + "..."


def _categorize(codes: set) -> str:
    if codes & _MAL:
        return "malicious"
    if codes & _PHISH:
        return "phishing"
    if codes & _SCAM:
        return "scam"
    if "PROMOTIONAL_LANGUAGE" in codes:
        return "spam"
    return "suspicious"


def analyze_message(*, subject: Optional[str] = "", body: Optional[str] = "", sender: Optional[str] = None,
                    reply_to: Optional[str] = None, attachments: Optional[List[str]] = None,
                    text_model=None, url_model=None, scan_type: str = "email",
                    threshold: float = TEXT_THRESHOLD) -> Dict[str, Any]:
    subject = "" if subject is None else subject
    body = "" if body is None else body
    if not isinstance(subject, str) or not isinstance(body, str):
        raise InvalidInputError("subject and body must be strings")
    if not (subject.strip() or body.strip()):
        raise InvalidInputError("message is empty")

    warnings: List[str] = []
    plain_body = html_to_text(body)[0] if looks_like_html(body) else body
    plain = (subject + "\n" + plain_body)[: MAX_TEXT_CHARS * 2]
    cleaned = clean_text(compose_email_text(subject, body))
    inds: Dict[str, Indicator] = {}

    def add(ind: Indicator):
        inds.setdefault(ind.code, ind)

    # --- trained model
    p, model_block, model_features, terms = None, None, [], []
    if text_model is not None:
        if cleaned:
            ex = explain_text(text_model, cleaned)
            p = ex["probability_suspicious"]
            model_features = ex["features"]
            terms = [f"'{f['feature']}'" for f in model_features if f["direction"] == "suspicious" and f["analyzer"] == "word"][:4]
            model_block = {
                "name": text_model.metadata.get("model_type", "Text classifier"),
                "version": text_model.version, "probability_suspicious": p,
                "predicted_label": "suspicious" if p >= threshold else "safe",
                "confidence": max(p, 1 - p), "threshold": threshold, "method": ex["method"],
                "logit": ex["logit"], "intercept": ex["intercept"],
                "n_active_features": ex["n_active_features"],
            }
            if ex["n_active_features"] == 0:
                warnings.append("No text feature overlapped the model vocabulary; probability reflects the intercept only.")
        else:
            warnings.append("Message has no usable text content; the text model was not applied.")

    # --- rule signals
    sig = extract_text_signals(plain)
    ev = lambda k: ", ".join(f"'{h}'" for h in sig[k])
    if "urgent" in sig:
        add(make_indicator("URGENT_LANGUAGE", "Matched urgency/threat phrases: " + ev("urgent")))
    if "credential" in sig:
        add(make_indicator("CREDENTIAL_REQUEST", "Matched requests for credentials/sensitive data: " + ev("credential")))
    if "payment" in sig:
        add(make_indicator("PAYMENT_REQUEST", "Matched unusual payment-method phrases: " + ev("payment")))
    if "advance_fee" in sig:
        add(make_indicator("ADVANCE_FEE_PATTERN", "Matched advance-fee wording: " + ev("advance_fee")))
    if "offer" in sig:
        add(make_indicator("UNSOLICITED_OFFER", "Matched prize/offer phrases: " + ev("offer")))
    if "promo" in sig:
        add(make_indicator("PROMOTIONAL_LANGUAGE", "Matched promotional phrases: " + ev("promo")))

    # --- sender / attachments
    for i in sender_indicators(sender, reply_to) + attachment_indicators(attachments):
        add(i)
    if sender and "SUSPICIOUS_SENDER" not in inds and ("urgent" in sig or "credential" in sig):
        from email.utils import parseaddr
        addr = parseaddr(sender)[1]
        if "@" in addr:
            reg = split_hostname(addr.rsplit("@", 1)[1])["registered"]
            brand = find_brand(tokenize(plain[:3000]))
            if brand and brand not in reg:
                add(make_indicator("IMPERSONATION_INDICATOR", f"Message mentions '{brand}' with urgency/credential wording but is sent from '{reg}'."))

    # --- embedded URLs
    urls = extract_urls(subject + "\n" + body, MAX_EMBEDDED_URLS)
    children = []
    for u in urls:
        try:
            child = analyze_url(u, url_model=url_model)
        except ValueError:
            warnings.append(f"Could not analyse link: {_short(u, 60)}")
            continue
        children.append((u, child))
        for bi in bubble_indicators(child, f"In link {_short(u, 50)}"):
            add(bi)
    flagged = [(u, c) for u, c in children if c["risk_score"] >= 50 or c["classification"] in ("phishing", "malicious")]
    if flagged:
        add(make_indicator("SUSPICIOUS_URL_IN_TEXT", "Flagged link(s): " + "; ".join(
            f"{_short(u, 60)} (URL risk {c['risk_score']}, {c['classification']})" for u, c in flagged[:3])))

    if p is not None and p >= threshold:
        add(make_indicator("ML_SUSPICIOUS_TEXT",
                           f"Text classifier estimated P(suspicious)={p:.3f} (threshold {threshold})."
                           + (" Strongest terms: " + ", ".join(terms) + "." if terms else ""),
                           source="model"))

    all_inds = list(inds.values())
    risk = compute_risk(all_inds, p)
    suspicious = (p is not None and (p >= threshold or risk["score"] >= 50)) or (p is None and risk["score"] >= 25)
    if suspicious:
        classification = _categorize(set(inds))
    else:
        classification = "safe" if p is not None else "unverified"

    return assemble_result(
        scan_type=scan_type, classification=classification, risk=risk, indicators=all_inds,
        model_block=model_block, model_features=model_features,
        extracted={"text_length_clean": len(cleaned), "n_urls_found": len(urls),
                   "signals": {k: v for k, v in sig.items()}},
        versions=make_versions(text_model, url_model), summary_terms=terms, warnings=warnings,
        extras={"embedded_urls": [{"url": u, "risk_score": c["risk_score"], "classification": c["classification"]}
                                  for u, c in children]},
    )