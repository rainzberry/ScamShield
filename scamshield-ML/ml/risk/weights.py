from __future__ import annotations

from typing import Dict, Optional, Tuple

from ..schemas import Indicator

# code: (label, default severity, evidence points, minimum-risk floor)
CATALOG: Dict[str, Tuple[str, str, int, int]] = {
    # URL
    "IP_BASED_URL": ("IP-Address Host", "HIGH", 14, 0),
    "SUSPICIOUS_TLD": ("Suspicious Top-Level Domain", "MEDIUM", 6, 0),
    "URL_SHORTENER": ("URL Shortening Service", "MEDIUM", 8, 0),
    "ENCODED_URL": ("Percent-Encoded URL", "LOW", 4, 0),
    "PUNYCODE_DOMAIN": ("Punycode / IDN Domain", "MEDIUM", 8, 0),
    "AT_SYMBOL_IN_URL": ("'@' Symbol in URL Authority", "HIGH", 12, 0),
    "LOOKALIKE_DOMAIN": ("Lookalike Domain", "HIGH", 16, 0),
    "BRAND_IN_SUBDOMAIN": ("Brand Name in Subdomain", "HIGH", 14, 0),
    "BRAND_IMPERSONATION_PATTERN": ("Brand Impersonation Pattern", "MEDIUM", 9, 0),
    "NO_HTTPS": ("Unencrypted HTTP", "LOW", 3, 0),
    "EXCESSIVE_SUBDOMAINS": ("Excessive Subdomains", "MEDIUM", 6, 0),
    "LONG_URL": ("Very Long URL", "LOW", 3, 0),
    "SUSPICIOUS_URL_KEYWORDS": ("Suspicious Keywords in URL", "MEDIUM", 6, 0),
    "HIGH_ENTROPY_HOST": ("Random-Looking Domain", "LOW", 4, 0),
    "NON_STANDARD_PORT": ("Non-Standard Port", "LOW", 3, 0),
    "MALFORMED_URL": ("Malformed URL", "MEDIUM", 10, 0),
    "DANGEROUS_URI_SCHEME": ("Dangerous URI Scheme", "CRITICAL", 30, 60),
    "ML_SUSPICIOUS_URL": ("URL Classifier Flag", "HIGH", 0, 0),
    # Text / email
    "URGENT_LANGUAGE": ("Urgent / Threatening Language", "MEDIUM", 7, 0),
    "CREDENTIAL_REQUEST": ("Credential / Sensitive-Data Request", "HIGH", 14, 0),
    "PAYMENT_REQUEST": ("Unusual Payment Request", "HIGH", 12, 0),
    "UNSOLICITED_OFFER": ("Unsolicited Prize / Offer", "MEDIUM", 7, 0),
    "ADVANCE_FEE_PATTERN": ("Advance-Fee Fraud Pattern", "HIGH", 14, 0),
    "PROMOTIONAL_LANGUAGE": ("Promotional / Spam Language", "LOW", 5, 0),
    "SUSPICIOUS_SENDER": ("Suspicious Sender", "HIGH", 14, 0),
    "REPLY_TO_MISMATCH": ("Reply-To Domain Mismatch", "MEDIUM", 8, 0),
    "IMPERSONATION_INDICATOR": ("Possible Impersonation", "MEDIUM", 8, 0),
    "EXECUTABLE_ATTACHMENT": ("Executable / Script Attachment", "CRITICAL", 28, 60),
    "DOUBLE_EXTENSION_ATTACHMENT": ("Double-Extension Attachment", "CRITICAL", 28, 60),
    "RISKY_ATTACHMENT": ("Risky Attachment Type", "MEDIUM", 9, 0),
    "SUSPICIOUS_URL_IN_TEXT": ("Suspicious Link in Message", "HIGH", 14, 0),
    "ML_SUSPICIOUS_TEXT": ("Text Classifier Flag", "HIGH", 0, 0),
    # QR / UPI / other payloads
    "SUSPICIOUS_QR_PAYLOAD": ("Suspicious QR Payload", "HIGH", 0, 0),
    "UPI_PAYMENT_REQUEST": ("QR Initiates a UPI Payment", "LOW", 2, 0),
    "UPI_PREFILLED_AMOUNT": ("Pre-filled Payment Amount", "LOW", 2, 0),
    "UPI_HIGH_AMOUNT": ("High Pre-filled Amount", "MEDIUM", 5, 0),
    "UPI_MERCHANT_UNVERIFIED": ("Merchant Not Independently Verified", "INFO", 0, 0),
    "UPI_INVALID_VPA": ("Missing / Invalid UPI ID", "MEDIUM", 10, 0),
    "UPI_UNKNOWN_HANDLE": ("UPI Handle Not in Known List", "LOW", 3, 0),
    "UPI_PAYEE_KEYWORDS": ("Support/Reward Words in Payee", "MEDIUM", 8, 0),
    "UPI_NOTE_REWARD_LANGUAGE": ("Refund/Reward Language in Note", "MEDIUM", 8, 0),
    "UPI_MISSING_PAYEE_NAME": ("No Payee Name Provided", "LOW", 2, 0),
    "UPI_DUPLICATE_PARAMS": ("Duplicate UPI Parameters", "MEDIUM", 8, 0),
    "UPI_INVALID_AMOUNT": ("Invalid Payment Amount", "LOW", 4, 0),
    "UPI_EMBEDDED_URL": ("URL Embedded in UPI Payload", "INFO", 0, 0),
    "WIFI_OPEN_NETWORK": ("Open (Unencrypted) Wi-Fi", "LOW", 4, 0),
    "WIFI_WEP": ("Weak WEP Wi-Fi Security", "MEDIUM", 6, 0),
}


def make_indicator(code: str, evidence: str, *, source: str = "rule",
                   severity: Optional[str] = None, points: Optional[int] = None) -> Indicator:
    label, sev, pts, floor = CATALOG[code]
    return Indicator(code, label, severity or sev, evidence, source,
                     pts if points is None else points, floor)