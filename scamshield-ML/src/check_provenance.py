import pandas as pd
import os

folder = "datasets/raw"

source_files = [
    "CEAS_08.csv",
    "Enron.csv",
    "Ling.csv",
    "Nazario.csv",
    "Nigerian_Fraud.csv",
    "SpamAssasin.csv"
]

print("=" * 80)
print("SCAMSHIELD AI - DATASET PROVENANCE CHECK")
print("=" * 80)

# ---------------------------------------------------------
# 1. Check total number of rows in source datasets
# ---------------------------------------------------------

total_rows = 0

print("\nSOURCE DATASET SIZES")
print("-" * 80)

for file in source_files:

    path = os.path.join(folder, file)
    df = pd.read_csv(path)

    rows = len(df)
    total_rows += rows

    print(f"{file:<25} {rows:>10,} rows")

print("-" * 80)
print(f"{'TOTAL':<25} {total_rows:>10,} rows")


# ---------------------------------------------------------
# 2. Check phishing_email.csv
# ---------------------------------------------------------

combined_path = os.path.join(folder, "phishing_email.csv")
combined = pd.read_csv(combined_path)

print("\nCOMBINED DATASET")
print("-" * 80)

print(f"phishing_email.csv        {len(combined):>10,} rows")


# ---------------------------------------------------------
# 3. Compare row counts
# ---------------------------------------------------------

print("\nROW COUNT VERIFICATION")
print("-" * 80)

if total_rows == len(combined):
    print("MATCH ✓")
    print("The source row counts add up exactly to phishing_email.csv.")
else:
    print("NO MATCH ✗")
    print("The row counts do not match.")


# ---------------------------------------------------------
# 4. Compare label totals
# ---------------------------------------------------------

print("\nCOMBINED DATASET LABEL COUNTS")
print("-" * 80)

print(combined["label"].value_counts().sort_index())


# ---------------------------------------------------------
# 5. Calculate expected label totals from sources
# ---------------------------------------------------------

source_label_counts = {0: 0, 1: 0}

for file in source_files:

    path = os.path.join(folder, file)
    df = pd.read_csv(path)

    counts = df["label"].value_counts()

    source_label_counts[0] += counts.get(0, 0)
    source_label_counts[1] += counts.get(1, 0)

print("\nSOURCE DATASETS COMBINED LABEL COUNTS")
print("-" * 80)

print(f"Label 0: {source_label_counts[0]:,}")
print(f"Label 1: {source_label_counts[1]:,}")


# ---------------------------------------------------------
# 6. Compare labels
# ---------------------------------------------------------

print("\nLABEL VERIFICATION")
print("-" * 80)

combined_label_0 = (combined["label"] == 0).sum()
combined_label_1 = (combined["label"] == 1).sum()

if (
    source_label_counts[0] == combined_label_0
    and source_label_counts[1] == combined_label_1
):
    print("MATCH ✓")
    print("Label totals also match exactly.")
else:
    print("NO MATCH ✗")
    print("Label totals are different.")


print("\n" + "=" * 80)
print("PROVENANCE CHECK COMPLETE")
print("=" * 80)