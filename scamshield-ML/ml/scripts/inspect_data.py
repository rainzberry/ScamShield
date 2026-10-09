"""Inspect downloaded datasets and write data/interim/dataset_report.json (real counts, no guesses).

Windows:  python ml\\scripts\\inspect_data.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ml.configs.settings import INTERIM_DIR, RAW_DIR  # noqa: E402
from ml.datasets.loaders import load_all_text_sources, load_phiusiil  # noqa: E402


def main() -> int:
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    report = {}

    df, rep = load_all_text_sources(RAW_DIR)
    if df.empty:
        print(f"[text] No text datasets found under {RAW_DIR}. Run download_data.py / see DATASETS.md")
        report["text"] = {"status": "no data found"}
    else:
        n_chars = (df["subject"] + " " + df["body"]).str.len()
        report["text"] = {
            **rep, "total_records": int(len(df)),
            "label_counts": {str(k): int(v) for k, v in df["label"].value_counts().items()},
            "exact_duplicate_rows": int(df.duplicated(subset=["subject", "body"]).sum()),
            "empty_text_rows": int((n_chars <= 1).sum()),
            "length_chars": {k: float(v) for k, v in n_chars.describe().items()},
        }
        print("[text] total records:", len(df))
        for src, s in report["text"]["sources"].items():
            print(f"   {src:28s} n={s['n_records']:7d} labels={s['label_counts']} origins={s['origin_counts']}")
        for fname, r in rep.get("curated_files", {}).items():
            print("   curated file", fname, r)

    phi = load_phiusiil(RAW_DIR)
    if phi.empty:
        print(f"[url] PhiUSIIL not found under {RAW_DIR / 'phiusiil'}")
        report["url"] = {"status": "no data found"}
    else:
        report["url"] = {
            "total_records": int(len(phi)),
            "label_counts_1_is_phishing": {str(k): int(v) for k, v in phi["label"].value_counts().items()},
            "null_urls": int(phi["url"].isna().sum()),
            "exact_duplicate_urls": int(phi.duplicated("url").sum()),
            "url_length_chars": {k: float(v) for k, v in phi["url"].str.len().describe().items()},
            "label_semantics": "UCI label (1=legitimate, 0=phishing) was inverted: here 1 = phishing.",
            "sample_phishing": phi[phi.label == 1]["url"].head(3).tolist(),
            "sample_legitimate": phi[phi.label == 0]["url"].head(3).tolist(),
        }
        print("[url] total:", len(phi), report["url"]["label_counts_1_is_phishing"])
        print("   CHECK the samples look right (phishing should look odd):")
        print("   phishing  :", report["url"]["sample_phishing"])
        print("   legitimate:", report["url"]["sample_legitimate"])

    out = INTERIM_DIR / "dataset_report.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("Report written to", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())