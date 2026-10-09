"""Severity bands.

RISK SCORING LIVES IN THE ML RISK ENGINE (the separate `ml/` project). The backend
never computes or adjusts a risk score. This module only maps an integer score to
the agreed, deterministic severity band:

    LOW 0-24 | MEDIUM 25-49 | HIGH 50-74 | CRITICAL 75-100
"""
from __future__ import annotations

SEVERITY_BANDS = ((75, "CRITICAL"), (50, "HIGH"), (25, "MEDIUM"), (0, "LOW"))


def severity_for(risk_score: int) -> str:
    if isinstance(risk_score, bool) or not isinstance(risk_score, int) or not 0 <= risk_score <= 100:
        raise ValueError("risk_score must be an integer between 0 and 100")
    for lower_bound, label in SEVERITY_BANDS:
        if risk_score >= lower_bound:
            return label
    raise AssertionError("unreachable")  # pragma: no cover
