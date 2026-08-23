import pandas as pd
import re
import nltk

from nltk.corpus import stopwords

# Download stopwords if necessary
try:
    STOPWORDS = set(stopwords.words("english"))
except LookupError:
    nltk.download("stopwords")
    STOPWORDS = set(stopwords.words("english"))


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

    # Remove English stopwords
    words = text.split()

    words = [
        word for word in words
        if word not in STOPWORDS
    ]

    return " ".join(words)


print("=" * 80)
print("SCAMSHIELD AI - STOPWORD MATCH TEST")
print("=" * 80)


combined = pd.read_csv(
    "datasets/raw/phishing_email.csv"
)

enron = pd.read_csv(
    "datasets/raw/Enron.csv"
)


# Create source text
enron_text = (
    enron["subject"].fillna("").astype(str)
    + " "
    + enron["body"].fillna("").astype(str)
)


# Normalize source
enron_normalized = enron_text.apply(normalize_text)


print("\nChecking first 10 combined emails...")
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
        print(
            "Matching Enron rows:",
            matches.index.tolist()[:5]
        )
    else:
        print("NO EXACT MATCH")


print("\n" + "=" * 80)
print("STOPWORD MATCH TEST COMPLETE")
print("=" * 80)