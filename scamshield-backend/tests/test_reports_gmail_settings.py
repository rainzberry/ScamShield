"""Reports (JSON + PDF), demo Gmail mode and settings."""


def _scan(client, auth):
    return client.post("/api/analyze/email", headers=auth, json={
        "sender": "a@b.top", "subject": "Verify <b>now</b> & win",
        "body": "Verify your account: http://secure-bank.top/verify-login"}).get_json()["scan"]


def test_json_report_contains_everything_required(client, auth):
    scan = _scan(client, auth)
    res = client.get(f"/api/reports/{scan['id']}", headers=auth)
    assert res.status_code == 200
    r = res.get_json()["report"]
    for key in ("report_id", "metadata", "classification", "risk_score", "confidence", "severity",
                "indicators", "evidence", "explanation", "recommendation", "model_version",
                "timestamp", "generated_at"):
        assert key in r, key
    assert r["metadata"]["scan_id"] == scan["id"] and r["risk_score"] == scan["risk_score"]
    assert r["evidence"], "indicator evidence should be listed"


def test_pdf_report_is_a_real_pdf_and_escapes_markup(client, auth):
    scan = _scan(client, auth)
    res = client.get(f"/api/reports/{scan['id']}?format=pdf", headers=auth)
    assert res.status_code == 200 and res.mimetype == "application/pdf"
    assert res.data.startswith(b"%PDF") and len(res.data) > 1000
    assert "attachment" in res.headers["Content-Disposition"]


def test_report_bad_format(client, auth):
    scan = _scan(client, auth)
    assert client.get(f"/api/reports/{scan['id']}?format=exe", headers=auth).status_code == 400
    assert client.get("/api/reports/does-not-exist", headers=auth).status_code == 404


def test_demo_gmail_is_labelled_and_never_pretends_to_be_real(client, auth):
    assert client.get("/api/gmail/messages", headers=auth).status_code == 400   # not connected yet
    status = client.post("/api/gmail/demo/connect", headers=auth).get_json()["gmail"]
    assert status["is_demo"] is True and status["oauth_supported"] is False
    data = client.get("/api/gmail/messages", headers=auth).get_json()
    assert data["is_demo"] is True and "DEMO" in data["label"]
    assert all(m["is_demo"] for m in data["messages"])
    assert all("classification" not in m for m in data["messages"])             # no pre-baked verdicts
    # a demo message goes through the REAL analysis pipeline
    msg = data["messages"][1]
    res = client.post("/api/analyze/email", headers=auth, json={
        "sender": msg["sender"], "subject": msg["subject"], "body": msg["body"],
        "url": msg["url"], "source": "gmail_demo"})
    assert res.status_code == 201 and res.get_json()["scan"]["details"]["source"] == "gmail_demo"
    assert client.get("/api/gmail/oauth/start", headers=auth).status_code == 501
    assert client.post("/api/gmail/disconnect", headers=auth).get_json()["gmail"]["connected"] is False


def test_settings_roundtrip(client, auth):
    assert client.get("/api/settings", headers=auth).get_json()["settings"]["theme"] == "system"
    res = client.put("/api/settings", headers=auth, json={"theme": "dark", "display_name": " Alice "})
    assert res.get_json()["settings"] == {"display_name": "Alice", "theme": "dark",
                                          "email_notifications": False}
    assert client.put("/api/settings", headers=auth, json={"theme": "neon"}).status_code == 400


def test_health_and_model_info(client, auth):
    h = client.get("/api/health").get_json()
    assert h["success"] is True and h["status"] == "ok" and h["database"] == "ok"
    assert client.get("/api/model/info", headers=auth).get_json()["model"]["available"] is True
