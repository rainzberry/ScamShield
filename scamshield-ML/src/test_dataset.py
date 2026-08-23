import pandas as pd

file_path = "D:/VIT/FALL SEMESTER 2026-2027/Software Engineering/Project/scamshield-ML/datasets/raw/phishing_email.csv"

df = pd.read_csv(file_path)

print("Dataset loaded successfully!")
print("\nShape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head())

print("\nLabel distribution:")
print(df["label"].value_counts())