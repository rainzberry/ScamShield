from __future__ import annotations

import math
from typing import Any, Dict, List

import numpy as np


def explain_text(model, cleaned_text: str, top_word: int = 8, top_char: int = 5,
                 top_neg_word: int = 4, top_neg_char: int = 2) -> Dict[str, Any]:
    """Exact linear explanation: contribution_i = tfidf_i * coef_i (log-odds units)."""
    pipe = model.estimator
    fu, clf = pipe.named_steps["features"], pipe.named_steps["clf"]
    names = model.cache.get("names")
    if names is None:
        names = np.asarray(fu.get_feature_names_out(), dtype=object)
        model.cache["names"] = names
    X = fu.transform([cleaned_text]).tocsr()
    pos = list(clf.classes_).index(1)
    p = float(clf.predict_proba(X)[0, pos])
    coef = clf.coef_[0]
    intercept = float(clf.intercept_[0])
    idx, vals = X.indices, X.data
    contrib = vals * coef[idx]
    logit = float(contrib.sum() + intercept)
    rows: List[Dict[str, Any]] = []
    for i, v, c in zip(idx, vals, contrib):
        analyzer, _, term = str(names[i]).partition("__")
        rows.append({"feature": term, "analyzer": analyzer, "tfidf": round(float(v), 5),
                     "coefficient": round(float(coef[i]), 5), "contribution": round(float(c), 5),
                     "direction": "suspicious" if c > 0 else "safe"})

    def pick(an, k, positive):
        sel = [r for r in rows if r["analyzer"] == an and (r["contribution"] > 0) == positive and r["contribution"] != 0]
        return sorted(sel, key=lambda r: -abs(r["contribution"]))[:k]

    feats = (pick("word", top_word, True) + pick("char", top_char, True)
             + pick("word", top_neg_word, False) + pick("char", top_neg_char, False))
    return {
        "probability_suspicious": p, "intercept": round(intercept, 5), "logit": logit,
        "n_active_features": int(len(idx)), "features": feats,
        "method": "Linear model: contribution = TF-IDF weight x logistic-regression coefficient (log-odds); positive pushes toward SUSPICIOUS.",
    }