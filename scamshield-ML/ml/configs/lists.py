"""Heuristic reference lists. They are NOT authoritative threat intelligence."""
from __future__ import annotations

MULTI_PART_SUFFIXES = frozenset({
    "co.uk", "org.uk", "ac.uk", "gov.uk", "com.au", "net.au", "org.au", "co.in", "net.in",
    "org.in", "gov.in", "ac.in", "co.jp", "com.br", "com.cn", "co.za", "com.mx", "co.nz",
    "com.sg", "com.tr", "com.ar", "co.kr", "com.hk", "com.tw", "com.my", "com.pk",
    "com.bd", "com.ng", "co.id", "com.vn", "com.ph", "com.ua",
})

SUSPICIOUS_TLDS = frozenset({
    "xyz", "top", "tk", "ml", "ga", "cf", "gq", "click", "link", "zip", "mov", "icu", "cyou",
    "buzz", "rest", "monster", "cam", "loan", "men", "work", "support", "country", "kim",
    "download", "racing", "stream", "review", "gdn", "bid", "win", "party", "science",
    "date", "faith", "accountant", "cricket",
})

URL_SHORTENERS = frozenset({
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "buff.ly", "rebrand.ly",
    "cutt.ly", "shorturl.at", "tiny.cc", "rb.gy", "lnkd.in", "s.id", "v.gd", "t.ly",
    "bl.ink", "soo.gd", "clck.ru", "qr.ae", "amzn.to", "fb.me", "tr.ee", "short.io",
})

SUSPICIOUS_URL_TOKENS = frozenset({
    "login", "signin", "verify", "verification", "secure", "account", "update", "confirm",
    "banking", "wallet", "password", "passwd", "credential", "suspend", "suspended",
    "unlock", "recover", "billing", "invoice", "payment", "support", "helpdesk", "webscr",
    "authenticate", "security", "alert", "validate", "appleid", "free", "bonus", "prize",
    "gift", "claim", "reward", "refund", "kyc",
})
STRONG_URL_SUBSTRINGS = (
    "login", "signin", "verify", "secure", "password", "banking", "account", "update",
    "wallet", "billing",
)

BRANDS = (
    "paypal", "amazon", "apple", "microsoft", "google", "facebook", "instagram", "netflix",
    "whatsapp", "linkedin", "dropbox", "docusign", "adobe", "ebay", "walmart", "dhl",
    "fedex", "ups", "usps", "chase", "wellsfargo", "bankofamerica", "citibank",
    "americanexpress", "coinbase", "binance", "metamask", "outlook", "office365", "icloud",
    "sbi", "hdfc", "hdfcbank", "icici", "icicibank", "axisbank", "kotak", "paytm", "phonepe",
    "gpay", "googlepay", "npci", "irctc", "flipkart", "amazonpay", "bhim", "uidai",
    "aadhaar", "incometax",
)

# Registered domains for which brand-impersonation features are forced to 0 (non-exhaustive).
BRAND_SAFE_REGISTERED_DOMAINS = frozenset({
    "paypal.com", "paypal.me", "amazon.com", "amazon.in", "amazon.co.uk", "amazon.de",
    "amazonaws.com", "apple.com", "icloud.com", "microsoft.com", "microsoftonline.com",
    "office.com", "office365.com", "live.com", "outlook.com", "google.com", "googleapis.com",
    "googleusercontent.com", "gstatic.com", "gmail.com", "youtube.com", "facebook.com",
    "instagram.com", "whatsapp.com", "netflix.com", "linkedin.com", "dropbox.com",
    "docusign.com", "docusign.net", "adobe.com", "ebay.com", "walmart.com", "dhl.com",
    "fedex.com", "ups.com", "usps.com", "chase.com", "wellsfargo.com", "bankofamerica.com",
    "citibank.com", "americanexpress.com", "coinbase.com", "binance.com", "metamask.io",
    "sbi.co.in", "onlinesbi.sbi", "hdfcbank.com", "icicibank.com", "axisbank.com",
    "kotak.com", "paytm.com", "phonepe.com", "npci.org.in", "irctc.co.in", "flipkart.com",
    "bhimupi.org.in", "uidai.gov.in", "incometax.gov.in",
})

FREEMAIL_DOMAINS = frozenset({
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "aol.com", "proton.me",
    "protonmail.com", "mail.com", "gmx.com", "yandex.com", "rediffmail.com", "icloud.com",
    "live.com", "zoho.com",
})
SENDER_ROLE_WORDS = (
    "support", "security", "billing", "helpdesk", "help desk", "bank", "customer care",
    "account team", "service desk", "verification", "refund",
)

DANGEROUS_ATTACHMENT_EXT = frozenset({
    "exe", "scr", "bat", "cmd", "com", "pif", "js", "jse", "vbs", "vbe", "wsf", "wsh",
    "ps1", "msi", "jar", "lnk", "hta", "iso", "img", "dll", "apk", "reg",
})
RISKY_ATTACHMENT_EXT = frozenset({
    "docm", "xlsm", "pptm", "dotm", "xlam", "zip", "rar", "7z", "ace", "html", "htm", "svg",
})

KNOWN_UPI_HANDLES = frozenset({
    "ybl", "ibl", "axl", "okaxis", "oksbi", "okhdfcbank", "okicici", "paytm", "apl", "upi",
    "sbi", "hdfcbank", "icici", "axisbank", "kotak", "fbl", "pnb", "boi", "barodampay",
    "cnrb", "idfcbank", "indus", "yesbank", "airtel", "postbank", "jupiteraxis",
    "freecharge", "fam", "ikwik", "rbl", "sib", "pingpay", "waicici", "wahdfcbank",
    "waaxis", "wasbi", "ptyes", "pthdfc", "ptaxis", "ptsbi",
})
UPI_PAYEE_KEYWORDS = (
    "refund", "support", "helpline", "customercare", "customer care", "kyc", "reward",
    "cashback", "prize", "lottery", "verification",
)

DANGEROUS_URI_SCHEMES = frozenset({"javascript", "data", "vbscript", "file", "blob"})