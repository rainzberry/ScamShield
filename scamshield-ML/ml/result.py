from __future__ import annotations

from typing import Any, Dict, List, Optional

from .configs.settings import RISK_FORMULA_VERSION, RULES_VERSION
from .risk.engine import build_summary, recommendation_for
from .risk.weights import make_indicator
from .schemas import SEVERITY_RANK, Indicator


def make_versions(text_model=None, url_model=None) -> Dict[str, Optional[str]]:
    return {
        "text_model": text_model.version if text_model else None,
        "url_model": url_model.version if url_model else None,
        "rules": RULES_VERSION,
        "risk": RISK_FORMULA_VERSION,
    }


def bubble_indicators(child: Dict[str, Any], prefix: str, min_rank: int = 2) -> List[Indicator]:
    """Re-create rule indicators (MEDIUM+) from a child analysis, prefixing the evidence."""
    out = []
    for ind in child.get("indicators", []):
        if ind.get("source") == "rule" and SEVERITY_RANK.get(ind["severity"], 0) >= min_rank:
            out.append(make_indicator(ind["code"], f"{prefix}: {ind['evidence']}"))
    return out


def assemble_result(
    *,
    scan_type: str,
    classification: str,
    risk: Dict[str, Any],
    indicators: List[Indicator],
    model_block: Optional[Dict[str, Any]] = None,
    model_features: Optional[List[Dict[str, Any]]] = None,
    extracted: Optional[Dict[str, Any]] = None,
    versions: Optional[Dict[str, Any]] = None,
    summary_terms: Optional[List[str]] = None,
    extras: Optional[Dict[str, Any]] = None,
    warnings: Optional[List[str]] = None,
) -> Dict[str, Any]:
    inds = sorted(indicators, key=lambda i: (-SEVERITY_RANK[i.severity], i.code))
    summary = build_summary(classification, risk, model_block, summary_terms or [], inds)
    result: Dict[str, Any] = {
        "scan_type": scan_type,
        "classification": classification,
        "risk_score": risk["score"],
        "confidence": model_block["confidence"] if model_block else None,
        "severity": risk["severity"],
        "indicators": [i.to_dict() for i in inds],
        "explanation": {
            "summary": summary,
            "model": model_block,
            "model_features": model_features or [],
            "rule_features": [
                {"code": i.code, "evidence": i.evidence, "points": i.points}
                for i in inds
                if i.source == "rule"
            ],
            "extracted_features": extracted or {},
        },
        "risk_breakdown": risk["breakdown"],
        "recommendation": recommendation_for(classification, risk["severity"]),
        "model_version": model_block["version"] if model_block else "rules-only",
        "versions": versions or {},
        "model_used": model_block is not None,
        "warnings": warnings or [],
    }
    if extras:
        result.update(extras)
    return result