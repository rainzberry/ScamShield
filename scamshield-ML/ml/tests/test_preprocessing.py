import pandas as pd

from ml.preprocessing.splitting import (dataset_fingerprint, grouped_stratified_split,
                                        stratified_split)
from ml.preprocessing.text_cleaning import clean_text, compose_email_text, extract_urls


def test_clean_text_replaces_urls_and_emails():
    t = clean_text("Visit http://Evil.com/x or mail bob@example.com NOW")
    assert "urltoken" in t and "emailtoken" in t
    assert "evil.com" not in t and "bob@" not in t


def test_clean_text_strips_html_and_scripts():
    t = clean_text("<html><body><p>Hello <b>World</b></p><script>bad()</script></body></html>")
    assert "hello world" in t
    assert "bad" not in t and "<" not in t


def test_clean_text_non_string_and_empty():
    assert clean_text(None) == "" and clean_text(123) == "" and clean_text("") == ""


def test_extract_urls_dedup_and_href():
    urls = extract_urls('Go to http://a.com/x. Also <a href="http://b.com/y">link</a> http://a.com/x')
    assert set(urls) == {"http://a.com/x", "http://b.com/y"} and len(urls) == 2


def test_extract_urls_empty_and_wrong_type():
    assert extract_urls("") == [] and extract_urls(None) == []


def test_compose_email_text():
    assert compose_email_text("Sub", "Body") == "Sub\n\nBody"
    assert compose_email_text(None, None).strip() == ""


def test_fingerprint_is_order_independent_and_sensitive():
    assert dataset_fingerprint(["a", "b"], [0, 1]) == dataset_fingerprint(["b", "a"], [1, 0])
    assert dataset_fingerprint(["a", "b"], [0, 1]) != dataset_fingerprint(["a", "b"], [1, 0])


def test_stratified_split_disjoint_and_stratified():
    df = pd.DataFrame({"id": range(400), "label": [0, 1] * 200, "source": ["x", "y"] * 200})
    tr, va, te = stratified_split(df, "label", seed=1, strat_extra="source")
    ids = [set(x["id"]) for x in (tr, va, te)]
    assert not (ids[0] & ids[1] or ids[0] & ids[2] or ids[1] & ids[2])
    assert len(tr) + len(va) + len(te) == 400
    for part in (tr, va, te):
        assert abs(part["label"].mean() - 0.5) < 0.05


def test_grouped_split_has_no_group_overlap():
    n = 2000
    df = pd.DataFrame({"url": [f"u{i}" for i in range(n)], "label": [i % 2 for i in range(n)],
                       "group": [f"g{i // 10}" for i in range(n)]})
    tr, va, te = grouped_stratified_split(df, "label", "group", seed=3)
    g = [set(x["group"]) for x in (tr, va, te)]
    assert not (g[0] & g[1] or g[0] & g[2] or g[1] & g[2])
    assert len(tr) + len(va) + len(te) == n
    assert 0.6 < len(tr) / n < 0.8