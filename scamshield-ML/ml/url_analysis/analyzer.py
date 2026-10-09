from __future__ import annotations

import re
from typing import Any, Dict, Optional

from ..configs.settings import RISK_FORMULA_VERSION, RULES_VERSION, URL_THRESHOLD
from ..explainability.url_explainer import explain_url
from ..result import assemble_result, make_versions
from ..risk.engine import compute_risk
from ..risk.weights import make_indicator
from ..schemas import InvalidInputError, MalformedURLError
from .features import analyze_url_structure
from .indicators import build_url_indicators

_DANGEROUS = re.compile(r"^\s*(javascript|data|vbscript|file|blob):", re.I)
_BRANDISH = {"LOOKALIKE_DOMAIN", "BRAND_IN_SUBDOMAIN", "BRAND_IMPERSONATION_PATTERN"}


def analyze_url(url: str, url_model=None, threshold: float = URL_THRESHOLD, scan_type: str = "url") -> Dict[str, Any]:
    """Offline URL analysis. The URL is parsed only - it is never fetched or opened."""
    if not isinstance(url, str) or not url.strip():
        raise InvalidInputError("URL must be a non-empty string")
    versions = make_versions(None, url_model)
    m = _DANGEROUS.match(url)
    if m:
        inds = [make_indicator("DANGEROUS_URI_SCHEME", f"URI scheme '{m.group(1).lower()}:' can run script or expose local content when opened.")]
        return assemble_result(scan_type=scan_type, classification="malicious", risk=compute_risk(inds, None),
                               indicators=inds, versions=versions, extras={"url": url[:200]})
    try:
        features, details = analyze_url_structure(url)
    except MalformedURLError as e:
        inds = [make_indicator("MALFORMED_URL", f"URL could not be parsed: {e}")]
        return assemble_result(scan_type=scan_type, classification="unverified", risk=compute_risk(inds, None),
                               indicators=inds, versions=versions, extras={"url": url[:200]})

    p: Optional[float] = None
    model_block, model_features, terms = None, [], []
    if url_model is not None:
        ex = explain_url(url_model, features)
        p = ex["probability_phishing"]
        model_features = ex["features"]
        model_block = {
            "name": url_model.metadata.get("model_type", "URL classifier"),
            "version": url_model.version, "probability_suspicious": p,
            "predicted_label": "phishing" if p >= threshold else "legitimate",
            "confidence": max(p, 1 - p), "threshold": threshold, "method": ex["method"],
        }
        terms = [f"{x['feature']}={x['value']:g}" for x in model_features if x["contribution"] > 0][:3]

    inds = build_url_indicators(features, details)
    ml_flag = p is not None and p >= threshold
    if ml_flag:
        inds.append(make_indicator(
            "ML_SUSPICIOUS_URL",
            f"URL classifier estimated P(phishing)={p:.3f} (threshold {threshold}). "
            + ("Top contributions: " + ", ".join(terms) + "." if terms else ""),
            source="model"))
    risk = compute_risk(inds, p)
    suspicious = (p is not None and (ml_flag or risk["score"] >= 50)) or (p is None and risk["score"] >= 25)
    codes = {i.code for i in inds}
    if suspicious:
        classification = "phishing" if (ml_flag or codes & _BRANDISH) else "suspicious"
    else:
        classification = "safe" if p is not None else "unverified"
    return assemble_result(
        scan_type=scan_type, classification=classification, risk=risk, indicators=inds,
        model_block=model_block, model_features=model_features, extracted=features,
        versions=versions, summary_terms=terms,
        extras={"url_details": {k: details[k] for k in
                ("normalized_url", "hostname", "registered_domain", "suffix", "scheme", "scheme_assumed")}},
    )