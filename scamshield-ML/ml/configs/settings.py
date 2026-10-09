from __future__ import annotations

import os
from pathlib import Path

ML_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ML_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"
REPORTS_DIR = ML_ROOT / "evaluation" / "reports"
MODELS_DIR = Path(os.environ.get("SCAMSHIELD_MODELS_DIR", str(ML_ROOT / "models")))

TEXT_MODEL_DIRNAME = "text_model"
URL_MODEL_DIRNAME = "url_model"

RANDOM_SEED = 42
TEXT_THRESHOLD = 0.5
URL_THRESHOLD = 0.5

MAX_TEXT_CHARS = 20000
MAX_EMBEDDED_URLS = 10
MAX_URL_LENGTH = 4096
MAX_QR_PAYLOAD_CHARS = 4296

SPLIT_FRACTIONS = {"train": 0.70, "val": 0.15, "test": 0.15}

RULES_VERSION = "rules-v1"
RISK_FORMULA_VERSION = "risk-v1"