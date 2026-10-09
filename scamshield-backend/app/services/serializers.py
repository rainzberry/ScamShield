"""JSON representations. Keeps the API response contract in ONE place."""
from __future__ import annotations

from ..models.scan import Scan, ThreatIndicator
from ..utils.timeutil import iso


def serialize_indicator(ind: ThreatIndicator) -> dict:
    return {"type": ind.indicator_type, "description": ind.description, "severity": ind.severity,
            "weight": ind.weight, "evidence": ind.evidence, "source": ind.source}


def serialize_scan(scan: Scan, *, detail: bool = True) -> dict:
    result = scan.result
    data = {
        "id": scan.id,
        "scan_type": scan.scan_type,
        "classification": result.classification,
        "risk_score": result.risk_score,
        "confidence": result.confidence,
        "severity": result.severity,
        "input_summary": scan.input_summary,
        "created_at": iso(scan.created_at),
        "model_version": result.model_version,
    }
    if detail:
        data.update({
            "indicators": [serialize_indicator(i) for i in scan.indicators],
            "explanation": result.explanation,
            "recommendation": result.recommendation,
            "details": scan.details,
            "input": scan.input_data,
        })
    else:
        data["indicator_count"] = len(scan.indicators)
    return data
