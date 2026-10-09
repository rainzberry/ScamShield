from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

from ..configs.settings import (MODELS_DIR, PROCESSED_DIR, REPORTS_DIR, TEXT_MODEL_DIRNAME,
                                URL_MODEL_DIRNAME)
from ..inference.model_store import load_bundle
from ..preprocessing.splitting import dataset_fingerprint
from ..url_analysis.features import features_dataframe
from .metrics import compute_binary_metrics

SPLITS = ("train", "val", "test")


def _write(report: Dict[str, Any], name: str, reports_dir: Path):
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / f"{name}.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = [f"# {name}", "", f"Model version: `{report.get('model_version')}`", ""]
    if report.get("warnings"):
        lines += ["**Warnings:** " + "; ".join(report["warnings"]), ""]
    lines += ["| split | n | accuracy | precision | recall | F1 | ROC-AUC | PR-AUC | Brier | ECE | TN | FP | FN | TP |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    f = lambda v: "n/a" if v is None else f"{v:.4f}"
    for s, m in report["splits"].items():
        c = m["confusion_matrix"]
        lines.append(f"| {s} | {m['n']} | {f(m['accuracy'])} | {f(m['precision'])} | {f(m['recall'])} | {f(m['f1'])} | "
                     f"{f(m['roc_auc'])} | {f(m['pr_auc'])} | {f(m['brier'])} | {f(m['ece'])} | {c['tn']} | {c['fp']} | {c['fn']} | {c['tp']} |")
    lines += ["", "Class distribution per split (0/1): " + ", ".join(
        f"{s}={m['class_distribution']['0']}/{m['class_distribution']['1']}" for s, m in report["splits"].items())]
    (reports_dir / f"{name}.md").write_text("\n".join(lines), encoding="utf-8")


def _probs_text(pipe, texts, batch: int = 5000):
    out = []
    for i in range(0, len(texts), batch):
        out.append(pipe.predict_proba(texts[i:i + batch])[:, 1])
    return np.concatenate(out) if out else np.array([])


def evaluate_text(models_dir=MODELS_DIR, processed_dir=PROCESSED_DIR, reports_dir=REPORTS_DIR) -> Dict[str, Any]:
    model = load_bundle(Path(models_dir) / TEXT_MODEL_DIRNAME)
    if model is None:
        raise FileNotFoundError("Text model not found. Run scripts/train_text_model.py first.")
    thr = model.metadata["threshold"]
    report: Dict[str, Any] = {"model_version": model.version, "threshold": thr, "splits": {}, "test_by_source": {}, "warnings": []}
    for s in SPLITS:
        df = pd.read_csv(Path(processed_dir) / f"text_{s}.csv.gz")
        df["text_clean"] = df["text_clean"].fillna("").astype(str)
        if s == "train" and dataset_fingerprint(df["text_clean"], df["label"]) != model.metadata["data_fingerprint"]:
            report["warnings"].append("Processed TRAIN data differs from the data this model was trained on - retrain.")
        pr = _probs_text(model.estimator, df["text_clean"].tolist())
        report["splits"][s] = compute_binary_metrics(df["label"].values, pr, thr)
        if s == "test":
            for src, g in df.assign(_p=pr).groupby("source"):
                report["test_by_source"][src] = compute_binary_metrics(g["label"].values, g["_p"].values, thr)
    _write(report, "text_model_evaluation", Path(reports_dir))
    return report


def evaluate_url(models_dir=MODELS_DIR, processed_dir=PROCESSED_DIR, reports_dir=REPORTS_DIR) -> Dict[str, Any]:
    model = load_bundle(Path(models_dir) / URL_MODEL_DIRNAME)
    if model is None:
        raise FileNotFoundError("URL model not found. Run scripts/train_url_model.py first.")
    thr = model.metadata["threshold"]
    report: Dict[str, Any] = {"model_version": model.version, "threshold": thr, "splits": {}, "warnings": [],
                              "top_features": sorted(model.metadata["impurity_importance"].items(), key=lambda kv: -kv[1])[:10]}
    for s in SPLITS:
        df = pd.read_csv(Path(processed_dir) / f"url_{s}.csv.gz")
        X, mask = features_dataframe(df["url"])
        y = df["label"].values[mask]
        if s == "train" and dataset_fingerprint(df["url"], df["label"]) != model.metadata["data_fingerprint"]:
            report["warnings"].append("Processed TRAIN data differs from the data this model was trained on - retrain.")
        pr = model.estimator.predict_proba(X)[:, list(model.estimator.classes_).index(1)]
        report["splits"][s] = compute_binary_metrics(y, pr, thr)
    _write(report, "url_model_evaluation", Path(reports_dir))
    return report


def leave_one_source_out(models_dir=MODELS_DIR, processed_dir=PROCESSED_DIR, reports_dir=REPORTS_DIR) -> Dict[str, Any]:
    """Train on all other sources, test on the held-out source: measures source-style overfitting."""
    from ..training.text_trainer import DEFAULT_TEXT_PARAMS, fit_text_pipeline
    model = load_bundle(Path(models_dir) / TEXT_MODEL_DIRNAME)
    C = model.metadata["chosen_C"] if model else 1.0
    params = model.metadata["params"] if model else DEFAULT_TEXT_PARAMS
    df = pd.concat([pd.read_csv(Path(processed_dir) / f"text_{s}.csv.gz") for s in SPLITS], ignore_index=True)
    df["text_clean"] = df["text_clean"].fillna("").astype(str)
    rep: Dict[str, Any] = {"C": C, "held_out": {}}
    for src in sorted(df["source"].unique()):
        te, tr = df[df["source"] == src], df[df["source"] != src]
        if tr["label"].nunique() < 2 or len(te) < 20:
            rep["held_out"][src] = {"skipped": "not enough data or single-class training remainder"}
            continue
        pipe = fit_text_pipeline(tr["text_clean"], tr["label"], C, params)
        rep["held_out"][src] = compute_binary_metrics(te["label"].values, _probs_text(pipe, te["text_clean"].tolist()), 0.5)
    Path(reports_dir).mkdir(parents=True, exist_ok=True)
    (Path(reports_dir) / "text_leave_one_source_out.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    return rep