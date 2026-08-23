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

print("=" * 70)
print("SCAMSHIELD AI - SOURCE DATASET INSPECTION")
print("=" * 70)

for file in files:

    path = os.path.join(folder, file)

    print("\n" + "-" * 70)
    print(f"FILE: {file}")
    print("-" * 70)

    try:
        df = pd.read_csv(path)

        print("Shape:", df.shape)

        print("Columns:")
        print(df.columns.tolist())

        print("\nFirst 3 rows:")
        print(df.head(3).to_string())

        print("\nMissing values:")
        print(df.isnull().sum().to_dict())

    except Exception as e:
        print("ERROR:", e)

print("\n" + "=" * 70)
print("SOURCE INSPECTION COMPLETE")
print("=" * 70)