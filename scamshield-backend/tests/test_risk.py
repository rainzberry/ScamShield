"""TC12 - deterministic risk / severity."""
import pytest

from app.errors.exceptions import MLContractError
from app.services.result_normalizer import normalize_ml_result
from app.services.severity import severity_for

BANDS = [(0, "LOW"), (24, "LOW"), (25, "MEDIUM"), (49, "MEDIUM"),
         (50, "HIGH"), (74, "HIGH"), (75, "CRITICAL"), (100, "CRITICAL")]


@pytest.mark.parametrize("score,expected", BANDS)
def test_tc12_severity_bands(score, expected):
    assert severity_for(score) == expected


@pytest.mark.parametrize("bad", [-1, 101, 50.5, "50", None, True])
def test_severity_rejects_invalid_scores(bad):
    with pytest.raises(ValueError):
        severity_for(bad)


def test_tc12_same_input_gives_identical_result(client, auth):
    body = {"text": "Your account is suspended. Verify your account now."}
    results = [client.post("/api/analyze/text", headers=auth, json=body).get_json()["scan"]
               for _ in range(3)]
    keys = ("classification", "risk_score", "confidence", "severity", "indicators", "model_version")
    assert all([r[k] for k in keys] == [results[0][k] for k in keys] for r in results)


def test_risk_and_confidence_are_independent_values():
    low_conf = normalize_ml_result({"classification": "phishing", "risk_score": 90, "confidence": 0.51})
    high_conf = normalize_ml_result({"classification": "safe", "risk_score": 3, "confidence": 0.99})
    assert (low_conf.risk_score, low_conf.confidence) == (90, 0.51)
    assert (high_conf.risk_score, high_conf.confidence) == (3, 0.99)


def test_rounding_is_deterministic_half_up():
    r = lambda v: normalize_ml_result({"classification": "safe", "risk_score": v, "confidence": 0.5}).risk_score
    assert [r(24.5), r(24.4), r(74.5), r(0), r(100)] == [25, 24, 75, 0, 100]


def test_normalizer_rejects_garbage():
    for bad in (None, {}, {"classification": "safe"}, {"classification": "x", "risk_score": 1, "confidence": 1}):
        with pytest.raises(MLContractError):
            normalize_ml_result(bad)
