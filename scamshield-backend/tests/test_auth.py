"""TC10 (unauthorized), TC16 (authentication), TC17 (malformed requests)."""
import pytest

from app.extensions import db
from app.models.user import User
from tests.conftest import PASSWORD, register


def test_tc16_register_login_me_logout(client, app):
    res = client.post("/api/auth/register", json={"email": "Carol@Example.com", "password": PASSWORD})
    assert res.status_code == 201
    body = res.get_json()
    assert body["success"] is True and body["user"]["email"] == "carol@example.com"
    assert "password_hash" not in body["user"]

    with app.app_context():                       # password is hashed, never plaintext
        user = db.session.query(User).filter_by(email="carol@example.com").one()
        assert user.password_hash != PASSWORD and PASSWORD not in user.password_hash
        assert user.password_hash.startswith("pbkdf2:")

    login = client.post("/api/auth/login", json={"email": "carol@example.com", "password": PASSWORD})
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.get_json()['access_token']}"}
    assert client.get("/api/auth/me", headers=headers).status_code == 200

    assert client.post("/api/auth/logout", headers=headers).status_code == 200
    after = client.get("/api/auth/me", headers=headers)       # token revoked
    assert after.status_code == 401
    assert after.get_json()["error"]["code"] == "TOKEN_REVOKED"


def test_login_wrong_password_and_unknown_user_look_identical(client):
    register(client, "dave@example.com")
    bad_pw = client.post("/api/auth/login", json={"email": "dave@example.com", "password": "WrongPass123"})
    unknown = client.post("/api/auth/login", json={"email": "nobody@example.com", "password": "WrongPass123"})
    assert bad_pw.status_code == unknown.status_code == 401
    assert bad_pw.get_json() == unknown.get_json()


def test_duplicate_email_rejected(client):
    register(client, "eve@example.com")
    res = client.post("/api/auth/register", json={"email": "EVE@example.com", "password": PASSWORD})
    assert res.status_code == 409 and res.get_json()["error"]["code"] == "EMAIL_IN_USE"


@pytest.mark.parametrize("payload", [
    {"email": "not-an-email", "password": PASSWORD},
    {"email": "a@example.com", "password": "short1"},
    {"email": "a@example.com", "password": "onlyletters"},
    {"email": "a@example.com", "password": "12345678"},
    {"email": "a@example.com"},
])
def test_register_validation(client, payload):
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 400
    assert res.get_json()["error"]["code"] == "VALIDATION_ERROR"
    assert PASSWORD not in res.get_data(as_text=True)


@pytest.mark.parametrize("method,url", [
    ("get", "/api/scans"), ("get", "/api/scans/abc"), ("get", "/api/dashboard/stats"),
    ("get", "/api/reports/abc"), ("post", "/api/analyze/text"), ("post", "/api/analyze/email"),
    ("post", "/api/analyze/url"), ("post", "/api/analyze/qr"), ("get", "/api/auth/me"),
    ("post", "/api/auth/logout"), ("get", "/api/settings"), ("get", "/api/gmail/status"),
])
def test_tc10_unauthorized_access(client, method, url):
    res = getattr(client, method)(url)
    assert res.status_code == 401
    body = res.get_json()
    assert body["success"] is False and body["error"]["code"] == "AUTHENTICATION_ERROR"


def test_tc10_garbage_token(client):
    res = client.get("/api/scans", headers={"Authorization": "Bearer not.a.jwt"})
    assert res.status_code == 401 and res.get_json()["error"]["code"] == "INVALID_TOKEN"


def test_tc17_malformed_requests(client, auth):
    h = auth
    cases = [
        client.post("/api/analyze/text", data="not json", headers=h),
        client.post("/api/analyze/text", json=["a", "list"], headers=h),
        client.post("/api/analyze/text", json={}, headers=h),
        client.post("/api/analyze/text", json={"text": "   "}, headers=h),
        client.post("/api/analyze/text", json={"text": "x" * 50_001}, headers=h),
        client.post("/api/analyze/url", json={"url": "javascript:alert(1)"}, headers=h),
        client.post("/api/analyze/url", json={"url": "http://exa mple.com"}, headers=h),
        client.post("/api/analyze/email", json={"subject": "no body"}, headers=h),
        client.post("/api/analyze/email", json={"body": "hi", "url": "ftp://x.com/a"}, headers=h),
        client.post("/api/analyze/email", json={"body": "hi", "attachments": "nope"}, headers=h),
        client.get("/api/scans?page=0", headers=h),
        client.get("/api/scans?per_page=1000", headers=h),
        client.get("/api/scans?classification=bogus", headers=h),
        client.get("/api/scans?sort=password", headers=h),
        client.post("/api/analyze/qr", headers=h),
    ]
    for res in cases:
        assert res.status_code == 400, res.get_data(as_text=True)
        body = res.get_json()
        assert body["success"] is False and body["error"]["code"] == "VALIDATION_ERROR"
        assert "Traceback" not in res.get_data(as_text=True)


def test_unknown_route_and_method_use_error_envelope(client):
    assert client.get("/api/nope").get_json()["error"]["code"] == "NOT_FOUND"
    assert client.delete("/api/health").status_code == 405


def test_security_headers_present(client):
    res = client.get("/api/health")
    assert res.headers["X-Content-Type-Options"] == "nosniff"
    assert res.headers["X-Frame-Options"] == "DENY"
    assert "X-Request-ID" in res.headers
