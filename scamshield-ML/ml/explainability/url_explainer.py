from __future__ import annotations

from typing import Any, Dict

import numpy as np

from ..url_analysis.features import FEATURE_NAMES


def explain_url(model, features: Dict[str, float], top_k: int = 8) -> Dict[str, Any]:
    """Single-feature ablation: contribution_i = P(x) - P(x with feature i set to benign median)."""
    meta = model.metadata
    names = list(meta["feature_names"])
    if names != FEATURE_NAMES:
        raise ValueError("URL model feature schema differs from current code - retrain the URL model.")
    clf = model.estimator
    pos = list(clf.classes_).index(1)
    x = np.array([[features[n] for n in names]], dtype=float)
    base = np.array([meta["baselines"][n] for n in names], dtype=float)
    p = float(clf.predict_proba(x)[0, pos])
    ablated = np.tile(x, (len(names), 1))
    for i in range(len(names)):
        ablated[i, i] = base[i]
    p_abl = clf.predict_proba(ablated)[:, pos]
    contrib = p - p_abl
    imp = meta.get("permutation_importance", {})
    rows = []
    for i in np.argsort(-np.abs(contrib)):
        if abs(contrib[i]) < 1e-6 or len(rows) >= top_k:
            continue
        rows.append({
            "feature": names[i], "value": float(x[0, i]), "benign_median": float(base[i]),
            "contribution": round(float(contrib[i]), 4),
            "direction": "phishing" if contrib[i] > 0 else "legitimate",
            "global_importance": round(float(meta["impurity_importance"].get(names[i], 0.0)), 4),
            "global_permutation_importance": round(float(imp.get(names[i], 0.0)), 4),
        })
    return {
        "probability_phishing": p, "features": rows,
        "method": "Single-feature ablation vs benign training median (interactions are not summed; contributions need not add up to P).",
    }