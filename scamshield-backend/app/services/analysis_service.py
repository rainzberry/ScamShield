"""Orchestrates: validated input -> ML engine -> normalised result -> persistence."""
from __future__ import annotations

import logging
from dataclasses import replace

from sqlalchemy.exc import SQLAlchemyError

from ..analyzers.payload import classify_payload, informational_indicators
from ..analyzers.qr_decoder import decode_qr_image
from ..extensions import db
from ..models.scan import AnalysisResult, Scan, ThreatIndicator
from ..models.user import User
from ..security.uploads import ValidatedImage
from ..utils.text import extract_urls, one_line
from .ml_adapter import get_ml_engine
from .result_normalizer import NormalizedResult, normalize_ml_result

log = logging.getLogger(__name__)

QR_SAFETY_NOTICE = ("The QR code was decoded locally. Nothing was opened, paid, dialled "
                    "or connected to.")


def _persist(user: User, scan_type: str, summary: str, input_data: dict,
             result: NormalizedResult, details: dict | None = None,
             extra_indicators: list[dict] | None = None) -> Scan:
    scan = Scan(user_id=user.id, scan_type=scan_type, input_summary=one_line(summary, 300),
                input_data=input_data, details=details or {})
    scan.result = AnalysisResult(
        classification=result.classification, risk_score=result.risk_score,
        confidence=result.confidence, severity=result.severity,
        explanation=result.explanation, recommendation=result.recommendation,
        model_version=result.model_version)
    for position, ind in enumerate(list(result.indicators) + list(extra_indicators or [])):
        scan.indicators.append(ThreatIndicator(
            position=position, indicator_type=ind["type"], description=ind["description"],
            severity=ind["severity"], weight=ind.get("weight"), evidence=ind.get("evidence"),
            source=ind.get("source", "ml")))
    db.session.add(scan)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        log.exception("Failed to persist scan")
        raise
    return scan


def _compare_summary(r: NormalizedResult) -> dict:
    return {"classification": r.classification, "risk_score": r.risk_score,
            "confidence": r.confidence, "model_version": r.model_version}


def _escalate(text_result: NormalizedResult, url_result: NormalizedResult) -> NormalizedResult:
    """Policy for an email that ALSO carries an explicit URL: the result with the higher
    ML risk_score wins (ties go to the text result). No new score is computed here."""
    winner = url_result if url_result.risk_score > text_result.risk_score else text_result
    seen, merged = set(), []
    for ind in list(winner.indicators) + list(
            text_result.indicators if winner is url_result else url_result.indicators):
        key = (ind["type"], ind["description"])
        if key not in seen:
            seen.add(key)
            merged.append(ind)
    explanation = dict(winner.explanation)
    explanation["components"] = {"email_text": _compare_summary(text_result),
                                 "url": _compare_summary(url_result)}
    explanation["combination_policy"] = "highest_risk_component"
    return replace(winner, indicators=merged, explanation=explanation)


def analyze_email(user: User, data) -> Scan:
    engine = get_ml_engine()
    urls = extract_urls(data.body)
    if data.url and data.url not in urls:
        urls.insert(0, data.url)
    context = {
        "scan_type": "email", "sender": data.sender, "subject": data.subject, "body": data.body,
        "urls": urls, "attachments": [a.model_dump() for a in data.attachments],
    }
    text = f"Subject: {data.subject}\n\n{data.body}" if data.subject else data.body
    result = normalize_ml_result(engine.analyze_text(text, context=context))
    details = {"source": data.source, "sender": data.sender, "subject": data.subject,
               "url_count": len(urls)}
    if data.url:
        url_result = normalize_ml_result(engine.analyze_url(data.url, context=context))
        result = _escalate(result, url_result)
        details["explicit_url"] = data.url
    summary = f"{data.subject or '(no subject)'} - from {data.sender or 'unknown sender'}"
    return _persist(user, "email", summary, data.model_dump(), result, details)


def analyze_text(user: User, data) -> Scan:
    result = normalize_ml_result(
        get_ml_engine().analyze_text(data.text, context={"scan_type": "text"}))
    return _persist(user, "text", data.text, {"text": data.text}, result, {})


def analyze_url(user: User, data) -> Scan:
    # The URL is passed as a string to the analyzer. It is never opened or fetched here.
    result = normalize_ml_result(
        get_ml_engine().analyze_url(data.url, context={"scan_type": "url"}))
    return _persist(user, "url", data.url, {"url": data.url}, result, {"url": data.url})


def analyze_qr(user: User, image: ValidatedImage) -> Scan:
    decoded = decode_qr_image(image.data)          # local decode only
    info = classify_payload(decoded.payload)       # classify text; never execute/open it
    raw = get_ml_engine().analyze_payload(
        info.analysis_payload, payload_type=info.payload_type, parsed=info.parsed,
        context={"scan_type": "qr"})
    result = normalize_ml_result(raw)
    details = {
        "filename": image.safe_filename,
        "image": {"format": image.image_format, "width": image.width, "height": image.height},
        "payload_type": info.payload_type,
        "decoded_payload": info.display_payload,
        "parsed": info.parsed,
        "payload_truncated": decoded.truncated,
        "codes_found": decoded.codes_found,
        "safety_notice": QR_SAFETY_NOTICE,
    }
    return _persist(user, "qr", f"QR ({info.payload_type}): {info.display_payload}",
                    {"filename": image.safe_filename, "payload_type": info.payload_type,
                     "decoded_payload": info.display_payload},
                    result, details, informational_indicators(info))
