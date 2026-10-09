from ml.risk.engine import compute_risk, recommendation_for
from ml.risk.weights import CATALOG, make_indicator
from ml.schemas import severity_from_score


def test_severity_bands():
    expected = {0: "LOW", 24: "LOW", 25: "MEDIUM", 49: "MEDIUM", 50: "HIGH", 74: "HIGH", 75: "CRITICAL", 100: "CRITICAL"}
    for score, sev in expected.items():
        assert severity_from_score(score) == sev


def test_known_value_and_determinism():
    inds = [make_indicator("CREDENTIAL_REQUEST", "x"), make_indicator("URGENT_LANGUAGE", "y")]
    r1, r2 = compute_risk(inds, 0.9), compute_risk(list(reversed(inds)), 0.9)
    assert r1 == r2
    # 55*0.9 = 49.5 ; evidence = 14 + 7 + combo 5 = 26 ; total 75.5 -> 76
    assert r1["score"] == 76 and r1["severity"] == "CRITICAL"
    assert r1["breakdown"]["combo_items"][0]["points"] == 5


def test_no_indicators_no_model_is_zero():
    r = compute_risk([], None)
    assert r["score"] == 0 and r["severity"] == "LOW"


def test_probability_is_clamped():
    assert compute_risk([], 1.5)["score"] == 55 and compute_risk([], -1)["score"] == 0


def test_evidence_caps():
    inds = [make_indicator(c, "x") for c, v in CATALOG.items() if v[2] > 0 and v[3] == 0]
    assert compute_risk(inds, 0.0)["score"] == 45
    assert compute_risk(inds, None)["score"] == 100


def test_floor_for_executable_attachment():
    r = compute_risk([make_indicator("EXECUTABLE_ATTACHMENT", "x.exe")], None)
    assert r["score"] == 60 and r["severity"] == "HIGH" and r["breakdown"]["floor_applied"]["floor"] == 60


def test_adding_evidence_never_lowers_score():
    base = [make_indicator("URL_SHORTENER", "x")]
    more = base + [make_indicator("SUSPICIOUS_TLD", "y")]
    assert compute_risk(more, 0.3)["score"] >= compute_risk(base, 0.3)["score"]


def test_breakdown_explains_score():
    inds = [make_indicator("IP_BASED_URL", "x"), make_indicator("NO_HTTPS", "y")]
    r = compute_risk(inds, 0.5)
    b = r["breakdown"]
    assert b["evidence_points"] == sum(i["points"] for i in b["evidence_items"]) + sum(c["points"] for c in b["combo_items"])
    assert r["score"] == int(b["model_points"] + b["evidence_points"] + 0.5)


def test_recommendation_text_exists():
    assert "phishing" in recommendation_for("phishing", "HIGH").lower()