import pandas as pd
import re


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
    text = re.sub(r"\s+", " ", text)

    return text.strip()


print("=" * 80)
print("SCAMSHIELD AI - COMBINED ROW MATCH TEST")
print("=" * 80)


# --------------------------------------------------
# Load datasets
# --------------------------------------------------

combined = pd.read_csv("datasets/raw/phishing_email.csv")

enron = pd.read_csv("datasets/raw/Enron.csv")


# --------------------------------------------------
# Normalize Enron subject + body
# --------------------------------------------------

enron_text = (
    enron["subject"].fillna("").astype(str)
    + " "
    + enron["body"].fillna("").astype(str)
)

enron_normalized = enron_text.apply(normalize_text)


# --------------------------------------------------
# Take first few combined emails
# --------------------------------------------------

print("\nChecking first 10 emails from phishing_email.csv...")
print("-" * 80)

for i in range(10):

    target = combined.loc[i, "text_combined"]

    matches = enron_normalized[
        enron_normalized == target
    ]

    print(f"\nCombined row {i}")
    print("Text:", target[:150])

    if len(matches) > 0:
        print("MATCH FOUND ✓")
        print("Matching Enron row:", matches.index.tolist()[:5])
    else:
        print("NO EXACT MATCH")


print("\n" + "=" * 80)
print("MATCH TEST COMPLETE")
print("=" * 80)