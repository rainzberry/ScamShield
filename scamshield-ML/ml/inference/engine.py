from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..configs.settings import (MODELS_DIR, TEXT_MODEL_DIRNAME, TEXT_THRESHOLD,
                                URL_MODEL_DIRNAME, URL_THRESHOLD)
from ..preprocessing.email_parsing import parse_eml_bytes
from ..qr_analysis.analyzer import analyze_qr_payload
from ..schemas import InvalidInputError
from ..text_analysis.analyzer import analyze_message
from ..url_analysis.analyzer import analyze_url
from .model_store import LoadedModel, load_bundle


class ScamShieldEngine:
    """Loads models ONCE; every analyze_* call is inference only (it never trains)."""

    def __init__(self, models_dir=None, load_models: bool = True):
        base = Path(models_dir) if models_dir else MODELS_DIR
        self.models_dir = base
        self.text_model: Optional[LoadedModel] = load_bundle(base / TEXT_MODEL_DIRNAME) if load_models else None
        self.url_model: Optional[LoadedModel] = load_bundle(base / URL_MODEL_DIRNAME) if load_models else None
        self._text_thr = (self.text_model.metadata.get("threshold", TEXT_THRESHOLD)
                          if self.text_model else TEXT_THRESHOLD)
        self._url_thr = (self.url_model.metadata.get("threshold", URL_THRESHOLD)
                         if self.url_model else URL_THRESHOLD)

    def status(self) -> Dict[str, Any]:
        def info(m: Optional[LoadedModel]):
            if m is None:
                return None
            md = m.metadata
            return {"model_version": m.version, "model_type": md.get("model_type"),
                    "trained_at_utc": md.get("trained_at_utc"), "data_fingerprint": md.get("data_fingerprint"),
                    "threshold": md.get("threshold"), "validation_metrics": {
                        k: md.get("validation_metrics", {}).get(k) for k in ("accuracy", "precision", "recall", "f1", "roc_auc", "pr_auc")}}
        return {"models_dir": str(self.models_dir), "text_model": info(self.text_model),
                "url_model": info(self.url_model),
                "mode": "full" if (self.text_model and self.url_model) else "degraded (rules-only for missing models)"}

    def analyze_text(self, text: str) -> Dict[str, Any]:
        return analyze_message(subject="", body=text, text_model=self.text_model, url_model=self.url_model,
                               scan_type="text", threshold=self._text_thr)

    def analyze_email(self, subject: str = "", body: str = "", sender: Optional[str] = None,
                      reply_to: Optional[str] = None, attachments: Optional[List[str]] = None) -> Dict[str, Any]:
        return analyze_message(subject=subject, body=body, sender=sender, reply_to=reply_to,
                               attachments=attachments, text_model=self.text_model, url_model=self.url_model,
                               scan_type="email", threshold=self._text_thr)

    def analyze_eml(self, raw: bytes) -> Dict[str, Any]:
        if not isinstance(raw, (bytes, bytearray)) or not raw.strip():
            raise InvalidInputError("EML content must be non-empty bytes")
        return self.analyze_email(**parse_eml_bytes(bytes(raw)))

    def analyze_url(self, url: str) -> Dict[str, Any]:
        return analyze_url(url, url_model=self.url_model, threshold=self._url_thr)

    def analyze_qr_payload(self, payload: str) -> Dict[str, Any]:
        return analyze_qr_payload(payload, text_model=self.text_model, url_model=self.url_model,
                                  url_threshold=self._url_thr, text_threshold=self._text_thr)

    def analyze(self, scan_type: str, data: Any) -> Dict[str, Any]:
        """Generic dispatcher: url/text/qr -> str, email -> dict(subject, body, sender, ...), eml -> bytes."""
        st = (scan_type or "").lower()
        if st == "url":
            return self.analyze_url(data)
        if st == "text":
            return self.analyze_text(data)
        if st == "qr":
            return self.analyze_qr_payload(data)
        if st == "email":
            if not isinstance(data, dict):
                raise InvalidInputError("email input must be a dict")
            return self.analyze_email(**data)
        if st == "eml":
            return self.analyze_eml(data)
        raise InvalidInputError(f"unknown scan_type '{scan_type}'")


@lru_cache(maxsize=4)
def get_engine(models_dir: Optional[str] = None) -> ScamShieldEngine:
    return ScamShieldEngine(models_dir)