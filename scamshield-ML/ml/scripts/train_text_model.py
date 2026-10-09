"""Train the Stage-1 text model (SAFE vs SUSPICIOUS). Uses TRAIN + VALIDATION only.

Windows:  python ml\\scripts\\train_text_model.py
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ml.configs.settings import MODELS_DIR, PROCESSED_DIR, TEXT_MODEL_DIRNAME  # noqa: E402
from ml.training.text_trainer import train_text_model  # noqa: E402


def main() -> int:
    paths = {s: PROCESSED_DIR / f"text_{s}.csv.gz" for s in ("train", "val")}
    if not all(p.exists() for p in paths.values()):
        print("Processed text data missing. Run scripts\\preprocess_data.py first.")
        return 1
    tr, va = (pd.read_csv(paths[s]) for s in ("train", "val"))
    for d in (tr, va):
        d["text_clean"] = d["text_clean"].fillna("").astype(str)
    print(f"Training on {len(tr)} rows, validating on {len(va)} rows ...")
    meta = train_text_model(tr, va, MODELS_DIR / TEXT_MODEL_DIRNAME)
    v = meta["validation_metrics"]
    print("Model version:", meta["model_version"], "| chosen C:", meta["chosen_C"])
    print(f"VALIDATION  acc={v['accuracy']:.4f} prec={v['precision']:.4f} rec={v['recall']:.4f} f1={v['f1']:.4f}")
    print("Saved to", MODELS_DIR / TEXT_MODEL_DIRNAME, "- now run scripts\\evaluate_models.py for the test report.")
    return 0


if __name__ == "__main__":
    sys.exit(main())