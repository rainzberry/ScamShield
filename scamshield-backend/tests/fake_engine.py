"""TEST DOUBLE for the ML engine.

This is NOT a classifier and is never imported by application code. Its only job is to give
the API tests a deterministic stand-in with the same interface as app.services.ml_adapter.MLEngine
so the backend's plumbing (validation, persistence, isolation, contracts) can be tested without
the real ML project. The real ML engine is exercised by the ML project's own tests.
"""
from __future__ import annotations

PHISH = ("verify your account", "suspended", "verify-login", "paypal-verify", "update your password",
         "kyc", ".top/", ".xyz/login")
SPAM = ("you have won", "free prize", "claim your reward", "limited offer", "free gift")


def _verdict(text: str) -> dict:
    t = text.lower()
    hits = [m for m in PHISH if m in t]
    if hits:
        return {"classification": "phishing", "risk_score": 91, "confidence": 0.96,
                "indicators": [{"type": "test_marker", "description": f"matched '{h}'",
                                "severity": "HIGH", "weight": 0.3, "evidence": h} for h in hits],
                "explanation": {"summary": "Test double: phishing markers present."},
                "recommendation": "Do not click links or share credentials.",
                "model_version": "test-double-0.1"}
    hits = [m for m in SPAM if m in t]
    if hits:
        return {"classification": "spam", "risk_score": 58, "confidence": 0.88,
                "indicators": [{"type": "test_marker", "description": f"matched '{h}'",
                                "severity": "MEDIUM", "weight": 0.2, "evidence": h} for h in hits],
                "explanation": {"summary": "Test double: spam markers present."},
                "recommendation": "Ignore and delete.", "model_version": "test-double-0.1"}
    return {"classification": "safe", "risk_score": 4, "confidence": 0.97, "indicators": [],
            "explanation": {"summary": "Test double: no markers."},
            "recommendation": "No action needed.", "model_version": "test-double-0.1"}


class FakeEngine:
    def __init__(self):
        self.calls: list[tuple] = []

    def preload(self):
        pass

    def analyze_text(self, text, context=None):
        self.calls.append(("text", text))
        return _verdict(text)

    def analyze_url(self, url, context=None):
        self.calls.append(("url", url))
        return _verdict(url)

    def analyze_payload(self, payload, payload_type=None, parsed=None, context=None):
        self.calls.append(("payload", payload_type, payload))
        return _verdict(payload)

    def model_info(self):
        return {"available": True, "analyzers": {k: {"available": True} for k in ("text", "url", "payload")}}
