from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion, Pipeline

from ..configs.settings import RANDOM_SEED, TEXT_THRESHOLD
from ..evaluation.metrics import compute_binary_metrics
from ..inference.model_store import save_bundle
from ..preprocessing.splitting import dataset_fingerprint

DEFAULT_TEXT_PARAMS: Dict[str, Any] = {
    "word_ngram": (1, 2), "word_min_df": 3, "word_max_features": 100000,
    "char_ngram": (3, 5), "char_min_df": 5, "char_max_features": 150000,
    "c_grid": [0.3, 1.0, 3.0, 10.0],
}


def build_feature_union(p: Dict[str, Any]) -> FeatureUnion:
    return FeatureUnion([
        ("word", TfidfVectorizer(analyzer="word", ngram_range=tuple(p["word_ngram"]), min_df=p["word_min_df"],
                                 max_features=p["word_max_features"], sublinear_tf=True, strip_accents="unicode")),
        ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=tuple(p["char_ngram"]), min_df=p["char_min_df"],
                                 max_features=p["char_max_features"], sublinear_tf=True)),
    ])


def _lr(C: float, seed: int) -> LogisticRegression:
    return LogisticRegression(C=C, class_weight="balanced", solver="liblinear", max_iter=1000, random_state=seed)


def fit_text_pipeline(texts, labels, C: float, params: Optional[Dict[str, Any]] = None, seed: int = RANDOM_SEED) -> Pipeline:
    p = {**DEFAULT_TEXT_PARAMS, **(params or {})}
    pipe = Pipeline([("features", build_feature_union(p)), ("clf", _lr(C, seed))])
    pipe.fit(list(texts), np.asarray(labels).astype(int))
    return pipe


def train_text_model(train_df: pd.DataFrame, val_df: pd.DataFrame, out_dir, params: Optional[Dict[str, Any]] = None,
                     seed: int = RANDOM_SEED) -> Dict[str, Any]:
    """Fit on TRAIN, choose C on VALIDATION. The TEST split is never touched here."""
    p = {**DEFAULT_TEXT_PARAMS, **(params or {})}
    ytr, yva = train_df["label"].astype(int).values, val_df["label"].astype(int).values
    fu = build_feature_union(p)
    Xtr = fu.fit_transform(train_df["text_clean"].tolist())
    Xva = fu.transform(val_df["text_clean"].tolist())
    trials, best = [], None
    for C in p["c_grid"]:
        clf = _lr(C, seed).fit(Xtr, ytr)
        m = compute_binary_metrics(yva, clf.predict_proba(Xva)[:, 1], TEXT_THRESHOLD)
        trials.append({"C": C, "val_f1": m["f1"], "val_pr_auc": m["pr_auc"]})
        score = (m["f1"], m["pr_auc"] or 0.0)
        if best is None or score > best[0]:
            best = (score, C, clf, m)
    _, C, clf, val_metrics = best
    pipe = Pipeline([("features", fu), ("clf", clf)])
    fp = dataset_fingerprint(train_df["text_clean"], ytr)
    meta = {
        "model_version": f"text-tfidf-lr-1.0.0+{fp[:8]}",
        "model_type": "TF-IDF (word 1-2 + char_wb 3-5) + Logistic Regression",
        "task": "stage1_safe_vs_suspicious", "classes": {"0": "safe", "1": "suspicious"},
        "threshold": TEXT_THRESHOLD, "chosen_C": C, "c_search": trials, "params": p, "seed": seed,
        "data_fingerprint": fp, "n_train": int(len(train_df)), "n_val": int(len(val_df)),
        "train_class_counts": {str(k): int(v) for k, v in pd.Series(ytr).value_counts().items()},
        "validation_metrics": val_metrics,
        "trained_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "sklearn_version": sklearn.__version__,
        "caveats": ["Binary SAFE/SUSPICIOUS only; SPAM/PHISHING/SCAM/MALICIOUS labels come from rules.",
                    "Public corpora are dated and source-specific; see leave-one-source-out results.",
                    "Probabilities come from regularised logistic regression and are not guaranteed calibrated (see Brier/ECE)."],
    }
    save_bundle(out_dir, pipe, meta)
    return meta