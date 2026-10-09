"""Thin, clean bridge to the separate ML project. NO ML logic lives in Flask.

The ML package is imported lazily and cached (models are loaded once, never per request,
never trained here). If a module/model artifact is missing the adapter raises
ModelUnavailableError (HTTP 503) instead of inventing a prediction.
"""
from __future__ import annotations

import importlib
import inspect
import logging
import sys
import threading
from pathlib import Path

from flask import current_app

from ..errors.exceptions import AnalysisFailedError, AppError, ModelUnavailableError

log = logging.getLogger(__name__)
_UNAVAILABLE_NAME_HINTS = ("modelnotfound", "modelnotloaded", "modelunavailable",
                           "artifactmissing", "artifactnotfound")


def get_ml_engine():
    return current_app.extensions["ml_engine"]


def _call_with_supported_kwargs(fn, args: tuple, **optional):
    """Pass only the optional keyword arguments the ML function actually accepts."""
    try:
        params = inspect.signature(fn).parameters
    except (TypeError, ValueError):
        return fn(*args)
    accepts_var_kw = any(p.kind is inspect.Parameter.VAR_KEYWORD for p in params.values())
    kwargs = {k: v for k, v in optional.items()
              if v is not None and (accepts_var_kw or k in params)}
    return fn(*args, **kwargs)


class MLEngine:
    def __init__(self, specs: dict[str, str], info_spec: str | None = None):
        self._specs = specs
        self._info_spec = info_spec
        self._cache: dict[str, object] = {}
        self._lock = threading.Lock()

    @classmethod
    def from_config(cls, config) -> "MLEngine":
        ml_path = config.get("ML_PROJECT_PATH")
        candidate = Path(ml_path) if ml_path else Path(config["INSTANCE_DIR"]).parent.parent
        if candidate.is_dir() and str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))
        return cls(
            {"text": config["ML_TEXT_ANALYZER"], "url": config["ML_URL_ANALYZER"],
             "payload": config["ML_PAYLOAD_ANALYZER"]},
            config.get("ML_INFO_FUNC"),
        )

    # -- loading ---------------------------------------------------------
    def _resolve(self, key: str):
        with self._lock:
            if key in self._cache:
                return self._cache[key]
        spec = self._specs.get(key) or ""
        module_name, _, func_name = spec.partition(":")
        if not module_name or not func_name:
            raise ModelUnavailableError(f"ML analyzer '{key}' is not configured correctly.")
        try:
            module = importlib.import_module(module_name)
        except ImportError as exc:
            log.warning("ML module %s not importable: %s", module_name, exc)
            raise ModelUnavailableError(
                f"The ML module '{module_name}' could not be loaded. "
                "Check ML_PROJECT_PATH and the ML_*_ANALYZER settings.") from exc
        except FileNotFoundError as exc:
            raise ModelUnavailableError("A required model artifact file is missing.") from exc
        fn = getattr(module, func_name, None)
        if not callable(fn):
            raise ModelUnavailableError(
                f"Function '{func_name}' was not found in ML module '{module_name}'.")
        with self._lock:
            self._cache[key] = fn
        return fn

    def preload(self) -> None:
        """Best-effort load at startup so the first request is fast. Never raises."""
        for key in self._specs:
            try:
                self._resolve(key)
            except ModelUnavailableError as exc:
                log.warning("ML analyzer '%s' unavailable at startup: %s", key, exc.message)
            except Exception:  # pragma: no cover - defensive
                log.exception("Unexpected error preloading ML analyzer '%s'", key)

    def _invoke(self, key: str, args: tuple, **optional):
        fn = self._resolve(key)
        try:
            return _call_with_supported_kwargs(fn, args, **optional)
        except AppError:
            raise
        except (FileNotFoundError, ImportError) as exc:
            log.error("ML artifact/import error in '%s': %s", key, type(exc).__name__)
            raise ModelUnavailableError("The analysis model files are missing or unreadable.") from exc
        except Exception as exc:
            if any(h in type(exc).__name__.lower() for h in _UNAVAILABLE_NAME_HINTS):
                raise ModelUnavailableError(str(exc)[:200] or None) from exc
            log.exception("ML analyzer '%s' raised an exception", key)
            raise AnalysisFailedError() from exc

    # -- public API ------------------------------------------------------
    def analyze_text(self, text: str, context: dict | None = None):
        return self._invoke("text", (text,), context=context)

    def analyze_url(self, url: str, context: dict | None = None):
        return self._invoke("url", (url,), context=context)

    def analyze_payload(self, payload: str, payload_type: str | None = None,
                        parsed: dict | None = None, context: dict | None = None):
        try:
            self._resolve("payload")
        except ModelUnavailableError:
            # No dedicated QR analyzer: route plain URL / text payloads to the matching analyzer.
            if payload_type == "url":
                return self.analyze_url(payload, context=context)
            if payload_type == "text":
                return self.analyze_text(payload, context=context)
            raise
        return self._invoke("payload", (payload,), payload_type=payload_type,
                            parsed=parsed, context=context)

    def model_info(self) -> dict:
        analyzers = {}
        for key in self._specs:
            try:
                self._resolve(key)
                analyzers[key] = {"available": True}
            except ModelUnavailableError as exc:
                analyzers[key] = {"available": False, "detail": exc.message}
        info = {"available": all(analyzers.get(k, {}).get("available") for k in ("text", "url")),
                "analyzers": analyzers}
        if self._info_spec:
            module_name, _, func_name = self._info_spec.partition(":")
            try:
                fn = getattr(importlib.import_module(module_name), func_name)
                info["model"] = fn()
            except Exception:
                log.warning("ML_INFO_FUNC failed", exc_info=True)
        return info
