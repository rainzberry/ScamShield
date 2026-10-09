import pytest

from ml.features.common import levenshtein, shannon_entropy, split_hostname
from ml.schemas import InvalidInputError, MalformedURLError
from ml.url_analysis.features import (FEATURE_NAMES, analyze_url_structure, extract_url_features,
                                      features_dataframe)
from ml.url_analysis.indicators import build_url_indicators


def codes(url):
    f, d = analyze_url_structure(url)
    return {i.code for i in build_url_indicators(f, d)}


def test_feature_schema_is_stable():
    f = extract_url_features("https://www.example.com/a?b=1")
    assert list(f.keys()) == FEATURE_NAMES and len(set(FEATURE_NAMES)) == len(FEATURE_NAMES)
    assert f["is_https"] == 1 and f["has_www"] == 1 and f["path_length"] == 2 and f["num_query_params"] == 1


def test_ip_host_and_http():
    f = extract_url_features("http://192.168.0.1/login")
    assert f["is_ip_host"] == 1 and f["is_https"] == 0 and f["num_subdomains"] == 0


def test_at_symbol_and_userinfo():
    f, d = analyze_url_structure("https://paypal.com@evil.example.com/")
    assert f["num_at_symbols"] == 1 and d["userinfo_present"] and d["hostname"] == "evil.example.com"


def test_punycode_shortener_tld():
    assert extract_url_features("https://xn--pple-43d.com")["has_punycode"] == 1
    assert extract_url_features("https://bit.ly/abc")["is_shortener"] == 1
    assert extract_url_features("https://secure-login.example.xyz")["suspicious_tld"] == 1


def test_lookalike_and_brand_in_subdomain():
    assert extract_url_features("https://paypa1.com/signin")["brand_lookalike"] == 1
    f = extract_url_features("http://paypal.com.evil-site.xyz/")
    assert f["brand_in_subdomain"] == 1 and f["suspicious_tld"] == 1


def test_official_domain_has_no_brand_flags():
    f = extract_url_features("https://www.paypal.com/signin")
    assert f["brand_lookalike"] == f["brand_in_subdomain"] == f["brand_in_registered_extra"] == 0


def test_scheme_is_assumed_when_missing():
    f, d = analyze_url_structure("paypa1-secure.xyz/login")
    assert d["scheme_assumed"] is True and f["is_https"] == 1


def test_indicators_are_derived_from_features():
    c = codes("http://192.168.0.1/login?x=%41%42%43")
    assert {"IP_BASED_URL", "NO_HTTPS", "ENCODED_URL"} <= c
    c2 = codes("https://paypa1-secure.xyz/login")
    assert {"LOOKALIKE_DOMAIN", "SUSPICIOUS_TLD"} <= c2
    assert codes("https://www.wikipedia.org/wiki/Machine_learning") == set()


def test_multi_part_suffix():
    sp = split_hostname("shop.example.co.uk")
    assert sp["registered"] == "example.co.uk" and sp["subdomain"] == "shop"


def test_helpers():
    assert shannon_entropy("aaaa") == 0.0 and shannon_entropy("") == 0.0
    assert levenshtein("kitten", "sitting") == 3


@pytest.mark.parametrize("bad", ["http://[::1", "http:///path", "https://" + "a" * 5000])
def test_malformed_urls_raise(bad):
    with pytest.raises(MalformedURLError):
        analyze_url_structure(bad)


@pytest.mark.parametrize("bad", ["", "   ", None, 5])
def test_empty_or_wrong_type_raises(bad):
    with pytest.raises(InvalidInputError):
        analyze_url_structure(bad)


def test_features_dataframe_masks_malformed():
    X, mask = features_dataframe(["https://a.com", "http://[::1", "https://b.org/x"])
    assert mask.tolist() == [True, False, True] and X.shape == (2, len(FEATURE_NAMES))