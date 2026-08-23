import pandas as pd
import os
import re
import nltk

from nltk.corpus import stopwords


# =========================================================
# SETTINGS
# =========================================================

RAW_DIR = "datasets/raw"
PROCESSED_DIR = "datasets/processed"

os.makedirs(PROCESSED_DIR, exist_ok=True)


# =========================================================
# STOPWORDS
# =========================================================

try:
    STOPWORDS = set(stopwords.words("english"))
except LookupError:
    nltk.download("stopwords")
    STOPWORDS = set(stopwords.words("english"))


# =========================================================
# TEXT CLEANING FUNCTION
# =========================================================

def clean_text(text):

    if pd.isna(text):
        return ""

    text = str(text)

    # Convert to lowercase
    text = text.lower()

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)

    # Remove URLs
    text = re.sub(
        r"http\S+|www\S+",
        " ",
        text
    )

    # Remove email addresses
    text = re.sub(
        r"\S+@\S+",
        " ",
        text
    )

    # Keep only letters and numbers
    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    # Normalize whitespace
    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    # Remove English stopwords
    words = text.split()

    words = [
        word
        for word in words
        if word not in STOPWORDS
    ]

    return " ".join(words)


# =========================================================
# LOAD SOURCE DATASETS
# =========================================================

files = [
    "CEAS_08.csv",
    "Enron.csv",
    "Ling.csv",
    "Nazario.csv",
    "Nigerian_Fraud.csv",
    "SpamAssasin.csv"
]


all_data = []


print("=" * 80)
print("SCAMSHIELD AI - DATA CLEANING")
print("=" * 80)


# =========================================================
# PROCESS EACH DATASET
# =========================================================

for filename in files:

    print(f"\nProcessing: {filename}")

    path = os.path.join(
        RAW_DIR,
        filename
    )

    df = pd.read_csv(path)

    # -----------------------------------------------------
    # Handle missing subject/body
    # -----------------------------------------------------

    if "subject" not in df.columns:
        df["subject"] = ""

    if "body" not in df.columns:
        df["body"] = ""

    df["subject"] = df["subject"].fillna("")
    df["body"] = df["body"].fillna("")


    # -----------------------------------------------------
    # Combine subject + body
    # -----------------------------------------------------

    df["text"] = (
        df["subject"].astype(str)
        + " "
        + df["body"].astype(str)
    )


    # -----------------------------------------------------
    # Clean text
    # -----------------------------------------------------

    df["text"] = df["text"].apply(clean_text)


    # -----------------------------------------------------
    # Keep only required columns
    # -----------------------------------------------------

    df = df[
        ["text", "label"]
    ].copy()


    # -----------------------------------------------------
    # Add source information
    # -----------------------------------------------------

    df["source"] = filename.replace(
        ".csv",
        ""
    )


    all_data.append(df)


    print(
        f"Rows processed: {len(df):,}"
    )


# =========================================================
# COMBINE DATASETS
# =========================================================

combined = pd.concat(
    all_data,
    ignore_index=True
)


print("\n" + "=" * 80)
print("COMBINED DATASET")
print("=" * 80)

print(
    "Rows:",
    len(combined)
)

print(
    "Columns:",
    combined.columns.tolist()
)


# =========================================================
# REMOVE EMPTY EMAILS
# =========================================================

before_empty = len(combined)

combined = combined[
    combined["text"].str.strip() != ""
].copy()

removed_empty = (
    before_empty - len(combined)
)

print(
    "\nEmpty emails removed:",
    removed_empty
)


# =========================================================
# HANDLE EXTREMELY LONG EMAILS
# =========================================================

MAX_LENGTH = 20000

# Calculate text length BEFORE checking for long emails
combined["text_length"] = combined["text"].str.len()

# Count emails exceeding the limit
long_emails = (
    combined["text_length"] > MAX_LENGTH
).sum()

# Truncate long emails instead of deleting them
combined["text"] = combined["text"].str.slice(
    0,
    MAX_LENGTH
)

# Recalculate length after truncation
combined["text_length"] = combined["text"].str.len()

print(
    "Extremely long emails truncated:",
    long_emails
)


# =========================================================
# REMOVE EXACT DUPLICATES
# =========================================================

before_duplicates = len(combined)

combined = combined.drop_duplicates(
    subset=["text", "label"]
)

removed_duplicates = (
    before_duplicates - len(combined)
)

print(
    "Duplicate emails removed:",
    removed_duplicates
)


# =========================================================
# LABEL VALIDATION
# =========================================================

print("\nLabel distribution:")

print(
    combined["label"].value_counts()
)


print("\nUnique labels:")

print(
    sorted(combined["label"].unique())
)


# =========================================================
# SOURCE DISTRIBUTION
# =========================================================

print("\nSource distribution:")

print(
    combined["source"].value_counts()
)


# =========================================================
# FINAL CLEANUP
# =========================================================

combined = combined[
    ["text", "label", "source"]
]


# =========================================================
# SAVE
# =========================================================

output_path = os.path.join(
    PROCESSED_DIR,
    "clean_emails.csv"
)

combined.to_csv(
    output_path,
    index=False
)


print("\n" + "=" * 80)
print("CLEANING COMPLETE")
print("=" * 80)

print(
    f"Final dataset: {len(combined):,} emails"
)

print(
    f"Saved to: {output_path}"
)