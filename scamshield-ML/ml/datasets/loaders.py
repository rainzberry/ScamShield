from __future__ import annotations

import mailbox
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd

from ..configs.settings import RAW_DIR
from ..preprocessing.email_parsing import parse_eml_bytes

_COLS = ["source", "origin", "subject", "body", "sender", "label"]
_ALIASES = {
    "subject": ["subject"],
    "body": ["body", "text", "message", "email_text", "email text", "content"],
    "sender": ["sender", "from"],
    "label": ["label", "class", "target", "email_type", "type"],
}
_POS = {"1", "spam", "phishing", "phishing email", "fraud", "malicious", "scam", "phish"}
_NEG = {"0", "ham", "legitimate", "safe email", "safe", "benign", "not spam", "legit"}


def norm_label(v):
    s = str(v).strip().lower()
    try:
        s = str(int(float(s)))
    except ValueError:
        pass
    if s in _POS:
        return 1
    if s in _NEG:
        return 0
    return None


def _pick(cols: Dict[str, str], names: List[str]):
    for n in names:
        if n in cols:
            return cols[n]
    return None


def load_spamassassin(raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    base = Path(raw_dir) / "spamassassin"
    rows: List[Dict[str, Any]] = []
    if base.is_dir():
        for d in sorted(p for p in base.rglob("*") if p.is_dir()):
            name = d.name.lower()
            if "ham" in name:
                label, origin = 0, "ham"
            elif "spam" in name:
                label, origin = 1, "spam"
            else:
                continue
            for f in d.iterdir():
                if not f.is_file() or f.name.startswith("cmds"):
                    continue
                try:
                    m = parse_eml_bytes(f.read_bytes())
                except Exception:
                    continue
                rows.append({"source": "spamassassin", "origin": origin, "subject": m["subject"],
                             "body": m["body"], "sender": m["sender"], "label": label})
    return pd.DataFrame(rows, columns=_COLS)


def load_curated_csvs(raw_dir: Path = RAW_DIR, skip_spamassassin: bool = False) -> Tuple[pd.DataFrame, Dict]:
    base = Path(raw_dir) / "phishing_email_datasets"
    frames, rep = [], {}
    if not base.is_dir():
        return pd.DataFrame(columns=_COLS), rep
    for f in sorted(base.glob("*.csv")):
        stem = f.stem.lower()
        if skip_spamassassin and "spamassassin" in stem:
            rep[f.name] = {"skipped": "raw SpamAssassin corpus already loaded (avoids overlap)"}
            continue
        try:
            raw = pd.read_csv(f, low_memory=False, on_bad_lines="skip")
        except Exception as e:
            rep[f.name] = {"error": str(e)}
            continue
        cols = {c.strip().lower(): c for c in raw.columns}
        c_sub, c_body = _pick(cols, _ALIASES["subject"]), _pick(cols, _ALIASES["body"])
        c_snd, c_lab = _pick(cols, _ALIASES["sender"]), _pick(cols, _ALIASES["label"])
        if c_lab is None or (c_body is None and c_sub is None):
            rep[f.name] = {"error": f"cannot find label/text columns in {list(raw.columns)}"}
            continue
        lab = raw[c_lab].map(norm_label)
        keep = lab.notna()
        df = pd.DataFrame({
            "source": f.stem,
            "subject": raw[c_sub].fillna("").astype(str) if c_sub else "",
            "body": raw[c_body].fillna("").astype(str) if c_body else "",
            "sender": raw[c_snd].fillna("").astype(str) if c_snd else "",
            "label": lab,
        })[keep].copy()
        df["label"] = df["label"].astype(int)
        if "nazario" in stem:
            df["origin"] = "phishing"
        elif "nigerian" in stem:
            df["origin"] = "fraud"
        else:
            df["origin"] = df["label"].map({0: "legitimate", 1: "spam_or_phishing"})
        frames.append(df[_COLS])
        rep[f.name] = {"rows_read": int(len(raw)), "rows_kept": int(keep.sum()),
                       "dropped_unmapped_label": int((~keep).sum())}
    return (pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=_COLS)), rep


def load_nazario_mbox(raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    base = Path(raw_dir) / "nazario"
    rows = []
    if base.is_dir():
        for f in sorted(p for p in base.iterdir() if p.is_file()):
            try:
                for msg in mailbox.mbox(str(f)):
                    m = parse_eml_bytes(msg.as_bytes())
                    rows.append({"source": "nazario_mbox", "origin": "phishing", "subject": m["subject"],
                                 "body": m["body"], "sender": m["sender"], "label": 1})
            except Exception:
                continue
    return pd.DataFrame(rows, columns=_COLS)


def load_all_text_sources(raw_dir: Path = RAW_DIR) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    sa = load_spamassassin(raw_dir)
    cur, cur_rep = load_curated_csvs(raw_dir, skip_spamassassin=not sa.empty)
    naz = load_nazario_mbox(raw_dir)
    df = pd.concat([x for x in (sa, cur, naz) if not x.empty], ignore_index=True) \
        if any(not x.empty for x in (sa, cur, naz)) else pd.DataFrame(columns=_COLS)
    report: Dict[str, Any] = {"curated_files": cur_rep, "sources": {}}
    if not df.empty:
        df["subject"] = df["subject"].fillna("").astype(str)
        df["body"] = df["body"].fillna("").astype(str)
        for src, g in df.groupby("source"):
            report["sources"][src] = {
                "n_records": int(len(g)),
                "label_counts": {str(k): int(v) for k, v in g["label"].value_counts().items()},
                "origin_counts": {str(k): int(v) for k, v in g["origin"].value_counts().items()},
                "empty_body": int((g["body"].str.strip() == "").sum()),
            }
    return df, report


def load_phiusiil(raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    """Returns columns [url, label, source] with label 1 = phishing (UCI label is inverted here)."""
    base = Path(raw_dir) / "phiusiil"
    for f in sorted(base.rglob("*.csv")) if base.is_dir() else []:
        try:
            df = pd.read_csv(f, usecols=lambda c: c.strip().lower() in ("url", "label"), low_memory=False)
        except Exception:
            continue
        cols = {c.strip().lower(): c for c in df.columns}
        if "url" in cols and "label" in cols:
            out = pd.DataFrame({"url": df[cols["url"]].astype(str).str.strip(),
                                "label": 1 - df[cols["label"]].astype(int)})
            out["source"] = "phiusiil"
            return out
    return pd.DataFrame(columns=["url", "label", "source"])


def load_tranco(raw_dir: Path = RAW_DIR, n: int = 0) -> pd.DataFrame:
    base = Path(raw_dir) / "tranco"
    for f in sorted(base.glob("*.csv")) if base.is_dir() and n > 0 else []:
        df = pd.read_csv(f, header=None, names=["rank", "domain"], nrows=n)
        out = pd.DataFrame({"url": "https://" + df["domain"].astype(str), "label": 0})
        out["source"] = "tranco"
        return out
    return pd.DataFrame(columns=["url", "label", "source"])