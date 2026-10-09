import json

import pytest

from ml.qr_analysis.payload import parse_payload, parse_upi
from ml.schemas import InvalidInputError

UPI = "upi://pay?pa=merchant@okaxis&pn=Shop%20One&am=250&cu=INR&tn=Order%2012"


@pytest.mark.parametrize("raw,expected", [
    ("https://example.com/a", "url"), ("www.example.com/x", "url"), (UPI, "upi"),
    ("mailto:a@b.com?subject=Hi", "email"), ("tel:+911234567890", "phone"),
    ("WIFI:T:WPA;S:Home;P:pw;;", "wifi"), ("BEGIN:VCARD\nFN:A\nEND:VCARD", "vcard"),
    ("smsto:+123456789:hello there", "sms"), ("hello there friend", "text"),
    ("geo:12.3,45.6", "unknown"), ("javascript:alert(1)", "unknown"),
])
def test_payload_classification(raw, expected):
    assert parse_payload(raw).type == expected


def test_upi_parsing_fields():
    p = parse_payload(UPI)
    assert p.fields["pa"] == "merchant@okaxis" and p.fields["pn"] == "Shop One"
    assert p.fields["am"] == "250" and p.fields["cu"] == "INR" and p.fields["tn"] == "Order 12"
    assert parse_upi("upi://pay?pa=a@b&pa=c@d")["duplicate_params"] == ["pa"]


def test_upi_is_not_called_fraud_just_because_unverified(rules_engine):
    r = rules_engine.analyze_qr_payload(UPI)
    codes = {i["code"] for i in r["indicators"]}
    assert r["scan_type"] == "qr" and r["payload"]["type"] == "upi"
    assert "UPI_MERCHANT_UNVERIFIED" in codes
    ev = next(i["evidence"] for i in r["indicators"] if i["code"] == "UPI_MERCHANT_UNVERIFIED")
    assert "Merchant identity could not be independently verified." in ev
    assert r["risk_score"] < 25 and r["classification"] == "unverified"
    assert r["confidence"] is None and r["model_used"] is False


def test_upi_red_flags(rules_engine):
    r = rules_engine.analyze_qr_payload("upi://pay?pa=a@okaxis&pa=b@okaxis&pn=Refund%20Support&am=20000&tn=cashback%20reward")
    codes = {i["code"] for i in r["indicators"]}
    assert {"UPI_DUPLICATE_PARAMS", "UPI_PAYEE_KEYWORDS", "UPI_NOTE_REWARD_LANGUAGE", "UPI_HIGH_AMOUNT"} <= codes
    r2 = rules_engine.analyze_qr_payload("upi://pay?pa=notavpa&pn=X")
    assert "UPI_INVALID_VPA" in {i["code"] for i in r2["indicators"]}


def test_wifi_password_never_leaks(rules_engine):
    r = rules_engine.analyze_qr_payload("WIFI:T:WPA;S:Home;P:secretpass;;")
    assert r["payload"]["type"] == "wifi" and "secretpass" not in json.dumps(r)
    r2 = rules_engine.analyze_qr_payload("WIFI:T:nopass;S:Cafe;;")
    assert "WIFI_OPEN_NETWORK" in {i["code"] for i in r2["indicators"]}


def test_url_payload_is_routed_through_url_analysis(rules_engine):
    r = rules_engine.analyze_qr_payload("http://192.168.1.1/login")
    assert r["scan_type"] == "qr" and r["payload"]["type"] == "url"
    assert "IP_BASED_URL" in {i["code"] for i in r["indicators"]}


def test_text_payload_is_routed_through_text_analysis(engine):
    r = engine.analyze_qr_payload("Your account will be suspended within 24 hours. Verify your password now.")
    assert r["scan_type"] == "qr" and r["payload"]["type"] == "text"
    assert {"URGENT_LANGUAGE", "CREDENTIAL_REQUEST"} <= {i["code"] for i in r["indicators"]}


def test_dangerous_scheme(rules_engine):
    r = rules_engine.analyze_qr_payload("javascript:alert(1)")
    assert r["classification"] == "malicious" and r["risk_score"] >= 60


@pytest.mark.parametrize("bad", ["", "   ", None, 7])
def test_empty_or_wrong_type_payload(rules_engine, bad):
    with pytest.raises(InvalidInputError):
        rules_engine.analyze_qr_payload(bad)