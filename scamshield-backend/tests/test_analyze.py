"""TC01, TC02, TC03, TC06, TC15 + response-contract checks."""
import pytest

from app import create_app
from app.config import TestConfig
from tests.conftest import register
from tests.fake_engine import FakeEngine

CONTRACT_KEYS = {"id", "scan_type", "classification", "risk_score", "confidence", "severity",
                 "indicators", "explanation", "recommendation", "created_at", "model_version"}


def _assert_contract(res, scan_type):
    assert res.status_code == 201, res.get_data(as_text=True)
    body = res.get_json()
    assert body["success"] is True
    scan = body["scan"]
    assert CONTRACT_KEYS <= set(scan)
    assert scan["scan_type"] == scan_type
    assert isinstance(scan["indicators"], list) and isinstance(scan["explanation"], dict)
    assert 0 <= scan["risk_score"] <= 100 and 0 <= scan["confidence"] <= 1
    assert scan["created_at"].endswith("Z")
    return scan


def test_tc01_legitimate_email(client, auth, engine):
    res = client.post("/api/analyze/email", headers=auth, json={
        "sender": "registrar@university.edu", "subject": "Timetable",
        "body": "The semester timetable is on the portal. Regards, Registrar."})
    scan = _assert_contract(res, "email")
    assert scan["classification"] == "safe" and scan["severity"] == "LOW"
    assert engine.calls and engine.calls[0][0] == "text"       # the real content reached the engine
    assert "timetable" in engine.calls[0][1].lower()


def test_tc02_phishing_email(client, auth):
    res = client.post("/api/analyze/email", headers=auth, json={
        "sender": "alert@secure-bank.top", "subject": "Account suspended",
        "body": "Your account is suspended. Verify your account now: http://secure-bank.top/verify-login",
        "attachments": [{"filename": "form.html", "content_type": "text/html", "size": 1200}]})
    scan = _assert_contract(res, "email")
    assert scan["classification"] == "phishing" and scan["severity"] == "CRITICAL"
    assert scan["risk_score"] == 91 and len(scan["indicators"]) >= 1
    assert scan["model_version"] == "test-double-0.1"


def test_email_with_explicit_url_uses_highest_risk_component(client, auth, engine):
    res = client.post("/api/analyze/email", headers=auth, json={
        "sender": "friend@example.com", "subject": "Look", "body": "Check this out",
        "url": "http://secure-bank.top/verify-login"})
    scan = _assert_contract(res, "email")
    assert scan["classification"] == "phishing"
    assert scan["explanation"]["combination_policy"] == "highest_risk_component"
    assert {c[0] for c in engine.calls} == {"text", "url"}


def test_tc03_suspicious_url_is_analyzed_not_fetched(client, auth, engine, monkeypatch):
    import socket

    def _no_network(*a, **k):
        raise AssertionError("The backend must never open a network connection to a submitted URL")

    monkeypatch.setattr(socket.socket, "connect", _no_network)
    res = client.post("/api/analyze/url", headers=auth, json={"url": "http://paypal-verify.xyz/login"})
    scan = _assert_contract(res, "url")
    assert scan["classification"] == "phishing" and scan["severity"] == "CRITICAL"
    assert engine.calls[-1] == ("url", "http://paypal-verify.xyz/login")


def test_url_without_scheme_is_normalised(client, auth, engine):
    res = client.post("/api/analyze/url", headers=auth, json={"url": "example.org/page"})
    _assert_contract(res, "url")
    assert engine.calls[-1] == ("url", "http://example.org/page")


def test_tc06_spam_text(client, auth):
    res = client.post("/api/analyze/text", headers=auth, json={
        "text": "Congratulations! You have won a free prize. Claim your reward now!"})
    scan = _assert_contract(res, "text")
    assert scan["classification"] == "spam" and scan["severity"] == "HIGH"


def test_scan_is_persisted_and_retrievable(client, auth):
    created = client.post("/api/analyze/text", headers=auth, json={"text": "hello there"}).get_json()["scan"]
    fetched = client.get(f"/api/scans/{created['id']}", headers=auth).get_json()["scan"]
    assert fetched["id"] == created["id"] and fetched["input"] == {"text": "hello there"}
    assert fetched["classification"] == created["classification"]


def test_tc15_model_unavailable_returns_503_and_stores_nothing(client_no_ml, auth_no_ml):
    res = client_no_ml.post("/api/analyze/text", headers=auth_no_ml, json={"text": "anything"})
    assert res.status_code == 503
    body = res.get_json()
    assert body == {"success": False, "error": {"code": "MODEL_UNAVAILABLE", "message": body["error"]["message"]}}
    listing = client_no_ml.get("/api/scans", headers=auth_no_ml).get_json()
    assert listing["pagination"]["total"] == 0                  # no fake result was persisted
    health = client_no_ml.get("/api/health").get_json()
    assert health["status"] == "degraded" and health["ml"]["available"] is False


class _BrokenEngine(FakeEngine):
    def __init__(self, payload):
        super().__init__()
        self.payload = payload

    def analyze_text(self, text, context=None):
        return self.payload


@pytest.mark.parametrize("bad", [
    {"classification": "weird", "risk_score": 10, "confidence": 0.5},
    {"classification": "safe", "risk_score": 150, "confidence": 0.5},
    {"classification": "safe", "risk_score": 10, "confidence": 7},
    {"classification": "safe", "risk_score": "high", "confidence": 0.5},
    {"classification": "safe", "confidence": 0.5},
])
def test_invalid_ml_response_is_rejected_not_stored(bad):
    app = create_app(TestConfig, ml_engine=_BrokenEngine(bad))
    c = app.test_client()
    h = register(c)
    res = c.post("/api/analyze/text", headers=h, json={"text": "hello"})
    assert res.status_code == 502 and res.get_json()["error"]["code"] == "ML_INVALID_RESPONSE"
    assert c.get("/api/scans", headers=h).get_json()["pagination"]["total"] == 0


def test_backend_owns_severity_even_if_ml_sends_a_different_one():
    payload = {"classification": "phishing", "risk_score": 91, "confidence": 0.9,
               "severity": "LOW", "recommendation": "x"}
    app = create_app(TestConfig, ml_engine=_BrokenEngine(payload))
    c = app.test_client()
    h = register(c)
    scan = c.post("/api/analyze/text", headers=h, json={"text": "hello"}).get_json()["scan"]
    assert scan["severity"] == "CRITICAL"


@pytest.fixture()
def client_no_ml():
    """Real MLEngine pointed at modules that do not exist => genuinely unavailable."""
    class NoMLConfig(TestConfig):
        ML_TEXT_ANALYZER = "does_not_exist.text:analyze_text"
        ML_URL_ANALYZER = "does_not_exist.url:analyze_url"
        ML_PAYLOAD_ANALYZER = "does_not_exist.qr:analyze_payload"
    return create_app(NoMLConfig).test_client()


@pytest.fixture()
def auth_no_ml(client_no_ml):
    return register(client_no_ml)
