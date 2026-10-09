"""TC04, TC05, TC07, TC08, TC09 - QR analysis through the API."""
import io

import pytest

from tests.helpers import blank_png, make_qr_png


def _upload(client, auth, data: bytes, name="qr.png", mime="image/png", field="file"):
    return client.post("/api/analyze/qr", headers=auth, content_type="multipart/form-data",
                       data={field: (io.BytesIO(data), name, mime)})


def test_tc04_legitimate_qr(client, auth, engine):
    res = _upload(client, auth, make_qr_png("https://www.example.org/docs"))
    assert res.status_code == 201, res.get_data(as_text=True)
    scan = res.get_json()["scan"]
    assert scan["scan_type"] == "qr" and scan["classification"] == "safe"
    assert scan["details"]["payload_type"] == "url"
    assert scan["details"]["decoded_payload"] == "https://www.example.org/docs"
    assert "Nothing was opened" in scan["details"]["safety_notice"]
    assert engine.calls[-1][:2] == ("payload", "url")


def test_tc05_suspicious_qr(client, auth):
    res = _upload(client, auth, make_qr_png("http://paypal-verify.xyz/login"))
    scan = res.get_json()["scan"]
    assert res.status_code == 201
    assert scan["classification"] == "phishing" and scan["severity"] == "CRITICAL"
    assert scan["details"]["payload_type"] == "url"


def test_tc07_upi_qr_parsing(client, auth):
    payload = "upi://pay?pa=merchant@okbank&pn=Test%20Shop&am=250.00&cu=INR&tr=TXN12345"
    res = _upload(client, auth, make_qr_png(payload))
    assert res.status_code == 201, res.get_data(as_text=True)
    scan = res.get_json()["scan"]
    parsed = scan["details"]["parsed"]
    assert scan["details"]["payload_type"] == "upi"
    assert parsed["upi_id"] == "merchant@okbank" and parsed["payee_name"] == "Test Shop"
    assert parsed["amount"] == "250.00" and parsed["currency"] == "INR"
    assert parsed["transaction_reference"] == "TXN12345"
    descriptions = [i["description"] for i in scan["indicators"]]
    assert "Merchant identity could not be independently verified." in descriptions
    assert scan["classification"] == "safe"           # unverifiable identity alone is NOT fraud
    info = [i for i in scan["indicators"] if i["source"] == "backend"]
    assert info and all(i["severity"] == "INFO" and i["weight"] is None for i in info)


def test_wifi_qr_password_is_redacted_and_not_connected(client, auth):
    res = _upload(client, auth, make_qr_png("WIFI:T:WPA;S:CafeNet;P:hunter2secret;;"))
    assert res.status_code == 201
    text = res.get_data(as_text=True)
    assert "hunter2secret" not in text
    assert res.get_json()["scan"]["details"]["payload_type"] == "wifi"


def test_tc08_invalid_qr(client, auth):
    res = _upload(client, auth, blank_png())                       # valid image, no QR
    assert res.status_code == 422 and res.get_json()["error"]["code"] == "QR_NOT_DECODABLE"
    res = _upload(client, auth, b"this is not an image", name="x.png")
    assert res.status_code == 400 and res.get_json()["error"]["code"] == "INVALID_IMAGE"
    assert client.get("/api/scans", headers=auth).get_json()["pagination"]["total"] == 0


def test_tc09_oversized_upload(client, auth, app):
    limit = app.config["QR_MAX_UPLOAD_BYTES"]
    res = _upload(client, auth, b"0" * (limit + 1))
    assert res.status_code == 413 and res.get_json()["error"]["code"] == "FILE_TOO_LARGE"
    huge = b"0" * (app.config["MAX_CONTENT_LENGTH"] + 10)          # blocked by Flask itself
    res = _upload(client, auth, huge)
    assert res.status_code == 413 and res.get_json()["success"] is False


@pytest.mark.parametrize("name,mime", [
    ("evil.exe", "application/octet-stream"), ("qr.svg", "image/svg+xml"),
    ("qr.png", "text/html"), ("qr.php", "image/png"), ("noextension", "image/png"),
])
def test_unsupported_formats_rejected(client, auth, name, mime):
    res = _upload(client, auth, make_qr_png("https://example.org"), name=name, mime=mime)
    assert res.status_code == 415 and res.get_json()["error"]["code"] == "UNSUPPORTED_FILE_TYPE"


def test_path_traversal_filename_is_neutralised(client, auth):
    res = _upload(client, auth, make_qr_png("https://example.org"), name="../../etc/passwd.png")
    assert res.status_code == 201
    name = res.get_json()["scan"]["details"]["filename"]
    assert "/" not in name and ".." not in name and name.endswith(".png")


def test_qr_analysis_makes_no_network_connections(client, auth, monkeypatch):
    import socket

    def _no_network(*a, **k):
        raise AssertionError("QR analysis must never open network connections")

    monkeypatch.setattr(socket.socket, "connect", _no_network)
    res = _upload(client, auth, make_qr_png("http://paypal-verify.xyz/login"))
    assert res.status_code == 201
