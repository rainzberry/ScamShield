import pandas as pd
import re
import nltk
import os

from nltk.corpus import stopwords


# =========================================================
# STOPWORDS
# =========================================================

try:
    STOPWORDS = set(stopwords.words("english"))
except LookupError:
    nltk.download("stopwords")
    STOPWORDS = set(stopwords.words("english"))


# =========================================================
# NORMALIZATION
# =========================================================

def normalize_text(text):

    if pd.isna(text):
        text = ""

    text = str(text).lower()

    # Remove HTML
    text = re.sub(r"<[^>]+>", " ", text)

    # Remove URLs
    text = re.sub(r"http\S+|www\S+", " ", text)

    # Remove punctuation
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Remove stopwords
    words = text.split()

    words = [
        word for word in words
        if word not in STOPWORDS
    ]

    return " ".join(words)


# =========================================================
# LOAD COMBINED DATASET
# =========================================================

folder = "datasets/raw"

combined = pd.read_csv(
    os.path.join(folder, "phishing_email.csv")
)

combined_text = combined["text_combined"].fillna("").astype(str)


# =========================================================
# SOURCE FILES
# =========================================================

source_files = [
    "CEAS_08.csv",
    "Enron.csv",
    "Ling.csv",
    "Nazario.csv",
    "Nigerian_Fraud.csv",
    "SpamAssasin.csv"
]


print("=" * 80)
print("SCAMSHIELD AI - SOURCE POSITION SEARCH")
print("=" * 80)


# =========================================================
# SEARCH EACH SOURCE
# =========================================================

for filename in source_files:

    print("\n" + "-" * 80)
    print(f"FILE: {filename}")
    print("-" * 80)

    path = os.path.join(folder, filename)

    df = pd.read_csv(path)

    # Build source text
    source_text = (
        df["subject"].fillna("").astype(str)
        + " "
        + df["body"].fillna("").astype(str)
    )

    # Select 5 rows spread across dataset
    sample_indices = [
        0,
        len(df) // 4,
        len(df) // 2,
        (3 * len(df)) // 4,
        len(df) - 1
    ]

    for source_index in sample_indices:

        normalized = normalize_text(
            source_text.iloc[source_index]
        )

        # Find exact occurrence in combined dataset
        matches = combined_text[
            combined_text == normalized
        ]

        print(
            f"\nSource row {source_index}:",
            end=" "
        )

        if len(matches) > 0:

            positions = matches.index.tolist()

            print("MATCH ✓")

            print(
                "Combined position(s):",
                positions[:10]
            )

        else:

            print("NO MATCH")


print("\n" + "=" * 80)
print("SOURCE POSITION SEARCH COMPLETE")
print("=" * 80)