from __future__ import annotations

import json
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import joblib

MODEL_FILE = "model.joblib"
METADATA_FILE = "metadata.json"


@dataclass
class LoadedModel:
    estimator: Any
    metadata: Dict[str, Any]
    path: Path
    cache: Dict[str, Any] = field(default_factory=dict)

    @property
    def version(self) -> str:
        return str(self.metadata.get("model_version", "unknown"))


def save_bundle(model_dir, estimator, metadata: Dict[str, Any]) -> Path:
    d = Path(model_dir)
    d.mkdir(parents=True, exist_ok=True)
    joblib.dump(estimator, d / MODEL_FILE, compress=3)
    with open(d / METADATA_FILE, "w", encoding="utf-8") as fh:
        json.dump(metadata, fh, indent=2, default=str)
    return d


def load_bundle(model_dir) -> Optional[LoadedModel]:
    """Load once; returns None if no artifact exists. Only load artifacts you trained yourself (joblib = pickle)."""
    d = Path(model_dir)
    mp, meta = d / MODEL_FILE, d / METADATA_FILE
    if not mp.is_file() or not meta.is_file():
        return None
    with open(meta, encoding="utf-8") as fh:
        metadata = json.load(fh)
    import sklearn
    trained = metadata.get("sklearn_version")
    if trained and trained != sklearn.__version__:
        warnings.warn(f"Model trained with scikit-learn {trained}, running {sklearn.__version__}. Retrain if you see errors.")
    return LoadedModel(joblib.load(mp), metadata, d)