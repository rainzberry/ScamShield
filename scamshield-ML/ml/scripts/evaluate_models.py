"""Evaluate saved models on TRAIN / VALIDATION / TEST and write reports to ml/evaluation/reports/.

Windows:  python ml\\scripts\\evaluate_models.py
          python ml\\scripts\\evaluate_models.py --text
          python ml\\scripts\\evaluate_models.py --url
          python ml\\scripts\\evaluate_models.py --loso      (slow: leave-one-source-out text check)
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ml.configs.settings import REPORTS_DIR  # noqa: E402
from ml.evaluation.evaluate import evaluate_text, evaluate_url, leave_one_source_out  # noqa: E402


def show(name, rep):
    print(f"\n=== {name} ({rep['model_version']}) ===")
    for w in rep.get("warnings", []):
        print("WARNING:", w)
    for s, m in rep["splits"].items():
        print(f"{s:5s} n={m['n']:7d} acc={m['accuracy']:.4f} prec={m['precision']:.4f} rec={m['recall']:.4f} "
              f"f1={m['f1']:.4f} roc_auc={m['roc_auc']} pr_auc={m['pr_auc']} brier={m['brier']:.4f} ece={m['ece']:.4f}")
        print(f"      confusion {m['confusion_matrix']['matrix']}  class_dist {m['class_distribution']}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", action="store_true")
    ap.add_argument("--url", action="store_true")
    ap.add_argument("--loso", action="store_true")
    a = ap.parse_args()
    if not (a.text or a.url or a.loso):
        a.text = a.url = True
    rc = 0
    try:
        if a.text:
            show("TEXT MODEL", evaluate_text())
        if a.url:
            show("URL MODEL", evaluate_url())
        if a.loso:
            rep = leave_one_source_out()
            print("\n=== LEAVE-ONE-SOURCE-OUT (text) ===")
            for src, m in rep["held_out"].items():
                print(src, m if "skipped" in m else f"n={m['n']} acc={m['accuracy']:.4f} recall={m['recall']:.4f} dist={m['class_distribution']}")
    except FileNotFoundError as e:
        print(e)
        rc = 1
    print("\nReports saved in", REPORTS_DIR)
    return rc


if __name__ == "__main__":
    sys.exit(main())