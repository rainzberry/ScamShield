from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Tuple
from urllib.parse import urlsplit

import numpy as np

from ..configs.lists import (STRONG_URL_SUBSTRINGS, SUSPICIOUS_TLDS, SUSPICIOUS_URL_TOKENS,
                             URL_SHORTENERS)
from ..configs.settings import MAX_URL_LENGTH
from ..features.common import is_ip_host, shannon_entropy, split_hostname
from ..schemas import InvalidInputError, MalformedURLError
from .brands import brand_signals

FEATURE_NAMES: List[str] = [
    "url_length", "hostname_length", "path_length", "query_length", "fragment_length",
    "num_dots", "num_subdomains", "num_hyphens_host", "num_hyphens_url", "num_digits_url",
    "num_digits_host", "digit_ratio_url", "num_special_chars", "special_char_ratio",
    "num_at_symbols", "is_ip_host", "is_https", "suspicious_tld", "tld_length", "is_shortener",
    "num_percent_encoded", "has_punycode", "has_non_ascii_host", "num_suspicious_tokens",
    "num_path_segments", "num_query_params", "has_port", "double_slash_in_path",
    "host_entropy", "path_entropy", "longest_host_label", "brand_in_registered_extra",
    "brand_in_subdomain", "brand_in_path", "brand_lookalike", "has_www",
]

_SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.\-]*://")
_CTRL = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")
_SPECIAL = "@?&=_~%#$!*+,;"


def normalize_url(raw: str) -> Tuple[str, bool]:
    """Return (url_with_scheme, scheme_was_assumed). Missing scheme -> https:// is assumed."""
    if not isinstance(raw, str) or not raw.strip():
        raise InvalidInputError("URL must be a non-empty string")
    url = _CTRL.sub("", raw.strip())
    if len(url) > MAX_URL_LENGTH:
        raise MalformedURLError(f"URL longer than {MAX_URL_LENGTH} characters")
    if url.startswith("//"):
        url = "https:" + url
    assumed = not _SCHEME.match(url)
    if assumed:
        url = "https://" + url
    return url, assumed


def analyze_url_structure(raw_url: str) -> Tuple[Dict[str, float], Dict[str, Any]]:
    url, assumed = normalize_url(raw_url)
    try:
        parts = urlsplit(url)
        host = parts.hostname or ""
        port = parts.port
    except ValueError as e:
        raise MalformedURLError(str(e))
    if not host:
        raise MalformedURLError("URL has no hostname")
    path, query, frag = parts.path, parts.query, parts.fragment
    sp = split_hostname(host)
    ip = is_ip_host(host)
    sub_labels = [l for l in sp["subdomain"].split(".") if l]
    has_www = int(bool(sub_labels) and sub_labels[0] == "www")
    if has_www:
        sub_labels = sub_labels[1:]
    host_labels = [l for l in host.split(".") if l]
    low = url.lower()
    no_scheme = low.split("://", 1)[1] if "://" in low else low
    tokens = {t for t in re.split(r"[^a-z0-9]+", no_scheme) if t}
    matched = set(tokens & SUSPICIOUS_URL_TOKENS) | {s for s in STRONG_URL_SUBSTRINGS if s in no_scheme}
    brand = brand_signals(sp, path + " " + query)
    n_digits = sum(c.isdigit() for c in url)
    n_special = sum(url.count(c) for c in _SPECIAL)
    n = max(len(url), 1)
    scheme = parts.scheme.lower()

    f: Dict[str, float] = {
        "url_length": len(url), "hostname_length": len(host), "path_length": len(path),
        "query_length": len(query), "fragment_length": len(frag),
        "num_dots": url.count("."), "num_subdomains": 0 if ip else len(sub_labels),
        "num_hyphens_host": host.count("-"), "num_hyphens_url": url.count("-"),
        "num_digits_url": n_digits, "num_digits_host": sum(c.isdigit() for c in host),
        "digit_ratio_url": n_digits / n, "num_special_chars": n_special,
        "special_char_ratio": n_special / n, "num_at_symbols": url.count("@"),
        "is_ip_host": int(ip), "is_https": int(scheme == "https"),
        "suspicious_tld": int(sp["suffix"].split(".")[-1] in SUSPICIOUS_TLDS),
        "tld_length": len(sp["suffix"].split(".")[-1]) if sp["suffix"] else 0,
        "is_shortener": int(sp["registered"] in URL_SHORTENERS or host in URL_SHORTENERS),
        "num_percent_encoded": len(re.findall(r"%[0-9a-fA-F]{2}", url)),
        "has_punycode": int(any(l.startswith("xn--") for l in host_labels)),
        "has_non_ascii_host": int(any(ord(c) > 127 for c in host)),
        "num_suspicious_tokens": len(matched),
        "num_path_segments": len([s for s in path.split("/") if s]),
        "num_query_params": len([p for p in query.split("&") if p]),
        "has_port": int(port not in (None, 80, 443)),
        "double_slash_in_path": int("//" in path),
        "host_entropy": shannon_entropy(host), "path_entropy": shannon_entropy(path),
        "longest_host_label": max((len(l) for l in host_labels), default=0),
        "brand_in_registered_extra": brand["brand_in_registered_extra"],
        "brand_in_subdomain": brand["brand_in_subdomain"],
        "brand_in_path": brand["brand_in_path"], "brand_lookalike": brand["brand_lookalike"],
        "has_www": has_www,
    }
    f = {k: float(f[k]) for k in FEATURE_NAMES}
    details: Dict[str, Any] = {
        "normalized_url": url, "scheme": scheme, "scheme_assumed": assumed, "hostname": host,
        "registered_domain": sp["registered"], "subdomain": sp["subdomain"], "label": sp["label"],
        "suffix": sp["suffix"], "path": path, "query": query, "port": port,
        "userinfo_present": "@" in parts.netloc, "matched_tokens": sorted(matched),
        "brand": brand, "label_entropy": shannon_entropy(sp["label"]),
    }
    return f, details


def extract_url_features(raw_url: str) -> Dict[str, float]:
    return analyze_url_structure(raw_url)[0]


def features_dataframe(urls: Iterable[str]):
    """Returns (X ndarray [n_valid, n_features], valid_mask ndarray[bool]) - malformed URLs are masked out."""
    rows, valid = [], []
    for u in urls:
        try:
            f, _ = analyze_url_structure(u)
            rows.append([f[n] for n in FEATURE_NAMES])
            valid.append(True)
        except ValueError:
            valid.append(False)
    X = np.asarray(rows, dtype=float).reshape(-1, len(FEATURE_NAMES))
    return X, np.asarray(valid, dtype=bool)