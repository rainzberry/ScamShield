from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

SEVERITY_RANK = {"INFO": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}


class InvalidInputError(ValueError):
    """Raised for empty / wrongly typed input. Backend should map to HTTP 400."""


class MalformedURLError(ValueError):
    """Raised when a URL cannot be parsed."""


def severity_from_score(score: int) -> str:
    if score >= 75:
        return "CRITICAL"
    if score >= 50:
        return "HIGH"
    if score >= 25:
        return "MEDIUM"
    return "LOW"


@dataclass(frozen=True)
class Indicator:
    code: str
    label: str
    severity: str
    evidence: str
    source: str = "rule"      # "rule" or "model"
    points: int = 0           # contribution to the evidence component of the risk score
    floor: int = 0            # minimum risk score this indicator enforces

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "label": self.label,
            "severity": self.severity,
            "evidence": self.evidence,
            "source": self.source,
            "points": self.points,
        }