from __future__ import annotations

from typing import Any, Dict, List

from ..risk.weights import make_indicator
from ..schemas import Indicator


def build_url_indicators(f: Dict[str, float], d: Dict[str, Any]) -> List[Indicator]:
    out: List[Indicator] = []
    b = d["brand"]
    if f["is_ip_host"]:
        out.append(make_indicator("IP_BASED_URL", f"Hostname '{d['hostname']}' is an IP address, not a domain name."))
    if f["suspicious_tld"]:
        out.append(make_indicator("SUSPICIOUS_TLD", f"TLD '.{d['suffix']}' is on a heuristic list of TLDs often abused for phishing (list is not authoritative)."))
    if f["is_shortener"]:
        out.append(make_indicator("URL_SHORTENER", f"'{d['registered_domain']}' is a URL shortener; the destination is hidden and was NOT resolved (no network requests are made)."))
    if f["num_percent_encoded"] >= 3:
        out.append(make_indicator("ENCODED_URL", f"URL contains {int(f['num_percent_encoded'])} percent-encoded characters."))
    if f["has_punycode"]:
        out.append(make_indicator("PUNYCODE_DOMAIN", f"Hostname '{d['hostname']}' uses punycode (xn--), which can disguise lookalike characters."))
    if d["userinfo_present"]:
        out.append(make_indicator("AT_SYMBOL_IN_URL", "URL contains '@' before the host, so the text before it is not the real destination."))
    if b["brand_lookalike"]:
        out.append(make_indicator("LOOKALIKE_DOMAIN", f"Domain token '{b['lookalike_token']}' resembles brand '{b['lookalike_of']}' (edit distance {b['lookalike_distance']} after homoglyph normalisation) but the registered domain is '{d['registered_domain']}'."))
    if b["brand_in_subdomain"]:
        out.append(make_indicator("BRAND_IN_SUBDOMAIN", f"Brand name '{b['matched_brand']}' appears in the subdomain '{d['subdomain']}', but the registered domain is '{d['registered_domain']}'."))
    if b["brand_in_registered_extra"] or (b["brand_in_path"] and f["num_suspicious_tokens"] >= 1):
        where = "registered domain label" if b["brand_in_registered_extra"] else "URL path/query"
        out.append(make_indicator("BRAND_IMPERSONATION_PATTERN", f"Brand name '{b['matched_brand']}' appears in the {where} of '{d['registered_domain']}' (heuristic pattern, not proof)."))
    if d["scheme"] == "http":
        out.append(make_indicator("NO_HTTPS", "URL uses unencrypted HTTP."))
    if f["num_subdomains"] >= 4:
        out.append(make_indicator("EXCESSIVE_SUBDOMAINS", f"Hostname has {int(f['num_subdomains'])} subdomain levels."))
    if f["url_length"] >= 120:
        out.append(make_indicator("LONG_URL", f"URL is {int(f['url_length'])} characters long."))
    if f["num_suspicious_tokens"] >= 2:
        out.append(make_indicator("SUSPICIOUS_URL_KEYWORDS", "URL contains credential/account-themed keywords: " + ", ".join(d["matched_tokens"]) + "."))
    if len(d["label"]) >= 12 and d["label_entropy"] >= 3.4 and any(c.isdigit() for c in d["label"]):
        out.append(make_indicator("HIGH_ENTROPY_HOST", f"Domain label '{d['label']}' looks randomly generated (entropy {d['label_entropy']:.2f} bits/char)."))
    if f["has_port"]:
        out.append(make_indicator("NON_STANDARD_PORT", f"URL uses non-standard port {d['port']}."))
    return out