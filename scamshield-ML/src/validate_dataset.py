import pandas as pd
import os


# =========================================================
# SETTINGS
# =========================================================

DATA_PATH = "datasets/processed/clean_emails.csv"


# =========================================================
# LOAD DATA
# =========================================================

df = pd.read_csv(DATA_PATH)


print("=" * 80)
print("SCAMSHIELD AI - CLEAN DATASET VALIDATION")
print("=" * 80)


# =========================================================
# 1. DATASET SHAPE
# =========================================================

print("\n1. DATASET SHAPE")
print(df.shape)


# =========================================================
# 2. COLUMNS
# =========================================================

print("\n2. COLUMNS")
print(df.columns.tolist())


# =========================================================
# 3. MISSING VALUES
# =========================================================

print("\n3. MISSING VALUES")

print(
    df.isnull().sum()
)


# =========================================================
# 4. EMPTY TEXT
# =========================================================

print("\n4. EMPTY TEXT")

empty_text = (
    df["text"]
    .fillna("")
    .str.strip()
    .eq("")
    .sum()
)

print(
    "Empty emails:",
    empty_text
)


# =========================================================
# 5. DUPLICATE ROWS
# =========================================================

print("\n5. DUPLICATE ROWS")

print(
    "Duplicate rows:",
    df.duplicated().sum()
)


# =========================================================
# 6. DUPLICATE TEXT
# =========================================================

print("\n6. DUPLICATE TEXT")

duplicate_text = (
    df["text"]
    .duplicated()
    .sum()
)

print(
    "Duplicate text entries:",
    duplicate_text
)


# =========================================================
# 7. LABEL VALIDATION
# =========================================================

print("\n7. LABEL VALIDATION")

print(
    "Unique labels:",
    sorted(df["label"].unique())
)

invalid_labels = ~df["label"].isin([0, 1])

print(
    "Invalid labels:",
    invalid_labels.sum()
)


# =========================================================
# 8. LABEL DISTRIBUTION
# =========================================================

print("\n8. LABEL DISTRIBUTION")

print(
    df["label"].value_counts()
)


print("\nLabel percentages:")

print(
    df["label"].value_counts(
        normalize=True
    ) * 100
)


# =========================================================
# 9. TEXT LENGTH
# =========================================================

print("\n9. TEXT LENGTH")

df["text_length"] = (
    df["text"].str.len()
)

print(
    df["text_length"].describe()
)


# =========================================================
# 10. TEXT LENGTH LIMIT
# =========================================================

print("\n10. TEXT LENGTH CHECK")

print(
    "Emails > 20,000 characters:",
    (df["text_length"] > 20000).sum()
)

print(
    "Maximum length:",
    df["text_length"].max()
)


# =========================================================
# 11. SOURCE DISTRIBUTION
# =========================================================

print("\n11. SOURCE DISTRIBUTION")

print(
    df["source"].value_counts()
)


# =========================================================
# 12. SOURCE × LABEL
# =========================================================

print("\n12. SOURCE × LABEL DISTRIBUTION")

source_label = pd.crosstab(
    df["source"],
    df["label"]
)

print(
    source_label
)


# =========================================================
# 13. SOURCE LABEL PERCENTAGES
# =========================================================

print("\n13. SOURCE LABEL PERCENTAGES")

source_percentages = pd.crosstab(
    df["source"],
    df["label"],
    normalize="index"
) * 100

print(
    source_percentages.round(2)
)


# =========================================================
# 14. SAMPLE EMAILS
# =========================================================

print("\n14. SAMPLE EMAILS")

for i, row in df.head(5).iterrows():

    print("\n----------------------------------------")

    print(
        "Source:",
        row["source"]
    )

    print(
        "Label:",
        row["label"]
    )

    print(
        "Text:",
        row["text"][:300]
    )


# =========================================================
# COMPLETE
# =========================================================

print("\n" + "=" * 80)
print("VALIDATION COMPLETE")
print("=" * 80)