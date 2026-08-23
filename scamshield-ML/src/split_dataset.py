import pandas as pd
from sklearn.model_selection import train_test_split
from pathlib import Path


# ============================================================
# SCAMSHIELD AI - DATASET SPLITTING
# ============================================================

print("=" * 80)
print("SCAMSHIELD AI - DATASET SPLITTING")
print("=" * 80)


# ------------------------------------------------------------
# 1. PATHS
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "datasets" / "processed" / "clean_emails.csv"

TRAIN_FILE = BASE_DIR / "datasets" / "processed" / "train.csv"
TEST_FILE = BASE_DIR / "datasets" / "processed" / "test.csv"


# ------------------------------------------------------------
# 2. LOAD CLEANED DATASET
# ------------------------------------------------------------

print("\n1. LOADING CLEANED DATASET")

df = pd.read_csv(INPUT_FILE)

print(f"Rows: {len(df)}")
print(f"Columns: {list(df.columns)}")


# ------------------------------------------------------------
# 3. VALIDATE REQUIRED COLUMNS
# ------------------------------------------------------------

required_columns = ["text", "label", "source"]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )


# ------------------------------------------------------------
# 4. ORIGINAL LABEL DISTRIBUTION
# ------------------------------------------------------------

print("\n2. ORIGINAL LABEL DISTRIBUTION")

print(df["label"].value_counts().sort_index())

print("\nOriginal label percentages:")

print(
    (df["label"].value_counts(normalize=True).sort_index() * 100)
    .round(2)
)


# ------------------------------------------------------------
# 5. TRAIN / TEST SPLIT
# ------------------------------------------------------------

print("\n3. SPLITTING DATASET")

# 80% Training
# 20% Testing
#
# Stratification maintains approximately the same
# spam/legitimate ratio in both datasets.

train_df, test_df = train_test_split(
    df,
    test_size=0.20,
    random_state=42,
    stratify=df["label"]
)


# ------------------------------------------------------------
# 6. RESET INDEX
# ------------------------------------------------------------

train_df = train_df.reset_index(drop=True)
test_df = test_df.reset_index(drop=True)


# ------------------------------------------------------------
# 7. TRAINING SET
# ------------------------------------------------------------

print("\n4. TRAINING SET")

print(f"Rows: {len(train_df)}")

print("\nLabel distribution:")
print(train_df["label"].value_counts().sort_index())

print("\nLabel percentages:")
print(
    (train_df["label"].value_counts(normalize=True).sort_index() * 100)
    .round(2)
)


# ------------------------------------------------------------
# 8. TESTING SET
# ------------------------------------------------------------

print("\n5. TESTING SET")

print(f"Rows: {len(test_df)}")

print("\nLabel distribution:")
print(test_df["label"].value_counts().sort_index())

print("\nLabel percentages:")
print(
    (test_df["label"].value_counts(normalize=True).sort_index() * 100)
    .round(2)
)


# ------------------------------------------------------------
# 9. VERIFY SPLIT
# ------------------------------------------------------------

print("\n6. SPLIT VERIFICATION")

total_rows = len(train_df) + len(test_df)

print(f"Original rows : {len(df)}")
print(f"Train rows    : {len(train_df)}")
print(f"Test rows     : {len(test_df)}")
print(f"Total         : {total_rows}")

if total_rows == len(df):
    print("Row count verification: PASSED")
else:
    print("Row count verification: FAILED")


# ------------------------------------------------------------
# 10. SAVE DATASETS
# ------------------------------------------------------------

print("\n7. SAVING DATASETS")

TRAIN_FILE.parent.mkdir(parents=True, exist_ok=True)

train_df.to_csv(TRAIN_FILE, index=False)
test_df.to_csv(TEST_FILE, index=False)

print(f"Training dataset saved to: {TRAIN_FILE}")
print(f"Testing dataset saved to : {TEST_FILE}")


# ------------------------------------------------------------
# 11. COMPLETE
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("DATASET SPLIT COMPLETE")
print("=" * 80)