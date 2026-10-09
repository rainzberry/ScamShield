"""Public API for the Flask backend. Imports are lazy to avoid import cycles.

    from ml.inference import analyze_url, analyze_email, analyze_text, analyze_qr_payload, InvalidInputError
"""
from ..schemas import InvalidInputError  # noqa: F401


def get_engine(models_dir=None):
    from .engine import get_engine as _get
    return _get(str(models_dir) if models_dir else None)


def analyze_url(url):
    return get_engine().analyze_url(url)


def analyze_text(text):
    return get_engine().analyze_text(text)


def analyze_email(subject="", body="", sender=None, reply_to=None, attachments=None):
    return get_engine().analyze_email(subject, body, sender, reply_to, attachments)


def analyze_eml(raw):
    return get_engine().analyze_eml(raw)


def analyze_qr_payload(payload):
    return get_engine().analyze_qr_payload(payload)


def model_status():
    return get_engine().status()