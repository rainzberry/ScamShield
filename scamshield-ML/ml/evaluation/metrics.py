from __future__ import annotations

from typing import Any, Dict

import numpy as np
from sklearn.metrics import (accuracy_score, average_precision_score, brier_score_loss,
                             classification_report, confusion_matrix,
                             precision_recall_fscore_support, roc_auc_score)


def expected_calibration_error(y, p, bins: int = 10) -> float:
    edges = np.linspace(0, 1, bins + 1)
    ece = 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (p >= lo) & ((p < hi) if hi < 1 else (p <= hi))
        if m.any():
            ece += m.mean() * abs(y[m].mean() - p[m].mean())
    return float(ece)


def compute_binary_metrics(y_true, y_prob, threshold: float = 0.5) -> Dict[str, Any]:
    y = np.asarray(y_true).astype(int)
    p = np.asarray(y_prob, dtype=float)
    pred = (p >= threshold).astype(int)
    tn, fp, fn, tp = (int(v) for v in confusion_matrix(y, pred, labels=[0, 1]).ravel())
    prec, rec, f1, _ = precision_recall_fscore_support(y, pred, average="binary", pos_label=1, zero_division=0)
    two = len(np.unique(y)) == 2
    return {
        "n": int(len(y)), "threshold": threshold,
        "class_distribution": {"0": int((y == 0).sum()), "1": int((y == 1).sum())},
        "accuracy": float(accuracy_score(y, pred)), "precision": float(prec),
        "recall": float(rec), "f1": float(f1),
        "roc_auc": float(roc_auc_score(y, p)) if two else None,
        "pr_auc": float(average_precision_score(y, p)) if two else None,
        "brier": float(brier_score_loss(y, p)), "ece": expected_calibration_error(y, p),
        "confusion_matrix": {"tn": tn, "fp": fp, "fn": fn, "tp": tp, "matrix": [[tn, fp], [fn, tp]]},
        "classification_report": classification_report(
            y, pred, labels=[0, 1], target_names=["negative", "positive"], output_dict=True, zero_division=0),
    }