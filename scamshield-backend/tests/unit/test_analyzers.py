"""Pure unit tests (no Flask app): QR decode, payload typing, UPI parsing, URL validation."""
import pytest

from app.analyzers.payload import classify_payload, informational_indicators
from app.analyzers.qr_decoder import decode_qr_image
from app.analyzers.upi import VERIFICATION_NOTE, parse_upi
from app.errors.exceptions import QRDecodeError
from app.utils.urls import normalize_url
from tests.helpers import blank_png, make_qr_png


def test_qr_roundtrip_decodes_url_text_and_upi():
    for text in ("https://www.example.org/docs", "hello world, plain text",
                 "upi://pay?pa=shop@okbank&pn=Shop&am=10.50&cu=INR"):
        assert decode_qr_image(make_qr_png(text)).payload == text


def test_qr_decoder_raises_on_image_without_qr():
    with pytest.raises(QRDecodeError):
        decode_qr_image(blank_png())


def test_tc07_upi_parsing_extracts_all_fields():
    p = parse_upi("upi://pay?pa=merchant@okbank&pn=Test%20Shop&am=250.00&cu=INR&tr=TXN12345&tn=Order%201")
    assert p["upi_id"] == "merchant@okbank" and p["upi_id_valid"] is True
    assert p["payee_name"] == "Test Shop" and p["amount"] == "250.00" and p["currency"] == "INR"
    assert p["transaction_reference"] == "TXN12345" and p["transaction_note"] == "Order 1"
    assert p["verification_note"] == VERIFICATION_NOTE and p["warnings"] == []


def test_upi_odd_values_are_noted_not_called_fraud():
    p = parse_upi("upi://pay?pa=bad&am=-5")
    assert p["upi_id_valid"] is False and p["amount_valid"] is False
    assert not any("fraud" in w.lower() or "scam" in w.lower() for w in p["warnings"])
    assert parse_upi("upi://pay?pn=NoId")["upi_id"] is None
    assert parse_upi("upi://pay")["amount"] is None


def test_payload_type_detection():
    expected = {
        "https://example.org": "url", "www.example.org/a": "url", "example.com:8080/x": "url",
        "upi://pay?pa=a@b": "upi", "WIFI:T:WPA;S:n;P:p;;": "wifi", "tel:+911234567890": "phone",
        "mailto:a@b.com": "email", "SMSTO:123:hi": "sms", "geo:1,2": "geo",
        "BEGIN:VCARD\nFN:X": "contact", "bitcoin:abc": "crypto", "javascript:alert(1)": "other_uri",
        "ftp://x.com": "other_uri", "Note: buy milk": "text", "just some text": "text",
    }
    for payload, kind in expected.items():
        assert classify_payload(payload).payload_type == kind, payload


def test_wifi_password_is_redacted():
    info = classify_payload("WIFI:T:WPA;S:Cafe;P:hunter2;;")
    assert "hunter2" not in info.display_payload and "hunter2" not in info.analysis_payload
    assert info.parsed == {"ssid": "Cafe", "security": "WPA", "hidden": False, "password_present": True}


def test_informational_indicators_are_info_only():
    for payload in ("upi://pay?pa=a@okbank&am=5", "WIFI:T:WPA;S:n;P:p;;", "javascript:alert(1)"):
        notes = informational_indicators(classify_payload(payload))
        assert notes and all(n["severity"] == "INFO" and n["weight"] is None for n in notes)


def test_url_validation():
    assert normalize_url("example.org") == "http://example.org"
    assert normalize_url(" https://a.com/x?y=1 ") == "https://a.com/x?y=1"
    for bad in ("", "javascript:alert(1)", "data:text/html,x", "ftp://a.com", "http://", "a b.com",
                "http://a.com:99999", "x" * 2100):
        with pytest.raises(ValueError):
            normalize_url(bad)
