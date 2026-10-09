"""Download datasets that allow scripted download.

Windows:  python ml\\scripts\\download_data.py
          python ml\\scripts\\download_data.py --only phiusiil
"""
import argparse
import shutil
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ml.configs.settings import RAW_DIR  # noqa: E402

SPAMASSASSIN_BASE = "https://spamassassin.apache.org/old/publiccorpus/"
SPAMASSASSIN_FILES = [
    "20030228_easy_ham.tar.bz2", "20030228_easy_ham_2.tar.bz2", "20030228_hard_ham.tar.bz2",
    "20030228_spam.tar.bz2", "20050311_spam_2.tar.bz2",
]
PHIUSIIL_URL = "https://archive.ics.uci.edu/static/public/967/phiusiil+phishing+url+dataset.zip"
TRANCO_URL = "https://tranco-list.eu/top-1m.csv.zip"

MANUAL = """
MANUAL DOWNLOADS (cannot be scripted reliably):
  1. Curated phishing-email CSVs (CEAS_08, Nazario, Nigerian_Fraud, Enron, Ling, SpamAssassin):
     search figshare for 'Phishing Email Curated Datasets' (Champa et al., 2024), check the license on the
     record page, and put the .csv files in:   ml\\data\\raw\\phishing_email_datasets\\
  2. Nazario phishing corpus (optional, mbox files): https://monkey.org/~jose/phishing/
     put the mbox files in:                    ml\\data\\raw\\nazario\\
  3. If an automatic download below failed, download the file in a browser and extract it to the
     folder named in the error message.
"""


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "ScamShield-academic-project/1.0"})
    with urllib.request.urlopen(req, timeout=180) as r, open(dest, "wb") as f:
        shutil.copyfileobj(r, f)


def safe_extract_tar(tar_path: Path, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    root = dest.resolve()
    with tarfile.open(tar_path) as tf:
        for m in tf.getmembers():
            if m.issym() or m.islnk() or not str((root / m.name).resolve()).startswith(str(root)):
                raise RuntimeError(f"Unsafe path in archive: {m.name}")
        try:
            tf.extractall(root, filter="data")
        except TypeError:   # Python < 3.12 without the filter argument
            tf.extractall(root)


def get_spamassassin() -> None:
    dl, out = RAW_DIR / "_downloads", RAW_DIR / "spamassassin"
    for name in SPAMASSASSIN_FILES:
        marker = out / f".done_{name}"
        if marker.exists():
            print(f"[spamassassin] {name} already extracted")
            continue
        arc = dl / name
        if not arc.exists():
            print(f"[spamassassin] downloading {name} ...")
            download(SPAMASSASSIN_BASE + name, arc)
        safe_extract_tar(arc, out)
        marker.touch()
    print(f"[spamassassin] OK -> {out}")


def _get_zip(label: str, url: str, out_name: str) -> None:
    dl, out = RAW_DIR / "_downloads", RAW_DIR / out_name
    arc = dl / f"{out_name}.zip"
    if not arc.exists():
        print(f"[{label}] downloading ...")
        download(url, arc)
    out.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(arc) as zf:
        zf.extractall(out)
    print(f"[{label}] OK -> {out}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=["spamassassin", "phiusiil", "tranco"])
    a = ap.parse_args()
    jobs = {"spamassassin": get_spamassassin,
            "phiusiil": lambda: _get_zip("phiusiil", PHIUSIIL_URL, "phiusiil"),
            "tranco": lambda: _get_zip("tranco", TRANCO_URL, "tranco")}
    chosen = [a.only] if a.only else ["spamassassin", "phiusiil"]   # tranco is optional
    failed = 0
    for name in chosen:
        try:
            jobs[name]()
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"[{name}] FAILED: {e}\n         -> download manually; see DATASETS.md")
    print(MANUAL)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())