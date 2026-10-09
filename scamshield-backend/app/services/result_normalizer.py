"""Validates and normalises whatever the ML engine returns into ONE internal shape.

This is the ML <-> backend contract. See README "ML integration" for the full spec.
"""
from __future__ import annotations

import json
import math
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field, is_dataclass

from ..errors.exceptions import MLContractError
from .severity import severity_for

VALID_CLASSIFICATIONS = ("safe", "spam", "phishing", "malicious")
_CLASS_ALIASES = {
    "safe": "safe", "legitimate": "safe", "legit": "safe", "ham": "safe",
    "benign": "safe", "clean": "safe", "spam": "spam", "phishing": "phishing",
    "phish": "phishing", "malicious": "malicious", "malware": "malicious",
}
VALID_INDICATOR_SEVERITIES = ("INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL")
MAX_INDICATORS = 50
_MAX_JSON_BYTES = 200_000

DEFAULT_RECOMMENDATIONS = {
    "safe": "No threat indicators were found. Stay cautious with unexpected requests.",
    "spam": "This looks like unwanted bulk or promotional content. Avoid replying or clicking links.",
    "phishing": "Do not click links, open attachments or share credentials. Report and delete it.",
    "malicious": "Do not interact with this content. Delete it and report it to your security contact.",
}


@dataclass(frozen=True)
class NormalizedResult:
    classification: str
    risk_score: int
    confidence: float
    severity: str
    indicators: list = field(default_factory=list)
    explanation: dict = field(default_factory=dict)
    recommendation: str = ""
    model_version: str = "unknown"


def _as_mapping(raw) -> dict:
    if isinstance(raw, Mapping):
        return dict(raw)
    if is_dataclass(raw) and not isinstance(raw, type):
        return asdict(raw)
    for attr in ("model_dump", "dict"):
        fn = getattr(raw, attr, None)
        if callable(fn):
            try:
                data = fn()
                if isinstance(data, Mapping):
                    return dict(data)
            except Exception:
                break
    if hasattr(raw, "__dict__"):
        return {k: v for k, v in vars(raw).items() if not k.startswith("_")}
    raise MLContractError("The analysis engine returned an unsupported result type.")


def _pick(data: dict, *names):
    for name in names:
        if data.get(name) is not None:
            return data[name]
    return None


def _jsonable(value, what: str):
    try:
        text = json.dumps(value, default=str)
    except (TypeError, ValueError):
        raise MLContractError(f"The analysis engine returned a non-serialisable {what}.") from None
    if len(text) > _MAX_JSON_BYTES:
        raise MLContractError(f"The analysis engine returned an oversized {what}.")
    return json.loads(text)


def _num(value, what: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise MLContractError(f"The analysis engine returned an invalid {what}.")
    return float(value)


def _indicator(item) -> dict:
    if isinstance(item, str):
        item = {"description": item}
    elif not isinstance(item, Mapping):
        item = _as_mapping(item)
    sev = str(_pick(item, "severity", "level") or "INFO").upper()
    if sev not in VALID_INDICATOR_SEVERITIES:
        sev = "INFO"
    weight = _pick(item, "weight", "score", "contribution")
    weight = float(weight) if isinstance(weight, (int, float)) and not isinstance(weight, bool) \
        and math.isfinite(weight) else None
    evidence = _pick(item, "evidence", "matched", "value")
    return {
        "type": str(_pick(item, "type", "name", "id", "category") or "signal")[:64],
        "description": str(_pick(item, "description", "detail", "message", "reason") or "")[:500],
        "severity": sev,
        "weight": weight,
        "evidence": None if evidence is None else str(evidence)[:1000],
        "source": "ml",
    }


def normalize_ml_result(raw) -> NormalizedResult:
    if raw is None:
        raise MLContractError("The analysis engine returned no result.")
    data = _as_mapping(raw)

    label = _pick(data, "classification", "label", "prediction", "class")
    classification = _CLASS_ALIASES.get(str(label).strip().lower()) if label is not None else None
    if classification is None:
        raise MLContractError("The analysis engine returned an unknown classification.")

    risk_value = _num(_pick(data, "risk_score", "risk"), "risk_score")
    if not 0 <= risk_value <= 100:
        raise MLContractError("The analysis engine returned a risk_score outside 0-100.")
    risk_score = int(math.floor(risk_value + 0.5))

    confidence = _num(_pick(data, "confidence", "probability"), "confidence")
    if not 0 <= confidence <= 1:
        raise MLContractError("The analysis engine returned a confidence outside 0-1.")

    raw_indicators = _pick(data, "indicators", "reasons", "signals") or []
    if not isinstance(raw_indicators, (list, tuple)):
        raise MLContractError("The analysis engine returned invalid indicators.")
    indicators = [_indicator(i) for i in list(raw_indicators)[:MAX_INDICATORS]]

    explanation = _pick(data, "explanation", "explanations")
    if explanation is None:
        explanation = {}
    elif isinstance(explanation, str):
        explanation = {"summary": explanation}
    elif isinstance(explanation, (list, tuple)):
        explanation = {"reasons": list(explanation)}
    elif not isinstance(explanation, Mapping):
        raise MLContractError("The analysis engine returned an invalid explanation.")
    explanation = _jsonable(explanation, "explanation")

    recommendation = _pick(data, "recommendation", "advice")
    recommendation = str(recommendation).strip()[:2000] if recommendation else \
        DEFAULT_RECOMMENDATIONS[classification]

    return NormalizedResult(
        classification=classification,
        risk_score=risk_score,
        confidence=round(confidence, 4),
        severity=severity_for(risk_score),   # backend-owned band mapping; ML severity is ignored
        indicators=indicators,
        explanation=explanation,
        recommendation=recommendation,
        model_version=str(_pick(data, "model_version", "version") or "unknown")[:64],
    )
