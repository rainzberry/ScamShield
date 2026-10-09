"""Clean, de-duplicate and split data -> data/processed/*.csv.gz and manifest.json.

Windows:  python ml\\scripts\\preprocess_data.py
          python ml\\scripts\\preprocess_data.py --text-only
          python ml\\scripts\\preprocess_data.py --url-only --tranco-benign 20000   (optional, see DATASETS.md)
"""
import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ml.configs.settings import MAX_TEXT_CHARS, PROCESSED_DIR, RANDOM_SEED, RAW_DIR, SPLIT_FRACTIONS  # noqa: E402
from ml.datasets.loaders import load_all_text_sources, load_phiusiil, load_tranco  # noqa: E402
from ml.features.common import split_hostname  # noqa: E402
from ml.preprocessing.splitting import grouped_stratified_split, stratified_split, text_key  # noqa: E402
from ml.preprocessing.text_cleaning import clean_text, compose_email_text  # noqa: E402
from ml.url_analysis.features import normalize_url  # noqa: E402


def update_manifest(key, value):
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    p = PROCESSED_DIR / "manifest.json"
    m = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    m[key] = value
    p.write_text(json.dumps(m, indent=2), encoding="utf-8")


def describe(df, extra=None):
    d = {"n": int(len(df)), "label_counts": {str(k): int(v) for k, v in df["label"].value_counts().items()}}
    if extra and extra in df:
        d["by_source"] = {str(k): int(v) for k, v in df[extra].value_counts().items()}
    return d


def build_text(max_chars: int) -> bool:
    df, _ = load_all_text_sources(RAW_DIR)
    if df.empty:
        print("[text] no raw text data found - skipping")
        return False
    n_loaded = len(df)
    df["text_clean"] = [clean_text(compose_email_text(s, b), max_chars) for s, b in zip(df["subject"], df["body"])]
    df = df[df["text_clean"].str.len() >= 15].copy()
    n_short = n_loaded - len(df)
    df["key"] = df["text_clean"].map(text_key)
    nun = df.groupby("key")["label"].nunique()
    conflict = set(nun[nun > 1].index)
    n_conflict = int(df["key"].isin(conflict).sum())
    df = df[~df["key"].isin(conflict)]
    before = len(df)
    df = df.drop_duplicates("key").reset_index(drop=True)
    n_dup = before - len(df)
    df["id"] = np.arange(len(df))
    tr, va, te = stratified_split(df, "label", RANDOM_SEED, strat_extra="source", **SPLIT_FRACTIONS)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    cols = ["id", "source", "origin", "label", "text_clean"]
    for name, part in (("train", tr), ("val", va), ("test", te)):
        part[cols].to_csv(PROCESSED_DIR / f"text_{name}.csv.gz", index=False)
    info = {"loaded": int(n_loaded), "removed_too_short": int(n_short), "removed_label_conflicts": n_conflict,
            "removed_exact_duplicates": int(n_dup), "kept": int(len(df)), "seed": RANDOM_SEED,
            "train": describe(tr, "source"), "val": describe(va, "source"), "test": describe(te, "source")}
    update_manifest("text", info)
    print("[text]", json.dumps(info, indent=2))
    return True


def _group(u):
    try:
        url, _ = normalize_url(u)
        host = urlsplit(url).hostname or ""
        return split_hostname(host)["registered"] if host else None
    except ValueError:
        return None


def build_url(tranco_n: int) -> bool:
    df = load_phiusiil(RAW_DIR)
    if df.empty:
        print("[url] PhiUSIIL not found - skipping")
        return False
    extra = load_tranco(RAW_DIR, tranco_n)
    if not extra.empty:
        print(f"[url] adding {len(extra)} Tranco benign domains (domain-only rows bias path features!)")
        df = pd.concat([df, extra], ignore_index=True)
    n_loaded = len(df)
    df = df.dropna(subset=["url"]).copy()
    df["url"] = df["url"].astype(str).str.strip()
    df = df[df["url"] != ""]
    df["group"] = [_group(u) for u in df["url"]]
    n_unparseable = int(df["group"].isna().sum())
    df = df.dropna(subset=["group"]).copy()
    df["key"] = df["url"].str.lower()
    nun = df.groupby("key")["label"].nunique()
    conflict = set(nun[nun > 1].index)
    n_conflict = int(df["key"].isin(conflict).sum())
    df = df[~df["key"].isin(conflict)]
    before = len(df)
    df = df.drop_duplicates("key").reset_index(drop=True)
    tr, va, te = grouped_stratified_split(df, "label", "group", RANDOM_SEED)
    g = [set(x["group"]) for x in (tr, va, te)]
    assert not (g[0] & g[1] or g[0] & g[2] or g[1] & g[2]), "domain leakage between splits!"
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    for name, part in (("train", tr), ("val", va), ("test", te)):
        part[["url", "label", "source", "group"]].to_csv(PROCESSED_DIR / f"url_{name}.csv.gz", index=False)
    info = {"loaded": int(n_loaded), "removed_unparseable": n_unparseable, "removed_label_conflicts": n_conflict,
            "removed_exact_duplicates": int(before - len(df)), "kept": int(len(df)), "seed": RANDOM_SEED,
            "split": "grouped by registered domain (no domain appears in two splits)",
            "train": describe(tr, "source"), "val": describe(va, "source"), "test": describe(te, "source")}
    update_manifest("url", info)
    print("[url]", json.dumps(info, indent=2))
    for name, part in (("train", tr), ("val", va), ("test", te)):
        if part["label"].nunique() < 2:
            print(f"WARNING: url {name} split has a single class")
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--text-only", action="store_true")
    ap.add_argument("--url-only", action="store_true")
    ap.add_argument("--max-chars", type=int, default=MAX_TEXT_CHARS)
    ap.add_argument("--tranco-benign", type=int, default=0, help="optional: add N Tranco domains as benign (default 0)")
    a = ap.parse_args()
    ok = True
    if not a.url_only:
        ok &= build_text(a.max_chars)
    if not a.text_only:
        ok &= build_url(a.tranco_benign)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())