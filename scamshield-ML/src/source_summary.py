import pandas as pd
import os

folder = "datasets/raw"

files = [
    "CEAS_08.csv",
    "Enron.csv",
    "Ling.csv",
    "Nazario.csv",
    "Nigerian_Fraud.csv",
    "phishing_email.csv",
    "SpamAssasin.csv"
]

print("=" * 80)
print("SCAMSHIELD AI - SOURCE DATASET SUMMARY")
print("=" * 80)

for file in files:

    path = os.path.join(folder, file)

    print("\n" + "-" * 80)
    print(f"FILE: {file}")
    print("-" * 80)

    try:
        df = pd.read_csv(path)

        print(f"Rows: {len(df):,}")
        print(f"Columns: {df.columns.tolist()}")

        print("\nMissing values:")
        missing = df.isnull().sum()
        print(missing[missing > 0].to_dict() if missing.sum() > 0 else "None")

        if "label" in df.columns:
            print("\nLabel distribution:")
            print(df["label"].value_counts().to_dict())

        print("\nDuplicate rows:")
        print(df.duplicated().sum())

    except Exception as e:
        print(f"ERROR: {e}")

print("\n" + "=" * 80)
print("SUMMARY COMPLETE")
print("=" * 80)