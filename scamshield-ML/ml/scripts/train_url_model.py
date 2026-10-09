"""Train the URL Random Forest. Uses TRAIN + VALIDATION only.

Windows:  python ml\\scripts\\train_url_model.py
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ml.configs.settings import MODELS_DIR, PROCESSED_DIR, URL_MODEL_DIRNAME  # noqa: E402
from ml.training.url_trainer import train_url_model  # noqa: E402


def main() -> int:
    paths = {s: PROCESSED_DIR / f"url_{s}.csv.gz" for s in ("train", "val")}
    if not all(p.exists() for p in paths.values()):
        print("Processed URL data missing. Run scripts\\preprocess_data.py first.")
        return 1
    tr, va = (pd.read_csv(paths[s]) for s in ("train", "val"))
    print(f"Extracting features and training on {len(tr)} URLs (validation {len(va)}) ...")
    meta = train_url_model(tr, va, MODELS_DIR / URL_MODEL_DIRNAME)
    v = meta["validation_metrics"]
    print("Model version:", meta["model_version"])
    print(f"VALIDATION  acc={v['accuracy']:.4f} prec={v['precision']:.4f} rec={v['recall']:.4f} f1={v['f1']:.4f}")
    top = sorted(meta["impurity_importance"].items(), key=lambda kv: -kv[1])[:8]
    print("Top features (impurity):", ", ".join(f"{k}={v:.3f}" for k, v in top))
    return 0


if __name__ == "__main__":
    sys.exit(main())