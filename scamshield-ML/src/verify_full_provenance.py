import pandas as pd
import re
import os
import nltk

from nltk.corpus import stopwords


# ---------------------------------------------------------
# Stopwords
# ---------------------------------------------------------

try:
    STOPWORDS = set(stopwords.words("english"))
except LookupError:
    nltk.download("stopwords")
    STOPWORDS = set(stopwords.words("english"))


# ---------------------------------------------------------
# Text normalization
# ---------------------------------------------------------

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

    # Normalize spaces
    text = re.sub(r"\s+", " ", text)

    # Remove stopwords
    words = text.split()

    words = [
        word
        for word in words
        if word not in STOPWORDS
    ]

    return " ".join(words)


# ---------------------------------------------------------
# Dataset information
# ---------------------------------------------------------

folder = "datasets/raw"

source_files = [
    "CEAS_08.csv",
    "Enron.csv",
    "Ling.csv",
    "Nazario.csv",
    "Nigerian_Fraud.csv",
    "SpamAssasin.csv"
]

combined = pd.read_csv(
    os.path.join(folder, "phishing_email.csv")
)


print("=" * 80)
print("SCAMSHIELD AI - FULL DATASET PROVENANCE VERIFICATION")
print("=" * 80)


# ---------------------------------------------------------
# Track combined dataset position
# ---------------------------------------------------------

start_index = 0

total_matches = 0
total_rows = 0


for file in source_files:

    print("\n" + "-" * 80)
    print(f"CHECKING: {file}")
    print("-" * 80)

    path = os.path.join(folder, file)

    df = pd.read_csv(path)

    rows = len(df)

    # Create source text
    source_text = (
        df["subject"].fillna("").astype(str)
        + " "
        + df["body"].fillna("").astype(str)
    )

    # Normalize
    normalized_source = source_text.apply(normalize_text)

    # Corresponding section in combined dataset
    end_index = start_index + rows

    combined_section = combined.iloc[
        start_index:end_index
    ]["text_combined"].reset_index(drop=True)

    normalized_source = normalized_source.reset_index(drop=True)

    # Compare
    matches = normalized_source == combined_section

    matched = matches.sum()

    percentage = (matched / rows) * 100

    print(f"Source rows:       {rows:,}")
    print(f"Expected range:    {start_index:,} - {end_index - 1:,}")
    print(f"Exact matches:     {matched:,}")
    print(f"Match percentage:  {percentage:.2f}%")

    if matched == rows:
        print("STATUS: ✓ COMPLETE MATCH")
    else:
        print("STATUS: ⚠ PARTIAL MATCH")

    total_matches += matched
    total_rows += rows

    start_index = end_index


# ---------------------------------------------------------
# Overall result
# ---------------------------------------------------------

overall_percentage = (
    total_matches / total_rows
) * 100


print("\n" + "=" * 80)
print("OVERALL PROVENANCE RESULT")
print("=" * 80)

print(f"Total source rows:  {total_rows:,}")
print(f"Total exact matches: {total_matches:,}")
print(f"Overall match rate: {overall_percentage:.2f}%")

if total_matches == total_rows:
    print("\n✓ COMPLETE PROVENANCE MATCH")
    print("Every source row matches the corresponding")
    print("processed row in phishing_email.csv.")

else:
    print("\n⚠ PARTIAL PROVENANCE MATCH")
    print("Some rows do not match exactly.")

print("\n" + "=" * 80)
print("PROVENANCE VERIFICATION COMPLETE")
print("=" * 80)