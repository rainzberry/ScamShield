from __future__ import annotations

import datetime as dt
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance

from ..configs.settings import RANDOM_SEED, URL_THRESHOLD
from ..evaluation.metrics import compute_binary_metrics
from ..inference.model_store import save_bundle
from ..preprocessing.splitting import dataset_fingerprint
from ..url_analysis.features import FEATURE_NAMES, features_dataframe

DEFAULT_URL_PARAMS: Dict[str, Any] = {
    "n_estimators": 300,
    "grid": [{"max_depth": None, "min_samples_leaf": 1}, {"max_depth": 30, "min_samples_leaf": 2},
             {"max_depth": 20, "min_samples_leaf": 5}],
    "perm_sample": 5000, "perm_repeats": 3,
}


def _rf(n: int, g: Dict[str, Any], seed: int) -> RandomForestClassifier:
    return RandomForestClassifier(n_estimators=n, max_depth=g["max_depth"], min_samples_leaf=g["min_samples_leaf"],
                                  class_weight="balanced_subsample", n_jobs=-1, random_state=seed)


def train_url_model(train_df: pd.DataFrame, val_df: pd.DataFrame, out_dir, params: Optional[Dict[str, Any]] = None,
                    seed: int = RANDOM_SEED) -> Dict[str, Any]:
    p = {**DEFAULT_URL_PARAMS, **(params or {})}
    Xtr, mtr = features_dataframe(train_df["url"])
    Xva, mva = features_dataframe(val_df["url"])
    ytr = train_df["label"].astype(int).values[mtr]
    yva = val_df["label"].astype(int).values[mva]
    trials, best = [], None
    for g in p["grid"]:
        rf = _rf(p["n_estimators"], g, seed).fit(Xtr, ytr)
        m = compute_binary_metrics(yva, rf.predict_proba(Xva)[:, list(rf.classes_).index(1)], URL_THRESHOLD)
        trials.append({**g, "val_f1": m["f1"], "val_pr_auc": m["pr_auc"]})
        score = (m["f1"], m["pr_auc"] or 0.0)
        if best is None or score > best[0]:
            best = (score, rf, m)
    _, rf, val_metrics = best
    baselines = np.median(Xtr[ytr == 0], axis=0)
    rng = np.random.RandomState(seed)
    k = min(len(yva), p["perm_sample"])
    sel = rng.choice(len(yva), size=k, replace=False)
    perm = {}
    if len(np.unique(yva[sel])) == 2:
        r = permutation_importance(rf, Xva[sel], yva[sel], scoring="f1", n_repeats=p["perm_repeats"],
                                   random_state=seed, n_jobs=1)
        perm = {n: float(v) for n, v in zip(FEATURE_NAMES, r.importances_mean)}
    fp = dataset_fingerprint(train_df["url"], train_df["label"])
    meta = {
        "model_version": f"url-rf-1.0.0+{fp[:8]}",
        "model_type": "Random Forest on offline lexical URL features",
        "task": "url_legitimate_vs_phishing", "classes": {"0": "legitimate", "1": "phishing"},
        "threshold": URL_THRESHOLD, "feature_names": FEATURE_NAMES,
        "baselines": {n: float(v) for n, v in zip(FEATURE_NAMES, baselines)},
        "impurity_importance": {n: float(v) for n, v in zip(FEATURE_NAMES, rf.feature_importances_)},
        "permutation_importance": perm, "grid_search": trials, "params": p, "seed": seed,
        "data_fingerprint": fp, "n_train": int(len(ytr)), "n_val": int(len(yva)),
        "n_malformed_dropped": int((~mtr).sum() + (~mva).sum()), "validation_metrics": val_metrics,
        "trained_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "sklearn_version": sklearn.__version__,
        "caveats": ["Trained on URL strings only; no network or page-content features.",
                    "Random-forest probabilities are vote fractions and are NOT calibrated (see Brier/ECE).",
                    "Public phishing-URL datasets can contain collection artefacts; treat reported scores as optimistic."],
    }
    save_bundle(out_dir, rf, meta)
    return meta