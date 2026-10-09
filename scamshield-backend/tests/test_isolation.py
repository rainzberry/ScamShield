"""TC10/TC11 - one user can never see or touch another user's data."""


def _scan(client, headers, text):
    res = client.post("/api/analyze/text", headers=headers, json={"text": text})
    assert res.status_code == 201
    return res.get_json()["scan"]["id"]


def test_tc11_user_isolation(client, auth, auth_b):
    a_scan = _scan(client, auth, "Verify your account immediately")
    b_scan = _scan(client, auth_b, "hello bob")

    a_list = client.get("/api/scans", headers=auth).get_json()
    b_list = client.get("/api/scans", headers=auth_b).get_json()
    assert [s["id"] for s in a_list["scans"]] == [a_scan]
    assert [s["id"] for s in b_list["scans"]] == [b_scan]

    # B cannot read A's scan or report (404, so IDs cannot be probed)
    for url in (f"/api/scans/{a_scan}", f"/api/reports/{a_scan}", f"/api/reports/{a_scan}?format=pdf"):
        res = client.get(url, headers=auth_b)
        assert res.status_code == 404, url
        assert res.get_json()["error"]["code"] == "NOT_FOUND"
        assert "phishing" not in res.get_data(as_text=True)

    # ... while A still can
    assert client.get(f"/api/scans/{a_scan}", headers=auth).status_code == 200
    assert client.get(f"/api/reports/{a_scan}", headers=auth).status_code == 200


def test_tc11_dashboard_is_per_user(client, auth, auth_b):
    for text in ("Verify your account now", "You have won a free prize", "hello"):
        _scan(client, auth, text)
    a = client.get("/api/dashboard/stats", headers=auth).get_json()
    b = client.get("/api/dashboard/stats", headers=auth_b).get_json()
    assert a["total_scans"] == 3
    assert b["total_scans"] == 0 and b["average_risk"] == 0 and b["recent_scans"] == []


def test_search_and_filter_never_cross_users(client, auth, auth_b):
    _scan(client, auth, "secret-token-xyz in alice's text")
    res = client.get("/api/scans?q=secret-token-xyz", headers=auth_b).get_json()
    assert res["pagination"]["total"] == 0
