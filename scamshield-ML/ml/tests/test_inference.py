import math

import pytest

from ml.explainability.text_explainer import explain_text
from ml.explainability.url_explainer import explain_url
from ml.inference.model_store import load_bundle
from ml.preprocessing.text_cleaning import clean_text
from ml.schemas import InvalidInputError, severity_from_score
from ml.url_analysis.features import FEATURE_NAMES, extract_url_features

CONTRACT = {"scan_type", "classification", "risk_score", "confidence", "severity", "indicators",
            "explanation", "recommendation", "model_version"}
PHISH = dict(
    subject="Verify your account immediately",
    body="Your account will be suspended within 24 hours. Click here to verify your password: http://paypa1-secure.xyz/login",
    sender="PayPal Support <help@gmail.com>", attachments=["invoice.pdf.exe"])


def test_models_load_with_metadata(tiny_models_dir):
    for d in ("text_model", "url_model"):
        m = load_bundle(tiny_models_dir / d)
        assert m is not None and m.version != "unknown"
        assert m.metadata["data_fingerprint"] and "validation_metrics" in m.metadata


def test_email_result_contract_and_ranges(engine):
    r = engine.analyze_email(**PHISH)
    assert CONTRACT <= set(r)
    assert 0 <= r["risk_score"] <= 100 and r["severity"] == severity_from_score(r["risk_score"])
    assert 0.5 <= r["confidence"] <= 1.0 and r["model_version"] == engine.text_model.version
    assert {"summary", "model_features", "rule_features"} <= set(r["explanation"])
    codes = {i["code"] for i in r["indicators"]}
    assert {"URGENT_LANGUAGE", "CREDENTIAL_REQUEST", "SUSPICIOUS_SENDER", "DOUBLE_EXTENSION_ATTACHMENT", "LOOKALIKE_DOMAIN"} <= codes
    assert r["risk_score"] >= 60 and r["classification"] == "malicious"
    for ind in r["indicators"]:
        assert {"code", "label", "severity", "evidence"} <= set(ind) and ind["evidence"]


def test_results_are_deterministic(engine):
    assert engine.analyze_email(**PHISH) == engine.analyze_email(**PHISH)
    u = "http://paypa1-secure-login.xyz/verify/account"
    assert engine.analyze_url(u) == engine.analyze_url(u)


def test_analysis_does_not_retrain_or_touch_artifacts(engine, tiny_models_dir):
    p = tiny_models_dir / "text_model" / "model.joblib"
    before = p.stat().st_mtime_ns
    engine.analyze_text("Verify your password now"); engine.analyze_url("http://192.168.1.1/login")
    assert p.stat().st_mtime_ns == before


def test_engine_is_cached(tiny_models_dir):
    from ml.inference import get_engine
    assert get_engine(tiny_models_dir) is get_engine(tiny_models_dir)


def test_text_explanation_is_consistent(tiny_models_dir):
    model = load_bundle(tiny_models_dir / "text_model")
    ex = explain_text(model, clean_text("Verify your password now or your account will be suspended"))
    assert ex["n_active_features"] > 0 and ex["features"]
    assert abs(1 / (1 + math.exp(-ex["logit"])) - ex["probability_suspicious"]) < 1e-9
    for f in ex["features"]:
        assert {"feature", "analyzer", "tfidf", "coefficient", "contribution", "direction"} <= set(f)
        assert abs(f["contribution"] - f["tfidf"] * f["coefficient"]) < 1e-3
        assert (f["contribution"] > 0) == (f["direction"] == "suspicious")


def test_url_explanation_uses_real_features(tiny_models_dir):
    model = load_bundle(tiny_models_dir / "url_model")
    feats = extract_url_features("http://paypa1-secure-login.xyz/verify/account")
    ex = explain_url(model, feats)
    assert 0 <= ex["probability_phishing"] <= 1
    for row in ex["features"]:
        assert row["feature"] in FEATURE_NAMES and row["value"] == feats[row["feature"]] and row["contribution"] != 0


def test_url_result_has_model_and_rule_evidence(engine):
    r = engine.analyze_url("http://paypa1-secure-login.xyz/verify/account")
    assert r["model_used"] and r["explanation"]["extracted_features"]["brand_lookalike"] == 1
    assert "LOOKALIKE_DOMAIN" in {i["code"] for i in r["indicators"]}


def test_rules_only_mode_without_models(rules_engine):
    r = rules_engine.analyze_email(subject="Lunch", body="Agenda attached for tomorrow's meeting.")
    assert r["confidence"] is None and r["model_used"] is False and r["model_version"] == "rules-only"
    assert r["classification"] == "unverified" and r["risk_score"] == 0
    u = rules_engine.analyze_url("http://192.168.1.1:8080/paypal/login/verify")
    assert u["risk_score"] > 0 and "IP_BASED_URL" in {i["code"] for i in u["indicators"]}


def test_eml_input(engine):
    raw = (b"From: PayPal Support <help@gmail.com>\r\nTo: a@b.com\r\nSubject: Urgent\r\n"
           b"Content-Type: text/plain\r\n\r\nYour account will be suspended within 24 hours. Verify your password now.\r\n")
    codes = {i["code"] for i in engine.analyze_eml(raw)["indicators"]}
    assert {"SUSPICIOUS_SENDER", "CREDENTIAL_REQUEST"} <= codes


@pytest.mark.parametrize("bad", ["", "   ", None, 123])
def test_empty_or_wrong_type_inputs_raise(engine, bad):
    with pytest.raises(InvalidInputError):
        engine.analyze_text(bad)
    with pytest.raises(InvalidInputError):
        engine.analyze_url(bad)


def test_empty_email_raises(engine):
    with pytest.raises(InvalidInputError):
        engine.analyze_email(subject="", body="  ")
    with pytest.raises(InvalidInputError):
        engine.analyze_eml(b"")


def test_malformed_and_dangerous_urls_return_findings(engine):
    r = engine.analyze_url("http://[::1")
    assert "MALFORMED_URL" in {i["code"] for i in r["indicators"]} and r["classification"] == "unverified"
    j = engine.analyze_url("javascript:alert(1)")
    assert j["classification"] == "malicious" and j["risk_score"] >= 60


def test_unknown_scan_type_raises(engine):
    with pytest.raises(InvalidInputError):
        engine.analyze("nope", "x")