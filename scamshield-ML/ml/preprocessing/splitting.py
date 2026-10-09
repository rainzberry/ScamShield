from __future__ import annotations

import hashlib
from typing import Iterable, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold, train_test_split


def text_key(s: str) -> str:
    return hashlib.md5(s.encode("utf-8", errors="ignore")).hexdigest()


def dataset_fingerprint(values: Iterable, labels: Iterable) -> str:
    h = hashlib.sha256()
    for v, l in sorted(zip(map(str, values), map(int, labels))):
        h.update(v.encode("utf-8", errors="ignore"))
        h.update(b"\x00" + str(l).encode() + b"\x01")
    return h.hexdigest()


def stratified_split(
    df: pd.DataFrame, label_col: str = "label", seed: int = 42,
    train: float = 0.70, val: float = 0.15, test: float = 0.15,
    strat_extra: Optional[str] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    assert abs(train + val + test - 1.0) < 1e-9
    key = df[label_col].astype(str)
    if strat_extra:
        combo = key + "|" + df[strat_extra].astype(str)
        if combo.value_counts().min() >= 10:
            key = combo
    idx = np.arange(len(df))
    tr, tmp = train_test_split(idx, test_size=1 - train, stratify=key.values, random_state=seed)
    va, te = train_test_split(
        tmp, test_size=test / (val + test), stratify=key.values[tmp], random_state=seed
    )
    return (df.iloc[tr].reset_index(drop=True), df.iloc[va].reset_index(drop=True),
            df.iloc[te].reset_index(drop=True))


def grouped_stratified_split(
    df: pd.DataFrame, label_col: str, group_col: str, seed: int = 42,
    n_splits: int = 20, n_train: int = 14, n_val: int = 3,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """~70/15/15 split in which no group (e.g. registered domain) appears in two splits."""
    sgkf = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    folds = np.full(len(df), -1)
    for i, (_, idx) in enumerate(sgkf.split(df, df[label_col], df[group_col])):
        folds[idx] = i
    tr = df[folds < n_train]
    va = df[(folds >= n_train) & (folds < n_train + n_val)]
    te = df[folds >= n_train + n_val]
    return tr.reset_index(drop=True), va.reset_index(drop=True), te.reset_index(drop=True)