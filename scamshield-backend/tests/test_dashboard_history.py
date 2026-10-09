"""TC13 (dashboard stats) and TC14 (history pagination/filter/sort/search)."""

TEXTS = {
    "phishing": "Verify your account immediately",
    "spam": "You have won a free prize",
    "safe": "Lunch at noon?",
}


def _post(client, auth, text):
    res = client.post("/api/analyze/text", headers=auth, json={"text": text})
    assert res.status_code == 201
    return res.get_json()["scan"]


def test_tc13_dashboard_stats_are_computed_from_the_database(client, auth):
    empty = client.get("/api/dashboard/stats", headers=auth).get_json()
    assert empty["total_scans"] == 0 and empty["average_risk"] == 0 and empty["recent_scans"] == []

    risks = []
    for kind, n in (("safe", 3), ("spam", 2), ("phishing", 4)):
        for i in range(n):
            risks.append(_post(client, auth, f"{TEXTS[kind]} #{i}")["risk_score"])
    client.post("/api/analyze/url", headers=auth, json={"url": "http://example.org"})
    risks.append(4)

    stats = client.get("/api/dashboard/stats", headers=auth).get_json()
    assert stats["success"] is True
    assert stats["total_scans"] == 10
    assert (stats["safe"], stats["spam"], stats["phishing"], stats["malicious"]) == (4, 2, 4, 0)
    assert stats["average_risk"] == round(sum(risks) / len(risks), 1)
    assert stats["by_scan_type"] == {"email": 0, "text": 9, "url": 1, "qr": 0}
    assert sum(stats["by_severity"].values()) == 10
    assert len(stats["recent_scans"]) == 5
    assert stats["trend"] and stats["trend"][-1]["count"] == 10


def test_tc14_pagination(client, auth):
    for i in range(25):
        _post(client, auth, f"message number {i}")
    p1 = client.get("/api/scans?per_page=10&page=1", headers=auth).get_json()
    p3 = client.get("/api/scans?per_page=10&page=3", headers=auth).get_json()
    p4 = client.get("/api/scans?per_page=10&page=4", headers=auth).get_json()
    assert p1["pagination"] == {"page": 1, "per_page": 10, "total": 25, "pages": 3,
                                "has_next": True, "has_prev": False}
    assert len(p1["scans"]) == 10 and len(p3["scans"]) == 5 and p4["scans"] == []
    assert p3["pagination"]["has_next"] is False
    ids = [s["id"] for page in (1, 2, 3)
           for s in client.get(f"/api/scans?per_page=10&page={page}", headers=auth).get_json()["scans"]]
    assert len(ids) == len(set(ids)) == 25                       # no overlap, nothing missing
    assert "explanation" not in p1["scans"][0]                   # compact list items


def test_tc14_filters_sort_and_search(client, auth):
    _post(client, auth, "Verify your account immediately")
    _post(client, auth, "You have won a free prize")
    _post(client, auth, "Lunch at noon?")
    client.post("/api/analyze/url", headers=auth, json={"url": "http://example.org/invoice"})

    def get(qs):
        return client.get(f"/api/scans?{qs}", headers=auth).get_json()

    assert {s["classification"] for s in get("classification=phishing")["scans"]} == {"phishing"}
    assert get("scan_type=url")["pagination"]["total"] == 1
    assert get("classification=all")["pagination"]["total"] == 4
    asc = [s["risk_score"] for s in get("sort=risk_score&order=asc")["scans"]]
    desc = [s["risk_score"] for s in get("sort=risk_score&order=desc")["scans"]]
    assert asc == sorted(asc) and desc == sorted(desc, reverse=True)
    assert get("q=invoice")["pagination"]["total"] == 1
    assert get("q=%25")["pagination"]["total"] == 0              # LIKE wildcards are escaped
    dates = [s["created_at"] for s in get("sort=created_at&order=desc")["scans"]]
    assert dates == sorted(dates, reverse=True)
